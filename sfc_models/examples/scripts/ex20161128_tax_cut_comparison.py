"""
ex20161128_tax_cut_comparison.py

Extend the SIM model (Godley and Lavoie, Chapter 3) with a capitalist sub-sector,
and then look at the effect of a tax cut.

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

from sfc_models.examples.Quick2DPlot import Quick2DPlot
from sfc_models.models import *
from sfc_models.sectors import Household, DoNothingGovernment, TaxFlow, FixedMarginBusiness, Capitalists


def CreateCountry(mod, name, code):
    # Create the country.
    cntry = Country(mod, name, code)
    # Create sectors
    DoNothingGovernment(cntry, 'Government', 'GOV')
    hou = Household(cntry, 'Household', 'HH', alpha_income=.75, alpha_fin=.5)
    hou.AddVariable('TaxRate', 'Tax rate for workers', '.2')
    cap = Capitalists(cntry, 'Capitalists', 'CAP', alpha_income=.2, alpha_fin=.3)
    cap.AddVariable('TaxRate', 'Tax rate for capitalists', '0.3')
    FixedMarginBusiness(cntry, 'Business Sector', 'BUS', profit_margin=0.2)
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    TaxFlow(cntry, 'TaxFlow', 'TF', .2)
    Market(cntry, 'Labour market', 'LAB')
    Market(cntry, 'Goods market', 'GOOD')
    return cntry


def main():
    # Create model, which holds all entities
    mod = Model()
    can = CreateCountry(mod, 'Scenario 1', 'SCEN1')
    us = CreateCountry(mod, 'Scenario 2', 'SCEN2')
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('SCEN1_GOV', 'DEM_GOOD', '[20.,] * 105')
    mod.AddExogenous('SCEN2_GOV', 'DEM_GOOD', '[20.,] * 105')
    # clean up output by starting at steady state by setting initial F
    mod.AddInitialCondition('SCEN1_HH', 'F', 29.09)
    mod.AddInitialCondition('SCEN1_CAP', 'F', 33.94)
    mod.AddInitialCondition('SCEN2_HH', 'F', 29.09)
    mod.AddInitialCondition('SCEN2_CAP', 'F', 33.94)
    # Generate a $1 tax cut based on steady state values.
    # Scenario #1: Tax cut for workers at t=5
    # Initial tax rate is 20%, and pays $14.545 in tax, so cut tax rate to 18.6%.
    # (tax rate = [.2, .2, .2, .2, .2, .186 ,186 ...]
    mod.AddExogenous('SCEN1_HH', 'TaxRate', '[0.2,]*5 + [0.186,]*100')
    # Scenario #2: Tax cut for capitalists at t=5
    # Initial tax rate is 30%, and pays $5.455 in tax, so cut tax rate to 24.5%.
    # (tax rate = [.3, .3, .3, .3, .3, .245 , ,245 ...]
    mod.AddExogenous('SCEN2_CAP', 'TaxRate', '[0.3,]*5 + [0.245,]*100')

    # Build the model
    # Output is put into two files, based on the file name passed into main() ['ex20161128_tax_cut_comparison']
    # (1) [...]_log.txt:  Log file
    # (2) [...].py:  File that solves the system of equations
    eqns = mod.main_deprecated('out_ex20161128_tax_cut_comparison')
    import out_ex20161128_tax_cut_comparison as SIM_Capitalist
    obj = SIM_Capitalist.SFCModel()
    obj.MaxTime = 40
    obj.PrintIterations = True
    obj.main()
    obj.WriteCSV('out_ex20161128_tax_cut_comparison.csv')

    p = Quick2DPlot([obj.t[1:], obj.t[1:]], [obj.SCEN1_GOOD_SUP_GOOD[1:], obj.SCEN2_GOOD_SUP_GOOD[1:]], 'Output - Y',
                    run_now=False)
    p.Legend = ['Scenario #1 - Worker Tax Cut', 'Scenario #2 - Capitalist Tax Cut']
    p.LegendPos = 'center right'
    p.DoPlot()


if __name__ == '__main__':
    main()
