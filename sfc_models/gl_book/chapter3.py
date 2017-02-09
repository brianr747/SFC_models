"""
chapter3.py
==========

Models from Chapter 3 of [G&L 2012].





[G&L 2012] "Monetary Economics: An Integrated Approach to credit, Money, Income, Production
and Wealth; Second Edition", by Wynne Godley and Marc Lavoie, Palgrave Macmillan, 2012.
ISBN 978-0-230-30184-9


Copyright 2017 Brian Romanchuk

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

from sfc_models.gl_book import GL_book_model
from sfc_models.models import *
from sfc_models.sectors import *


class SIM(GL_book_model):
    """
    Implements the SIM model from Chapter 3 of G&L - Section 3.7.1.  SIM = "Simplest model."

    """
    def build_model(self):
        country = self.Country
        gov = DoNothingGovernment(country, 'Government', 'GOV')
        hh = Household(country, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
        # A literally non-profit business sector
        bus = FixedMarginBusiness(country, 'Business Sector', 'BUS', profit_margin=0.0)
        # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
        tax = TaxFlow(country, 'TaxFlow', 'TF', .2)
        labour = Market(country, 'Labour market', 'LAB')
        goods = Market(country, 'Goods market', 'GOOD')
        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            self.Model.AddExogenous('GOV', 'DEM_GOOD', '[0.,] + [20.,] * 105')
        return self.Model


class SIMEX1(GL_book_model):
    """
    Implements the SIMEX model from Chapter 3 of G&L - Section 3.7.1.  SIMEX = "Model SIM (Simplest) with expectations."

    Household consumption is based on expected income, and not realised income. In this version of the model, expected
    income equals the previous period's income.
    """
    def build_model(self):
        country = self.Country
        gov = DoNothingGovernment(country, 'Government', 'GOV')
        hh = HouseholdWithExpectations(country, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
        # A literally non-profit business sector
        bus = FixedMarginBusiness(country, 'Business Sector', 'BUS', profit_margin=0.0)
        # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
        tax = TaxFlow(country, 'TaxFlow', 'TF', .2)
        labour = Market(country, 'Labour market', 'LAB')
        goods = Market(country, 'Goods market', 'GOOD')
        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            self.Model.AddExogenous('GOV', 'DEM_GOOD', '[0.,] + [20.,] * 105')
        return self.Model

