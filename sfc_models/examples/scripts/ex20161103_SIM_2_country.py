"""
ex20161103_SIM_2_country.py

Build a modified SIM model (G&L Chapter 3) for two countries, one with non-zero profits,
using sfc_model classes.

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
from sfc_models.sectors import Household, DoNothingGovernment, TaxFlow, FixedMarginBusiness


def main():
    # Create model, which holds all entities
    mod = Model()
    # Create first country - Canada.
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

    # Create a second country, with non-zero profits
    # This is a very error-prone way of building the model; if we repeat code blocks, they should be in
    # a function.
    # Create United States - Almost identical to Canada.
    us = Country(mod, 'United States', 'US')
    # Create sectors
    gov2 = DoNothingGovernment(us, 'Government', 'GOV')
    hh2 = Household(us, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
    # ********** Profit margin of 10% *****************
    bus2 = FixedMarginBusiness(us, 'Business Sector', 'BUS', profit_margin=0.1)
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    tax2 = TaxFlow(us, 'TaxFlow', 'TF', .2)
    labor2 = Market(us, 'Labor market', 'LAB')
    goods2 = Market(us, 'Goods market', 'GOOD')
    # *****************************************************************
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    # Since we have a two country model, we need to specify the full sector code, which includes the country code.
    mod.AddExogenous('CA_GOV', 'DEM_GOOD', '[20.,] * 105')
    mod.AddExogenous('US_GOV', 'DEM_GOOD', '[20.,] * 105')
    # Build the model
    # Output is put into two files, based on the file name passed into main() ['out_SIM_Machine_Model_2']
    # (1) [out_ex20161103]_log.txt:  Log file
    # (2) [out_ex20161103].py:  File that solves the system of equations
    eqns = mod.main_deprecated('out_ex20161103')

    # Only import after the file is created (which is unusual).
    import out_ex20161103 as SFCmod
    obj = SFCmod.SFCModel()
    obj.main()
    obj.WriteCSV('out_ex20161103.csv')
    p = Quick2DPlot([obj.t, obj.t], [obj.CA_GOOD_SUP_GOOD, obj.US_GOOD_SUP_GOOD], 'Output - Y', run_now=False)
    p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    p.DoPlot()
    p = Quick2DPlot([obj.t, obj.t], [obj.CA_BUS_F, obj.US_BUS_F], 'Business Sector Financial Assets (F)', run_now=False)
    p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    p.DoPlot()
    p = Quick2DPlot([obj.t, obj.t], [obj.CA_GOV_FISC_BAL, obj.US_GOV_FISC_BAL], 'Government Financial Balance',
                    run_now=False)
    p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    p.DoPlot()


if __name__ == '__main__':
    main()
