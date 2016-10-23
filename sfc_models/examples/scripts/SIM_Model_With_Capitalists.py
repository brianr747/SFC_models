"""
SIM_Model_With_Capitalists.py

Extend the SIM model (Godley and Lavoie, Chapter 3) with a capitalist sub-sector.

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
    Household(cntry, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
    Capitalists(cntry, 'Capitalists', 'CAP', alpha_income=.6, alpha_fin=.4)
    # A literally non-profit business sector
    FixedMarginBusiness(cntry, 'Business Sector', 'BUS', profit_margin=0.2)
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    TaxFlow(cntry, 'TaxFlow', 'TF', .2)
    Market(cntry, 'Labour market', 'LAB')
    Market(cntry, 'Goods market', 'GOOD')
    return cntry

def main():
    # Create model, which holds all entities
    mod = Model()
    can = CreateCountry(mod, 'Canada', 'CA')
    us = CreateCountry(mod, 'United states', 'US')
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('CA_GOV', 'DEM_GOOD', '[20.,] * 105')
    mod.AddExogenous('US_GOV', 'DEM_GOOD', '[20.,] * 105')
    # Patch the propensity to consume in the United States
    mod.AddExogenous('US_CAP', 'AlphaIncome', '[.1,]*105')
    # Build the model
    # Output is put into two files, based on the file name passed into main() ['out_SIM_Model_With_Capitalists']
    # (1) [...]_log.txt:  Log file
    # (2) [...].py:  File that solves the system of equations
    eqns = mod.main('out_SIM_Model_With_Capitalists')
    import out_SIM_Model_With_Capitalists as SIM_Capitalist
    obj = SIM_Capitalist.SFCModel()
    obj.MaxTime = 20
    obj.PrintIterations = True
    obj.main()
    obj.WriteCSV('out_SIM_Model_With_Capitalists.csv')

    p = Quick2DPlot([obj.t, obj.t], [obj.CA_GOOD_SUP_GOOD, obj.US_GOOD_SUP_GOOD], 'Output - Y', run_now=False)
    p.Legend = ['Canada', 'U.S.']
    p.DoPlot()
    # p = Quick2DPlot([obj.t, obj.t], [obj.BUS_F, obj2.BUS_F], 'Business Sector Financial Assets (F)', run_now=False)
    # p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    # p.DoPlot()
    # p = Quick2DPlot([obj.t, obj.t], [obj.GOV_FISC_BAL, obj2.GOV_FISC_BAL], 'Government Financial Balance',
    #                 run_now=False)
    # p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    # p.DoPlot()

if __name__ == '__main__':
    main()