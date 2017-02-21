"""
chapter4.py
==========

Models from Chapter 4 of [G&L 2012].

- Model PC = Model with Portfolio Choice
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
from sfc_models.models import *
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
        hh.GenerateAssetWeighting([('DEP', eqn)], 'MON')
        # Fix the Pretax income equation to include deposit income.
        hh.Equations['PreTax'] = 'SUP_LAB + INTDEP'


        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            tre.SetExogenous('DEM_GOOD', '[0.,] + [20.,] * 105')
            dep.SetExogenous('r', '[.025,]*10 + [.035,]*105')
            self.Model.AddInitialCondition('HH', 'AfterTax', 86.486)
            self.Model.AddInitialCondition('HH', 'F', 86.486)
            self.Model.AddInitialCondition('HH', 'DEM_DEP', 64.865)
        return self.Model

    def expected_output(self):
        """
        Expected output for the model (using default input).
        Based on Table 3.4, page 69.
        :return: list
        """
        out = [
            ('GOV_DEM_GOOD', [0., 20., 20., 20., 20.]), # G
            ('GOOD_SUP_GOOD', [0., 38.5, 47.9]),  # Y
            ('GOV_T', [0., 7.7, 9.6]),  # T
            ('HH_AfterTax', [0., 30.8, 38.3]), # YD
            ('HH_F', [0., 12.3, 22.7]),  # H = high-powered money
        ]
        return out
