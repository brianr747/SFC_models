"""
chapter4.py
==========

Models from Chapter 4 of [G&L 2012].

- Model PC = Model with Portfolio Choice

Note that if using the book initial conditions, not all variables are being set at
present. This will affect some stock variable accounting.

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
from sfc_models.sectors import *


class PC(GL_book_model):
    """
    Implements Model PC from Chapter 4 of G&L. PC = "Portfolio Choice."

    """

    def build_model(self):
        country = self.Country
        tre = Treasury(country, 'Treasury', 'TRE')
        cb = CentralBank(country, 'Central Bank', 'CB', treasury=tre)
        hh = Household(country, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
        # A literally non-profit business sector
        bus = FixedMarginBusiness(country, 'Business Sector', 'BUS', profit_margin=0.0)
        # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
        tax = TaxFlow(country, 'TaxFlow', 'TF', .2, taxes_paid_to='TRE')
        labour = Market(country, 'Labour market', 'LAB')
        goods = Market(country, 'Goods market', 'GOOD')
        mm = MoneyMarket(country, issuer_short_code='CB')
        dep = DepositMarket(country, issuer_short_code='TRE')
        # Create the demand for deposits.  ('MON' is the residual asset.)
        hh.AddVariable('L0', 'lambda_0: share of bills in wealth', '0.635')
        hh.AddVariable('L1', 'lambda_1: parameter related to interest rate', '5.')
        hh.AddVariable('L2', 'lambda_2: parameter related to disposable income', '.01')
        # Generate the equation. Need to get the name of the interest rate variable
        r = dep.GetVariableName('r')
        # The format() call will replace '{0}' with the contents of the 'r' variable.
        eqn = 'L0 + L1 * {0} - L2 * (AfterTax/F)'.format(r)
        hh.GenerateAssetWeighting({'DEP': eqn}, 'MON')
        # Add a decorative equation: Government Fiscal Balance
        # = Primary Balance - Interest expense + Central Bank Dividend (= interest
        # received by the central bank).
        tre.AddVariable('FISCBAL', 'Fiscal Balance', 'PRIM_BAL - INTDEP + CB__INTDEP')

        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            tre.SetExogenous('DEM_GOOD', '[20.,] * 105')
            dep.SetExogenous('r', '[.025,]*10 + [.035,]*105')
            # NOTE:
            # Initial conditions are only partial; there may be issues with some
            # variables.
            self.Model.AddInitialCondition('HH', 'AfterTax', 86.486)
            self.Model.AddInitialCondition('HH', 'F', 86.486)
            self.Model.AddInitialCondition('TRE', 'F', -86.486)
            self.Model.AddInitialCondition('HH', 'DEM_DEP', 64.865)
            self.Model.AddGlobalEquation('t', 'decorated time axis', '1950. + k')
        return self.Model

    def expected_output(self):
        """
        Expected output for the model (using default input).
        Based on EViews output using code from Gennaro Zezza (from sfcmodels.net)

        NOTE: A spreadsheet at sfcmodels.net gives different output; income is changing during the
        same period as the rate change.

        We ignore value at t=0
        :return: list
        """
        out = [
            ('t', [None, 1951., 1952., 1953., ]),
            ('TRE__DEM_GOOD', [None, 20., 20., 20., 20.]),  # G
            ('DEP__r', [0.025, ] * 10 + [.035] * 5),
            ('HH__WGT_DEP', [None, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.80, 0.80, 0.80, 0.80, 0.80,
                            0.80, 0.80]),  # Weight of deposits (bills)
            ('HH__AfterTax', [None, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 87.72,
                             88.04, 88.32, 88.56, 88.77, 88.95, 89.11]),  # YD
            ('TRE__T', [None, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.93, 22.01, 22.08,
                       22.14, 22.19, 22.24, 22.28]),  # T
            ('GOOD__SUP_GOOD', [None, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49,
                               107.22, 107.62, 107.95, 108.25, 108.50, 108.71, 108.90, 109.06, 109.20, 109.33]),  # Y
            ('HH__DEM_MON', [None, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 17.30, 17.40, 17.49,
                            17.56, 17.62, 17.68, 17.72, 17.76, 17.80]),  # high-powered money (H)
        ]
        return out
