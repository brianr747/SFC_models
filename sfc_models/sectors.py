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
from sfc_models.models import Sector
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
        self.AddVariable('FISC_BAL', 'Government Fiscal Balance', 'T - DEM_GOOD')


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
    """

    def __init__(self, country, long_name, code, taxrate):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('TaxRate', 'Tax rate', '%0.4f' % (taxrate,))
        self.AddVariable('T', 'Taxes Paid', '<To be determined>')

    def GenerateEquations(self):
        terms = []
        # Find all sector that are taxable
        taxrate_name = self.GetVariableName('TaxRate')
        for s in self.Parent.SectorList:
            if s.ID == self.ID:
                continue
            if 'PreTax' in s.Equations:
                term = '%s * %s' % (taxrate_name, s.GetVariableName('PreTax'))
                s.AddCashFlow('-T', term, 'Taxes paid.')
                terms.append('+' + term)
        self.Equations['T'] = utils.create_equation_from_terms(terms)
        # work on other sectors
        tax_fullname = self.GetVariableName('T')
        gov = self.Parent.LookupSector('GOV')
        gov.AddCashFlow('T', tax_fullname, 'Tax revenue received.')