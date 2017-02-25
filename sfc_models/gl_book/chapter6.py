"""
chapter6.py
==========

Models from Chapter 6 of [G&L 2012].

- Model REG = Regional Model (Country divided into North and South regions.)

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

class REG(GL_book_model):
    """
    Implements Model REG from Chapter 6 of G&L. REG = "Regional."

    This could have been attempted with two countries (which have the same
    currency), but there's only a single central bank and Treasury. Splitting
    into two countries would mean that we would need to aggregate two different
    government sectors.
    """
    def build_model(self):
        country = self.Country
        # As before, there's only one copy of the governmental sectors
        tre = Treasury(country, 'Treasury', 'TRE')
        cb = CentralBank(country, 'Central Bank', 'CB', treasury=tre)
        # Now we split
        hh_n = Household(country, 'Household - North', 'HH_N', alpha_income=.6, alpha_fin=.4, labour_name='LAB_N',
                         consumption_good_name='GOOD')
        hh_s = Household(country, 'Household - South', 'HH_S', alpha_income=.7, alpha_fin=.3, labour_name='LAB_S',
                         consumption_good_name='GOOD')
        # Calculate total good consumption using existing function, then split the
        # demand between North/South
        hh_n.AddVariable('DEM_GOOD_N', 'Demand for Goods Produced in North', 'DEM_GOOD- DEM_GOOD_S')
        hh_n.AddVariable('DEM_GOOD_S', 'Demand for goods from south (imports)', 'MU*PreTax')
        hh_n.AddVariable('MU', 'Propensity to import', '0.18781')
        hh_s.AddVariable('DEM_GOOD_S', 'Demand for Goods Produced in South', 'DEM_GOOD- DEM_GOOD_N')
        hh_s.AddVariable('DEM_GOOD_N', 'Demand for goods from North (imports)', 'MU*PreTax')
        hh_s.AddVariable('MU', 'Propensity to import', '0.18781')

        # A literally non-profit business sector
        bus_n = FixedMarginBusiness(country, 'Business Sector - North', 'BUS_N', profit_margin=0.0)
        bus_s = FixedMarginBusiness(country, 'Business Sector - South', 'BUS_S', profit_margin=0.0)
        # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
        tax = TaxFlow(country, 'TaxFlow', 'TF', .2, taxes_paid_to='TRE')
        labour_s = Market(country, 'Labour market', 'LAB_S')
        labour_n = Market(country, 'Labour market', 'LAB_N')
        goods_n = Market(country, 'Goods market - North', 'GOOD_N')
        goods_s = Market(country, 'Goods market - South', 'GOOD_S')
        mm = MoneyMarket(country, issuer_short_code='CB')
        dep = DepositMarket(country, issuer_short_code='TRE')
        # Create the demand for deposits.  ('MON' is the residual asset.)
        hh_n.AddVariable('L0', 'lambda_0: share of bills in wealth', '0.635')
        hh_n.AddVariable('L1', 'lambda_1: parameter related to interest rate', '5.')
        hh_n.AddVariable('L2', 'lambda_2: parameter related to disposable income', '.01')
        # Generate the equation. Need to get the name of the interest rate variable
        r = dep.GetVariableName('r')
        # The format() call will replace '{0}' with the contents of the 'r' variable.
        eqn = 'L0 + L1 * {0} - L2 * (AfterTax/F)'.format(r)
        hh_n.GenerateAssetWeighting([('DEP', eqn)], 'MON')
        # Create the demand for deposits.  ('MON' is the residual asset.)
        hh_s.AddVariable('L0', 'lambda_0: share of bills in wealth', '0.67')
        hh_s.AddVariable('L1', 'lambda_1: parameter related to interest rate', '6.')
        hh_s.AddVariable('L2', 'lambda_2: parameter related to disposable income', '.07')
        # Generate the equation. Need to get the name of the interest rate variable
        r = dep.GetVariableName('r')
        # The format() call will replace '{0}' with the contents of the 'r' variable.
        eqn = 'L0 + L1 * {0} - L2 * (AfterTax/F)'.format(r)
        hh_s.GenerateAssetWeighting([('DEP', eqn)], 'MON')

        # Fix the Pretax income equation to include deposit income.
        hh_n.Equations['PreTax'] = 'SUP_LAB_N + INTDEP'
        hh_s.Equations['PreTax'] = 'SUP_LAB_S + INTDEP'
        # Add a decorative equation: Government Fiscal Balance
        # = Primary Balance - Interest expense + Central Bank Dividend (= interest
        # received by the central bank).
        tre.AddVariable('FISCBAL', 'Fiscal Balance', 'PRIM_BAL - INTDEP + CB_INTDEP')


        if self.UseBookExogenous:
            # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
            tre.SetExogenous('DEM_GOOD_N', '[20.,] * 105')
            tre.SetExogenous('DEM_GOOD_S', '[20.,] * 105')
            dep.SetExogenous('r', '[.025,]*10 + [.035,]*105')
            # NOTE:
            # Initial conditions are only partial; there may be issues with some
            # variables.
            self.Model.AddInitialCondition('HH', 'AfterTax', 86.486)
            self.Model.AddInitialCondition('HH_N', 'F', 86.486)
            self.Model.AddInitialCondition('HH_S', 'F', 86.486)
            self.Model.AddInitialCondition('TRE', 'F', 2.*-86.486)
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
            ('t', [None, 1951., 1952., 1953.,]),
            ('TRE_DEM_GOOD', [None, 20., 20., 20., 20.]), # G
            ('DEP_r', [0.025,]* 10 + [.035]*5),
            ('HH_WGT_DEP', [None, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.80, 0.80, 0.80, 0.80, 0.80,
                            0.80, 0.80]), # Weight of deposits (bills)
            ('HH_AfterTax', [None, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 86.49, 87.72,
                             88.04, 88.32, 88.56, 88.77, 88.95, 89.11]),  # YD
            ('TRE_T', [None, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.93, 22.01, 22.08,
                       22.14, 22.19, 22.24, 22.28]),  # T
            ('GOOD_SUP_GOOD', [None, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49, 106.49,
                               107.22, 107.62, 107.95, 108.25, 108.50, 108.71, 108.90, 109.06, 109.20, 109.33]),  # Y
            ('HH_DEM_MON', [None, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 21.62, 17.30, 17.40, 17.49,
                        17.56, 17.62, 17.68, 17.72, 17.76, 17.80]),  # high-powered money (H)
        ]
        return out
