"""
sectors.py
==========

Models for standard sectors.


Copyright 2016 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from sfc_models.models import Sector, FinancialAssetMarket, Market
import sfc_models.utils as utils


class BaseHousehold(Sector):
    """
    Base class for all household sectors
    """
    def __init__(self, country, long_name, code, alpha_income, alpha_fin):
        Sector.__init__(self, country, long_name, code)
        self.AlphaIncome = alpha_income
        self.AlphaFin = alpha_fin
        self.AddVariable('AlphaIncome', 'Parameter for consumption out of income', '%0.4f' % (self.AlphaIncome,))
        self.AddVariable('AlphaFin', 'Parameter for consumption out of financial assets', '%0.4f' % (self.AlphaFin,))
        self.AddVariable('DEM_GOOD', 'Expenditure on goods consumption', 'AlphaIncome * AfterTax + AlphaFin * LAG_F')
        self.AddVariable('PreTax', 'Pretax income', 'SET IN DERIVED CLASSES')
        self.AddVariable('AfterTax', 'Aftertax income', 'PreTax - T')
        self.AddVariable('T', 'Taxes paid.', '')


class Household(BaseHousehold):
    def __init__(self, country, long_name, code, alpha_income, alpha_fin):
        BaseHousehold.__init__(self, country, long_name, code, alpha_income, alpha_fin)
        self.AddVariable('SUP_LAB', 'Supply of Labour', '<To be determined>')
        self.Equations['PreTax'] = 'SUP_LAB'


class Capitalists(BaseHousehold):
    def __init__(self, country, long_name, code, alpha_income, alpha_fin):
        BaseHousehold.__init__(self, country, long_name, code, alpha_income, alpha_fin)
        self.AddVariable('DIV', 'Dividends', '')
        self.Equations['PreTax'] = 'DIV'


class DoNothingGovernment(Sector):
    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')
        self.AddVariable('FISC_BAL', 'Government Primary Fiscal Balance (Need to fix)', 'T - DEM_GOOD')


class Treasury(Sector):
    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')
        self.AddVariable('PRIM_BAL', 'Government Primary Fiscal Balance', 'T - DEM_GOOD')
        # Treasury has no money holdings
        self.AddVariable('DEM_MON', 'Demand for Money', '0.0')


class CentralBank(Sector):
    def __init__(self, country, long_name, code, treasury):
        Sector.__init__(self, country, long_name, code)
        self.Treasury = treasury
        # Demand for deposits = F + Supply of money (Central bank net worth plus money supply)
        self.AddVariable('DEM_DEP', 'Demand for deposits', 'F + SUP_MON')

    def GenerateEquations(self):
        self.AddCashFlow('-CBDIV', 'INTDEP', 'Dividends paid to Treasury')
        self.Treasury.AddCashFlow('CBDIV', self.GetVariableName('CBDIV'), 'Dividends paid by the central bank')



class FixedMarginBusiness(Sector):
    def __init__(self, country, long_name, code, profit_margin=0.0):
        Sector.__init__(self, country, long_name, code)
        self.ProfitMargin = profit_margin
        self.AddVariable('SUP_GOOD', 'Supply of goods', '<TO BE DETERMINED>')
        self.AddVariable('PROF', 'Profits', 'SUP_GOOD - DEM_LAB')


    def GenerateEquations(self):
        wage_share = 1.0 - self.ProfitMargin
        market_sup_good = self.Parent.LookupSector('GOOD').GetVariableName('SUP_GOOD')
        if self.ProfitMargin == 0:
            self.AddVariable('DEM_LAB', 'Demand for labour', market_sup_good)
            self.Equations['PROF'] = ''
        else:
            self.AddVariable('DEM_LAB', 'Demand for labour', '%0.3f * %s' % (wage_share, market_sup_good))
            self.Equations['PROF'] = '%0.3f * %s' % (self.ProfitMargin, market_sup_good)
        for s in self.Parent.SectorList:
            if 'DIV' in s.Equations:
                self.AddCashFlow('-DIV', 'PROF', 'Dividends paid')
                s.AddCashFlow('DIV', self.GetVariableName('PROF'), 'Dividends received')
                break


class TaxFlow(Sector):
    """
    TaxFlow: Not really a sector, but keep it in the same list

    Uses the TaxRate of this object, or the TaxRate of the sector (if it is defined).
    """

    def __init__(self, country, long_name, code, taxrate, taxes_paid_to='GOV'):
        Sector.__init__(self, country, long_name, code, has_F=False)
        self.AddVariable('TaxRate', 'Tax rate', '%0.4f' % (taxrate,))
        self.AddVariable('T', 'Taxes Paid', '<To be determined>')
        self.TaxingSector = taxes_paid_to

    def GenerateEquations(self):
        terms = []
        # Find all sector that are taxable
        taxrate_name = self.GetVariableName('TaxRate')
        for s in self.Parent.SectorList:
            if s.ID == self.ID:
                continue
            if 'PreTax' in s.Equations:
                # If the sector has a tax rate defined for it, use that tax rate instead of this object's rate.
                # Need to add support for fdiffering rates for each type of income?
                if 'TaxRate' in s.Equations:
                    tax_name_used = s.GetVariableName('TaxRate')
                else:
                    tax_name_used = taxrate_name
                term = '%s * %s' % (tax_name_used, s.GetVariableName('PreTax'))
                s.AddCashFlow('-T', term, 'Taxes paid.')
                terms.append('+' + term)
        self.Equations['T'] = utils.create_equation_from_terms(terms)
        # work on other sectors
        tax_fullname = self.GetVariableName('T')
        gov = self.Parent.LookupSector(self.TaxingSector)
        gov.AddCashFlow('T', tax_fullname, 'Tax revenue received.')


class MoneyMarket(FinancialAssetMarket):
    """
    The class that handles "money" within the model. The assumption is that the rate of interest is zero, and so this
    is really government money (currency). It probably should be labelled "currency," but that might be confusing.

    (Note from Brian R: The name of this class is painful, as I am currently finishing off "Abolish Money (From
    Economics)!", but this is meant to be an open source project, and ease of use trumps my analytical biases.

    In order to transition cleanly simpler models that do not specify financial markets, the default behaviour is to
    emulate the behaviour of a model without any FinancialAssetMarket classes created. This is done by creating a
    default "demand for money" equation in each sector that is:
            DEM_{MONEY} = F,
    that is, money holdings at time t = financial asset holdings at time t. (The supplier, by default = 'GOV', just
    has a open-ended supply, like other markets.)

    Note that since SUP and DEM are always realised (for now), the money stock is equal to the supply by the issuer.
    """

    def __init__(self, country, long_name='Money', code='MON', issuer_short_code='GOV'):
        FinancialAssetMarket.__init__(self, country, long_name, code, issuer_short_code)

    def GenerateEquations(self):
        """
        Generate equation.
         :return: None
        """
        country = self.Parent
        dem_name = 'DEM_' + self.Code
        dem_terms = []
        for s in country.SectorList:
            if not s.HasF:
                continue
            if s.Code == self.IssuerShortCode:
                s.AddVariable('SUP_' + self.Code, 'Supply of ' + self.LongName, self.GetVariableName(dem_name))
                self.AddVariable('SUP_' + self.Code, 'Supply of ' + self.LongName,
                                 s.GetVariableName('SUP_' + self.Code))
                continue
            try:
                term = s.GetVariableName(dem_name)
                dem_terms.append(term)
                continue
            except KeyError:
                pass
            s.AddVariable(dem_name, 'Demand for ' + self.LongName, s.GetVariableName('F'))
            dem_terms.append(s.GetVariableName(dem_name))
        self.AddVariable(dem_name,'Total demand for ' + self.LongName, utils.create_equation_from_terms(dem_terms))

class DepositMarket(FinancialAssetMarket):
    """
    An interest-bearing deposit. This will act as a stand-in for Treasury bills for now. The price is fixed at 1,
    and pays interest based on the lagged interest rate and lagged holdings.

    Interest rate convention: 0.01 = 1% interest. The variable name is 'r'; defaults to 0%. In simpler models, will be
    an exogenous variable.

    Assumed to be a single issuer; the supply equation is filled in automatically (always meets demand).

    Unlike MoneyMarket, no demand is filled in. In order to use this market, need to set up a demand variable in one
    sector (at least).

    This class will automatically create interest income variables and cash flows in affected sectors.

    Note that since SUP and DEM are always realised (for now), the amount oustanding is equal to the supply by the
    issuer.
    """

    def __init__(self, country, long_name='Deposit', code='DEP', issuer_short_code='GOV'):
        FinancialAssetMarket.__init__(self, country, long_name, code, issuer_short_code)
        self.AddVariable('r', 'Interest rate', '0.')
        self.AddVariable('LAG_r', 'Lagged Interest rate', 'r(k-1)')

    def GenerateEquations(self):
        """
        Generate equations.
 
        :return: None
        """
        country = self.Parent
        dem_terms = []
        dem_name = 'DEM_' + self.Code
        for s in country.SectorList:
            if isinstance(s, Market):
                continue
            if s.Code == self.IssuerShortCode:
                sup_name = 'SUP_' + self.Code
                s.AddVariable(sup_name, 'Supply of ' + self.LongName, self.GetVariableName('DEM_' + self.Code))
                s.AddVariable('LAG_' + sup_name, 'Lagged Supply of ' + self.LongName, s.GetVariableName(sup_name) + '(k-1)')
                s.AddCashFlow('-INT' + self.Code,
                              '{0}*{1}'.format(self.GetVariableName('LAG_r'), s.GetVariableName('LAG_' + sup_name)),
                              'Interest paid on ' + self.LongName)
                self.AddVariable('SUP_' + self.Code, 'Supply of ' + self.LongName,
                                 s.GetVariableName('SUP_' + self.Code))
                continue
            dem_name = 'DEM_' + self.Code
            try:
                term = s.GetVariableName(dem_name)
            except KeyError:
                continue
            s.AddVariable('LAG_' + dem_name, 'Lagged demand for ' + self.LongName, s.GetVariableName(dem_name)+'(k-1)')
            s.AddCashFlow('+INT' + self.Code,
                          '{0}*{1}'.format(self.GetVariableName('LAG_r'), s.GetVariableName('LAG_' + dem_name)),
                          'Interest received on ' + self.LongName)
            dem_terms.append(s.GetVariableName(dem_name))
        self.AddVariable(dem_name, 'Total demand for ' + self.LongName, utils.create_equation_from_terms(dem_terms))



