"""
ex20170108_model_PC.py

Create Model PC (Godley & Lavoie Chapter 4).


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


from sfc_models.examples.Quick2DPlot import Quick2DPlot
from sfc_models.models import *
from sfc_models.sectors import Household, Treasury, CentralBank, TaxFlow, FixedMarginBusiness, DepositMarket, MoneyMarket


def main():
    # Create model, which holds all entities
    mod = Model()
    # Create first country - Canada. (This model only has one country.)
    can = Country(mod, 'Canada', 'CA')
    # Create sectors
    tre = Treasury(can, 'Treasury', 'TRE')
    cb = CentralBank(can, 'Central Bank', 'CB', treasury=tre)
    hh = Household(can, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
    # A literally non-profit business sector
    bus = FixedMarginBusiness(can, 'Business Sector', 'BUS', profit_margin=0.0)
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    tax = TaxFlow(can, 'TaxFlow', 'TF', .2, taxes_paid_to='TRE')
    labour = Market(can, 'Labour market', 'LAB')
    goods = Market(can, 'Goods market', 'GOOD')
    # Add the financial markets
    # GOV -> issuing sector
    mm = MoneyMarket(can, issuer_short_code='CB')
    dep = DepositMarket(can, issuer_short_code='TRE')
    # --------------------------------------------
    # Financial asset demand equations
    # Need to call this before we set the demand functions for
    mod.GenerateFullSectorCodes()
    # Need the full variable name for 'F' in household
    hh_F = hh.GetVariableName('F')
    hh.AddVariable('DEM_MON', 'Demand for Money', '0.5 * ' + hh_F)
    hh.AddVariable('DEM_DEP', 'Demand for deposits', '0.5 * ' + hh_F)
    # -----------------------------------------------------------------
    # Need to set the exogenous variables
    # Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('TRE', 'DEM_GOOD', '[20.,] * 105')
    mod.AddExogenous('DEP', 'r', '[0.0,] * 5 + [0.04]*100')
    mod.AddInitialCondition('HH', 'F', 80.)
    # Build the model
    # Output is put into two files, based on the file name passed into main() ['out_SIM_Machine_Model']
    # (1) [out_YYY]_log.txt:  Log file
    # (2) [out_YYY].py:  File that solves the system of equations
    mod.NumberIterations = 100
    eqns = mod.main_deprecated('out_ex20170108_model_PC')

    # Only import after the file is created (which is unusual).
    import out_ex20170108_model_PC as SFCmod
    obj = SFCmod.SFCModel()
    obj.main()
    obj.WriteCSV('out_ex20170103_model_PC.csv')
    Quick2DPlot(obj.t[1:], obj.GOOD_SUP_GOOD[1:], 'Goods supplied (national production Y)')
    Quick2DPlot(obj.t[1:], obj.HH_F[1:], 'Household Financial Assets (F)')


if __name__ == '__main__':
    main()