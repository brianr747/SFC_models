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
from sfc_models.sector import Sector, Market, FinancialAssetMarket
from sfc_models.utils import Logger
import sfc_models.utils as utils
from sfc_models.utils import LogicError


class BaseHousehold(Sector):
    """
    Base class for all household sectors
    """

    def __init__(self, country, code, long_name='', alpha_income=.6, alpha_fin=.4,
                 consumption_good_name='GOOD'):
        """
        Describes SFC model typical household sector. Subclasses are need to specify
        income source.

        :param country: Country
        :param long_name: str
        :param code: str
        """
        if long_name == '':
            long_name = 'Household {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self, country, code, long_name=long_name, has_F=True)
        self.AlphaIncome = alpha_income
        self.AlphaFin = alpha_fin
        self.IsTaxable = True
        self.GetModel().AddCashFlowIncomeExclusion(self, 'DEM_' + consumption_good_name)
        self.AddVariable('AlphaIncome', 'Parameter for consumption out of income', '%0.4f' % (self.AlphaIncome,))
        self.AddVariable('AlphaFin', 'Parameter for consumption out of financial assets', '%0.4f' % (self.AlphaFin,))
        self.AddVariable('DEM_' + consumption_good_name, 'Expenditure on goods consumption',
                         'AlphaIncome * AfterTax + AlphaFin * LAG_F')
        # self.AddVariable('PreTax', 'Pretax income', 'SET IN DERIVED CLASSES')
        self.AddVariable('AfterTax', 'Aftertax income', 'INC - T')
        self.AddVariable('T', 'Taxes paid.', '')

    def _GenerateEquations(self):
        """
        Overwrites the Alpha variables, in case the user sets them before _GenerateEquations
        is called.
        :return:
        """
        self.SetEquationRightHandSide('AlphaIncome',  '%0.4f' % (self.AlphaIncome,))
        self.SetEquationRightHandSide('AlphaFin', '%0.4f' % (self.AlphaFin,))


class Household(BaseHousehold):
    def __init__(self, country, code, long_name='', alpha_income=.6, alpha_fin=.4,
                 consumption_good_name='GOOD', labour_name='LAB'):
        """
        Typical household sector, that consumes one good ('GOOD' by default) and
        provides labour ('LAB' by default).

        :param country: Country
        :param long_name: str
        :param code: str
        """
        BaseHousehold.__init__(self, country, code, long_name, alpha_income=alpha_income,
                               alpha_fin=alpha_fin, consumption_good_name=consumption_good_name)
        self.AddVariable('SUP_' + labour_name, 'Supply of Labour', '0.')
        # self.SetEquationRightHandSide('PreTax', 'SUP_' + labour_name)

    def _GenerateEquations(self):
        """
        Call Base to reset alpha variables
        :return:
        """
        BaseHousehold._GenerateEquations(self)


class HouseholdWithExpectations(Household):
    """
    Household sector where consumption is based on expected income.

    The default functionality is that the expected after tax income equals the previous value
    of realised after tax income.
    """

    def __init__(self, country, code, long_name='', alpha_income=.7, alpha_fin=.3,
                 consumption_good_name='GOOD', labour_name='LAB'):
        Household.__init__(self, country, code, long_name=long_name, alpha_income=alpha_income,
                           alpha_fin=alpha_fin, consumption_good_name=consumption_good_name)
        self.SetEquationRightHandSide('DEM_GOOD',
                                      'AlphaIncome * EXP_AfterTax + AlphaFin * LAG_F')
        self.AddVariable('LAG_AfterTax', 'Lagged Aftertax income', 'AfterTax(k-1)')
        self.AddVariable('EXP_AfterTax', 'Expected Aftertax income', 'LAG_AfterTax')

    def _GenerateEquations(self):
        """
        Call base class to reset the Alpha variables.
        :return:
        """
        BaseHousehold._GenerateEquations(self)


class Capitalists(BaseHousehold):
    def __init__(self, country, code, long_name='', alpha_income=.7, alpha_fin=.3,
                 consumption_good_name='GOOD'):
        BaseHousehold.__init__(self, country, code, long_name=long_name, alpha_fin=alpha_fin,
                               alpha_income=alpha_income,
                               consumption_good_name=consumption_good_name)
        self.AddVariable('DIV', 'Dividends', '')
        # self.SetEquationRightHandSide('PreTax', 'DIV')

    def _GenerateEquations(self):
        BaseHousehold._GenerateEquations(self)


class DoNothingGovernment(Sector):
    """
    Consolidated government sector. Use this if you do not want to have to deal with
    financial asset holdings.
    """
    def __init__(self, country, code, long_name=''):
        if long_name == '':
            long_name = 'Government {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self, country, code, long_name)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')
        self.AddVariable('PRIM_BAL', 'Government Primary Fiscal Balance', 'T - DEM_GOOD')
        self.AddVariable('FISC_BAL', 'Government Fiscal Balance', 'INC')

        #self.AddVariable('T', 'Government Taxes', '0.')


class Treasury(Sector):
    def __init__(self, country, code, long_name=''):
        if long_name == '':
            long_name = 'Treasury {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self, country, code, long_name)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')
        self.AddVariable('PRIM_BAL', 'Government Primary Fiscal Balance', 'T - DEM_GOOD')
        # Treasury has no money holdings
        self.AddVariable('DEM_MON', 'Demand for Money', '0.0')


class CentralBank(Sector):
    def __init__(self, country, code, long_name='', treasury=None):
        if long_name == '':
            long_name = 'Central Bank {0} in Country {1}'.format(code, Country.Code)
        Sector.__init__(self, country, code, long_name, has_F=True)
        self.Treasury = treasury
        # Demand for deposits = F + Supply of money (Central bank net worth plus money supply)
        self.AddVariable('DEM_DEP', 'Demand for deposits', 'F + SUP_MON')

    def _GenerateEquations(self):
        self.GetModel().RegisterCashFlow(self, self.Treasury, 'INTDEP')
        # self.AddCashFlow('-CBDIV', 'INTDEP', 'Dividends paid to Treasury')
        # self.Treasury.AddCashFlow('CBDIV', self.GetVariableName('CBDIV'), 'Dividends paid by the central bank')


class FixedMarginBusiness(Sector):
    def __init__(self, country, code, long_name='', profit_margin=0.0, labour_input_name='LAB',
                 output_name='GOOD'):
        if long_name == '':
            long_name = 'Business {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self,country, code, long_name, has_F=True)
        self.ProfitMargin = profit_margin
        self.LabourInputName = labour_input_name
        self.OutputName = output_name
        self.AddVariable('SUP_' + output_name, 'Supply of goods', '')
        self.AddVariable('PROF', 'Profits', 'SUP_GOOD - DEM_' + labour_input_name)

    def _GenerateEquations(self):
        # self.AddVariable('SUP_GOOD', 'Supply of goods', '<TO BE DETERMINED>')
        wage_share = 1.0 - self.ProfitMargin
        Logger('Searching for Market Sector with Code {0} in parent country', priority=4,
               data_to_format=(self.OutputName,))
        try:
            market_sup_good = self.Parent.LookupSector(self.OutputName).GetVariableName('SUP_' + self.OutputName)
        except KeyError:
            raise Warning('Business {0} Cannot Find Market for {1}'.format(self.Code, self.OutputName))
        if self.ProfitMargin == 0:
            self.AddVariable('DEM_' + self.LabourInputName, 'Demand for labour', market_sup_good)
            # self.Equations['PROF'] = ''
        else:
            self.AddVariable('DEM_' + self.LabourInputName, 'Demand for labour',
                             '%0.3f * %s' % (wage_share, market_sup_good))
            self.SetEquationRightHandSide('PROF', '%0.3f * %s' % (self.ProfitMargin, market_sup_good))
        for s in self.Parent.SectorList:
            if 'DIV' in s.EquationBlock.Equations:
                Logger('Adding dividend flow', priority=5)
                self.AddCashFlow('-DIV', 'PROF', 'Dividends paid', is_income=False)
                s.AddCashFlow('DIV', self.GetVariableName('PROF'), 'Dividends received', is_income=True)
                break


class FixedMarginBusinessMultiOutput(Sector):
    """
    Create a business that supplies multiple markets.
    The market objects must exist before creation (so we cannot create Market classes
    that assume the supply objects exist first!).
    """

    def __init__(self, country, code, long_name='', profit_margin=0.0,
                 labour_input_name='LAB', market_list=()):
        if long_name == '':
            long_name = 'Multi-Output Business {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self, country, code, long_name=long_name, has_F=True)
        self.ProfitMargin = profit_margin
        self.LabourInputName = labour_input_name
        self.MarketList = market_list
        self.AddVariable('SUP', 'Total supply', '')
        for market in market_list:
            self.AddMarket(market)
        self.AddVariable('PROF', 'Profits', 'SUP - DEM_{0}'.format(labour_input_name))
        self.AddVariable('DEM_' + labour_input_name, 'Demand for labour.', '')

    def AddMarket(self, market):
        """
        Add a market to the list of suppliers
        :param market: Market
        :return:
        """
        if self.ShareParent(market):
            term = 'SUP_' + market.Code
        else:
            # We do not have the FullCodes yet, but we now know we are in a multi-
            # country model. So we can call Model.GetSectorCodeWithCountry()
            term = 'SUP_' + self.GetModel().GetSectorCodeWithCountry(market)
        self.AddVariable(term, 'Supply of ' + market.Code, '')
        self.AddTermToEquation('SUP', term)

    def _GenerateEquations(self):
        wage_share = 1.0 - self.ProfitMargin
        demand_labour = 'DEM_' + self.LabourInputName
        if self.ProfitMargin == 0:
            self.SetEquationRightHandSide(demand_labour, 'SUP')
        else:
            self.SetEquationRightHandSide(demand_labour, '%0.3f * SUP' % (wage_share,))
            # self.Equations['PROF'] = '%0.3f * %s' % (self.ProfitMargin, market_sup_good)
        for s in self.Parent.SectorList:
            if 'DIV' in s.EquationBlock.Equations:  # pragma: no cover
                raise NotImplementedError('Not tested yet')
                self.AddCashFlow('-DIV', 'PROF', 'Dividends paid', is_income=False)
                s.AddCashFlow('DIV', self.GetVariableName('PROF'), 'Dividends received',
                              is_income=True)
                break


class TaxFlow(Sector):
    """
    TaxFlow: Not really a sector, but keep it in the same list

    Uses the TaxRate of this object, or the TaxRate of the sector (if it is defined).
    """

    def __init__(self, country, code, long_name='', taxrate=0.0, taxes_paid_to='GOV'):
        if long_name == '':
            long_name = 'TaxFlow Object {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self, country, code, long_name, has_F=False)
        self.AddVariable('TaxRate', 'Tax rate', '%0.4f' % (taxrate,))
        self.AddVariable('T', 'Taxes Paid', '')
        self.TaxingSector = taxes_paid_to
        self.TaxRate = taxrate

    def _GenerateEquations(self):
        # Overwrite the tax rate, in case the user sets self.TaxRate directly.
        self.SetEquationRightHandSide('TaxRate', '%0.4f' % (self.TaxRate,))
        terms = []
        # Find all sector that are taxable
        taxrate_name = self.GetVariableName('TaxRate')
        for s in self.CurrencyZone.GetSectors():
            if s.ID == self.ID:
                continue
            if s.IsTaxable:
                # If the sector has a tax rate defined for it, use that tax rate instead of this object's rate.
                # Need to add support for fdiffering rates for each type of income?
                if 'TaxRate' in s.EquationBlock.Equations:
                    tax_name_used = s.GetVariableName('TaxRate')
                else:
                    tax_name_used = taxrate_name
                term = '%s * %s' % (tax_name_used, s.GetVariableName('INC'))
                # The INC variable is pretax.
                s.AddCashFlow('-T', term, 'Taxes paid.', is_income=False)
                terms.append(term)
                #self.AddTermToEquation('T', term)
        self.SetEquationRightHandSide('T', utils.create_equation_from_terms(terms))
        # work on other sectors
        tax_fullname = self.GetVariableName('T')
        gov = self.CurrencyZone.LookupSector(self.TaxingSector)
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

    def __init__(self, country, code='MON', long_name='', issuer_short_code='GOV'):
        FinancialAssetMarket.__init__(self, country, code, long_name,
                                      issuer_short_code=issuer_short_code)

    def _GenerateEquations(self):
        """
        Generate equation.
         :return: None
        """
        Logger('MoneyMarket _GenerateEquations', priority=5)
        dem_name = 'DEM_' + self.Code
        self.AddVariable(dem_name, 'Total demand for ' + self.LongName,'')
        dem_terms = []
        for s in self.SearchListSource.GetSectors():
            if not s.HasF:
                continue
            if s.Code == self.IssuerShortCode:
                Logger('Found Issuer', priority=3)
                s.AddVariable('SUP_' + self.Code, 'Supply of ' + self.LongName, self.GetVariableName(dem_name))
                self.AddVariable('SUP_' + self.Code, 'Supply of ' + self.LongName,
                                 s.GetVariableName('SUP_' + self.Code))
                continue
            try:
                # If the Sector already has demand for this, add the term.
                term = s.GetVariableName(dem_name)
                self.AddTermToEquation(dem_name, term)
                # dem_terms.append(term)
                continue
            except KeyError:
                pass
            Logger('Sector is missing demand for {0}; automatically filled in', priority=3,
                   data_to_format=(dem_name,))
            s.AddVariable(dem_name, 'Demand for ' + self.LongName, s.GetVariableName('F'))
            self.AddTermToEquation(dem_name, s.GetVariableName(dem_name))
            #dem_terms.append(s.GetVariableName(dem_name))
        #self.AddVariable(dem_name, 'Total demand for ' + self.LongName, utils.create_equation_from_terms(dem_terms))


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

    def __init__(self, country, code='DEP', long_name='', issuer_short_code='GOV'):
        FinancialAssetMarket.__init__(self, country, code, long_name=long_name,
                                      issuer_short_code=issuer_short_code)
        self.AddVariable('r', 'Interest rate', '0.')
        self.AddVariable('LAG_r', 'Lagged Interest rate', 'r(k-1)')

    def _GenerateEquations(self):
        """
        Generate equations.
 
        :return: None
        """
        dem_terms = []
        dem_name = 'DEM_' + self.Code
        for s in self.SearchListSource.GetSectors():
            if isinstance(s, Market):
                continue
            if s.Code == self.IssuerShortCode:
                sup_name = 'SUP_' + self.Code
                s.AddVariable(sup_name, 'Supply of ' + self.LongName, self.GetVariableName('DEM_' + self.Code))
                s.AddVariable('LAG_' + sup_name, 'Lagged Supply of ' + self.LongName,
                              s.GetVariableName(sup_name) + '(k-1)')
                s.AddCashFlow('-INT' + self.Code,
                              '{0}*{1}'.format(self.GetVariableName('LAG_r'), s.GetVariableName('LAG_' + sup_name)),
                              'Interest paid on ' + self.LongName)
                self.AddVariable('SUP_' + self.Code, 'Supply of ' + self.LongName,
                                 s.GetVariableName('SUP_' + self.Code))
                continue
            dem_name = 'DEM_' + self.Code
            try:
                # noinspection PyUnusedLocal
                term = s.GetVariableName(dem_name)
            except KeyError:
                continue
            s.AddVariable('LAG_' + dem_name, 'Lagged demand for ' + self.LongName,
                          s.GetVariableName(dem_name) + '(k-1)')
            s.AddCashFlow('+INT' + self.Code,
                          '{0}*{1}'.format(self.GetVariableName('LAG_r'), s.GetVariableName('LAG_' + dem_name)),
                          'Interest received on ' + self.LongName)
            dem_terms.append(s.GetVariableName(dem_name))
        self.AddVariable(dem_name, 'Total demand for ' + self.LongName, utils.create_equation_from_terms(dem_terms))


class GoldStandardCentralBank(CentralBank):
    """
    Central bank that undertakes Gold purchases/sales to balance the foreign exchange
    market.

    Must create an ExternalSector object in the model.
    """
    def __init__(self, country, code, long_name='', treasury=None, initial_gold_stock=0.0):
        if long_name == '':
            long_name = 'Gold Standard Central Bank {0} in {1}'.format(code, country.Code)
        CentralBank.__init__(self, country, code, long_name=long_name, treasury=treasury)
        self.InitialGoldStock = initial_gold_stock

    def _GenerateEquations(self):
        CentralBank._GenerateEquations(self)
        ext = self.GetModel().ExternalSector
        if ext is None:
            msg = 'Must Create an ExternalSector in order to use {0}'.format(type(self))
            raise LogicError(msg)
        purchases = 'GOLDPURCHASES'
        currency = self.CurrencyZone.Currency
        desc = 'Net Purchases of Gold in TK; Forces EXT_FX_NET_TK to zero'.replace('TK', currency)
        currency_balance = ext['FX'].GetVariableName('NET_' + currency)
        # A somewhat recursive definition; has ugly convergence properties.
        # In fact, will not converge without the step adaptation used.
        # An alternative is to create a special function that is run as a final step
        # before solving.
        # It would get the final net supply terms, remove itself, and use that as the
        # supply variable.
        self.AddVariable(purchases, desc, '{0} - {1}'.format(purchases, currency_balance))
        ext['GOLD'].SetGoldPurchases(self, purchases,
                                     self.InitialGoldStock)


class GoldStandardGovernment(DoNothingGovernment):
    """
    Central bank that undertakes Gold purchases/sales to balance the foreign exchange
    market.

    Must create an ExternalSector object in the model.
    """
    def __init__(self, country, code, long_name='', initial_gold_stock=0.0):
        if long_name == '':
            long_name = 'Gold Standard Government {0} in Country {1}'.format(code, country.Code)
        DoNothingGovernment.__init__(self, country, code, long_name)
        self.InitialGoldStock = initial_gold_stock

    def _GenerateEquations(self):
        DoNothingGovernment._GenerateEquations(self)
        ext = self.GetModel().ExternalSector
        if ext is None:
            msg = 'Must Create an ExternalSector in order to use {0}'.format(type(self))
            raise LogicError(msg)
        purchases = 'GOLDPURCHASES'
        currency = self.CurrencyZone.Currency
        desc = 'Net Purchases of Gold in TK; Forces EXT_FX_NET_TK to zero'.replace('TK', currency)
        currency_balance = ext['FX'].GetVariableName('NET_' + currency)
        # A somewhat recursive definition; has ugly convergence properties.
        # In fact, will not converge without the step adaptation used.
        # An alternative is to create a special function that is run as a final step
        # before solving.
        # It would get the final net supply, remove itself, and use that to set supply.
        self.AddVariable(purchases, desc, '{0} - {1}'.format(purchases, currency_balance))
        # Set purchases to 0 at k=0 so that we have a well-defined GOLD variable
        self.AddInitialCondition(purchases, 0.0)
        ext['GOLD'].SetGoldPurchases(self, purchases,
                                     self.InitialGoldStock)
