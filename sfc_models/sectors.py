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


class Household(Sector):
    def __init__(self, country, long_name, code, alpha_income, alpha_fin):
        Sector.__init__(self, country, long_name, code)
        self.AlphaIncome = alpha_income
        self.AlphaFin = alpha_fin
        self.AddVariable('AlphaIncome', 'Parameter for consumption out of income', '%0.4f' % (self.AlphaIncome,))
        self.AddVariable('AlphaFin', 'Parameter for consumption out of financial assets', '%0.4f' % (self.AlphaFin,))
        self.AddVariable('DEM_GOOD', 'Expenditure on goods consumption', 'AlphaIncome * AfterTax + AlphaFin * LAG_F')
        self.AddVariable('SUP_LAB', 'Supply of Labour', '<To be determined>')
        self.AddVariable('PreTax', 'Pretax income', 'SUP_LAB')
        self.AddVariable('AfterTax', 'Aftertax income', 'PreTax - T')
        self.AddVariable('T', 'Taxes paid.', '')


class DoNothingGovernment(Sector):
    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')


class TaxFlow(Sector):
    """
    TaxFlow: Not really a sector, but keep it in the same list
    """

    def __init__(self, country, long_name, code, taxrate):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('TaxRate', 'Tax rate', '%0.4f' % (taxrate,))
        self.AddVariable('T', 'Taxes Paid', '<To be determined>')

    def GenerateEquations(self):
        hh = self.Parent.LookupSector('HH')
        hh_name = hh.GetVariableName('SUP_LAB')
        self.Equations['T'] = 'TaxRate * %s' % (hh_name, )
        # work on other sectors
        tax_fullname = self.GetVariableName('T')
        hh.AddCashFlow('-T', tax_fullname, 'Taxes paid.')
        gov = self.Parent.LookupSector('GOV')
        gov.AddCashFlow('T', tax_fullname, 'Tax revenue received.')