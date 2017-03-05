"""
build_SIM_model.py

Build the classic SIM model (G&L Chapter 3) using sfc_model classes.

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

import os

from sfc_models.examples import get_file_base
from sfc_models.models import *
from sfc_models.sector import Market
from sfc_models.sectors import Household, DoNothingGovernment, TaxFlow, FixedMarginBusiness


def main():
    # Create model, which holds all entities
    mod = Model()
    # Create first country - Canada. (This model only has one country.)
    can = Country(mod, 'Canada', 'CA')
    # Create sectors
    gov = DoNothingGovernment(can, 'Government', 'GOV')
    hh = Household(can, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
    # A literally non-profit business sector
    bus = FixedMarginBusiness(can, 'Business Sector', 'BUS', profit_margin=0.0)
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    tax = TaxFlow(can, 'TaxFlow', 'TF', .2)
    labour = Market(can, 'Labour market', 'LAB')
    goods = Market(can, 'Goods market', 'GOOD')
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('GOV', 'DEM_GOOD', '[20.,] * 105')
    # This line sets the name of the output files based on the code file's name...
    base_name = os.path.join('output', get_file_base(__file__))
    # Build the model
    mod.main(base_name)
    print(mod.EquationSolver.TimeSeries)

    # # Only import after the file is created (which is unusual).
    # import out_SIM_Machine_Model
    # obj = out_SIM_Machine_Model.SFCModel()
    # obj.main_deprecated()
    # obj.WriteCSV('out_SIM_Machine_Model.csv')
    # Quick2DPlot(obj.t, obj.GOOD_SUP_GOOD, 'Goods supplied (national production Y)')
    # Quick2DPlot(obj.t, obj.HH_F, 'Household Financial Assets (F)')
    # #-------------------------------------------------------------------------------
    # # Create a second country, with non-zero profits
    # # (Could have done this within a single model, but equations would have been ridiculous.)
    # # This is a very error-prone way of building the model; if we repeat code blocks, they should be in
    # # a function. It took me 5 tries to eliminate the errors after the cut and paste...
    # mod2 = Model()
    # # Create first country - Canada. (This model only has one country.)
    # us = Country(mod2, 'United States', 'US')
    # # Create sectors
    # gov2 = DoNothingGovernment(us, 'Government', 'GOV')
    # hh2 = Household(us, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
    # # Profit margin of 10%
    # bus2 = FixedMarginBusiness(us, 'Business Sector', 'BUS', profit_margin=0.1)
    # # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    # tax2 = TaxFlow(us, 'TaxFlow', 'TF', .2)
    # labor2 = Market(us, 'Labor market', 'LAB')
    # goods2 = Market(us, 'Goods market', 'GOOD')
    # # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    # mod2.AddExogenous('GOV', 'DEM_GOOD', '[20.,] * 105')
    # # Build the model
    # # Output is put into two files, based on the file name passed into main() ['out_SIM_Machine_Model_2']
    # # (1) [out_SIM_machine_Model_2]_log.txt:  Log file
    # # (2) [out_SIM_machine_Model_2].py:  File that solves the system of equations
    # eqns = mod2.main_deprecated('out_SIM_Machine_Model_2')
    #
    # # Only import after the file is created (which is unusual).
    # import out_SIM_Machine_Model_2
    # obj2 = out_SIM_Machine_Model_2.SFCModel()
    # obj2.main_deprecated()
    # obj2.WriteCSV('out_SIM_Machine_Model_2.csv')
    # p = Quick2DPlot([obj.t, obj.t], [obj.GOOD_SUP_GOOD, obj2.GOOD_SUP_GOOD], 'Output - Y', run_now=False)
    # p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    # p.DoPlot()
    # p = Quick2DPlot([obj.t, obj.t], [obj.BUS_F, obj2.BUS_F], 'Business Sector Financial Assets (F)', run_now=False)
    # p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    # p.DoPlot()
    # p = Quick2DPlot([obj.t, obj.t], [obj.GOV_FISC_BAL, obj2.GOV_FISC_BAL], 'Government Financial Balance',
    #                 run_now=False)
    # p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    # p.DoPlot()


if __name__ == '__main__':
    main()
