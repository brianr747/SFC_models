"""
chapter3.py
==========

Models from Chapter 3 of [G&L 2012].

- Model SIM = Simplest SFC Model
- Model SIMEX1 = Model SIM + Expectations. This version features expected income that is the previous period's
  realised income.

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
from sfc_models.sector_definitions import DoNothingGovernment, Household, FixedMarginBusiness, TaxFlow, HouseholdWithExpectations
from sfc_models.sector import Market


class SIM(GL_book_model):
    """
    Implements the SIM model from Chapter 3 of G&L - Section 3.7.1.  SIM = "Simplest model."

    """

    def build_model(self):
        country = self.Country
        gov = DoNothingGovernment(country, 'GOV', 'Government')
        hh = Household(country, 'HH', 'Household', alpha_income=.6, alpha_fin=.4)
        # A literally non-profit business sector
        bus = FixedMarginBusiness(country, 'BUS', 'Business Sector')
        # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
        tax = TaxFlow(country, 'TF', 'TaxFlow', taxrate=.2)
        labour = Market(country, 'LAB', 'Labour market')
        goods = Market(country, 'GOOD', 'Goods market')
        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            gov.SetExogenous('DEM_GOOD', '[0.,] + [20.,] * 105')
        return self.Model

    def expected_output(self):
        """
        Expected output for the model (using default input).
        Based on Table 3.4, page 69.
        :return: list
        """
        out = [
            ('GOV__DEM_GOOD', [0., 20., 20., 20., 20.]),  # G
            ('GOOD__SUP_GOOD', [0., 38.44, 47.9]),  # Y
            ('GOV__T', [0., 7.7, 9.6]),  # T
            ('HH__AfterTax', [0., 30.8, 38.3]),  # YD
            ('HH__F', [0., 12.3, 22.7]),  # H = high-powered money
        ]
        return out


class SIMEX1(GL_book_model):
    """
    Implements the SIMEX model from Chapter 3 of G&L - Section 3.7.1.  SIMEX = "Model SIM (Simplest) with expectations."

    Household consumption is based on expected income, and not realised income. In this version of the model, expected
    income equals the previous period's income.

    (Another version of SIMEX within the book has expectations that do not change, hence this model is referred to as
    SIMEX1.)

    In order to replicate the book results, we need to patch in a value for the expected income for the first period.
    This is done by setting the after-tax income level for period 0.

    From page 81:
        Here things are much simpler. For instance, starting again from scratch,
        as we did with the numerical example of Table 3.4, we can suppose that, in
        the second period, households only expect as income the services purchased
        by government. [Brian R: This means that expected after tax income is $20 - $4 = $16.]

    (My thanks to Marc Lavoie for highlighting this text; I did not get the correct interpretation of that
     passage.)I
    """

    def build_model(self):
        country = self.Country
        gov = DoNothingGovernment(country, 'GOV', 'Government')
        hh = HouseholdWithExpectations(country, 'HH', 'Household', alpha_income=.6, alpha_fin=.4)
        # A literally non-profit business sector
        bus = FixedMarginBusiness(country, 'BUS', 'Business Sector')
        # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
        tax = TaxFlow(country, 'TF', 'TaxFlow', .2)
        labour = Market(country, 'LAB', 'Labour market')
        goods = Market(country, 'GOOD', 'Goods market')
        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            gov.SetExogenous('DEM_GOOD', '[0.,] + [20.,] * 105')
            # In order to replicate the book results, we need to patch in this initial condition so that the
            # expected income in period 1 is 16.
            self.Model.AddInitialCondition('HH', 'AfterTax', 16.)
        return self.Model

    def expected_output(self):
        """
        Expected output for the model (using default input).
        Based on Table 3.6, page 69.
        :return: list
        """
        out = [
            ('GOV__DEM_GOOD', [0., 20., 20., 20., 20.]),  # G
            ('GOOD__SUP_GOOD', [0., 29.6, 39.8]),  # Y   NOTE: Book has 39.9 as the final figure...
            ('GOV__T', [0., 5.9, 8.0]),  # T
            ('HH__AfterTax', [16., 23.7, 31.9]),  # YD
            ('HH__EXP_AfterTax', [0., 16., 23.7]),  # Expected YD
            ('HH__F', [0., 14.1, 26.1]),  # H = high-powered money
        ]
        return out
