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

import sfc_models
from sfc_models.examples.Quick2DPlot import Quick2DPlot
from sfc_models.models import Model, Country
from sfc_models.sector import Market
from sfc_models.utils import Logger, get_file_base
from sfc_models.sector_definitions import Household, DoNothingGovernment, TaxFlow, FixedMarginBusiness


def main():
    # The next line of code sets the name of the output files based on the code file's name.
    # This means that if you paste this code into a new file, get a new log name.
    sfc_models.register_standard_logs('output', __file__)
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

    # Do the main work of building and solving the model
    mod.main()
    CUT = 25
    t = mod.GetTimeSeries('t', cutoff=CUT)
    Y_CA = mod.GetTimeSeries('CA_GOOD__SUP_GOOD', cutoff=CUT)
    Y_US = mod.GetTimeSeries('US_GOOD__SUP_GOOD', cutoff=CUT)
    p = Quick2DPlot([t,t], [Y_CA, Y_US], 'Output - Y', run_now=False)
    p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    p.DoPlot()
    F_CA = mod.GetTimeSeries('CA_BUS__F', cutoff=CUT)
    F_US = mod.GetTimeSeries('US_BUS__F', cutoff=CUT)
    p = Quick2DPlot([t, t], [F_CA, F_US], 'Business Sector Financial Assets (F)', run_now=False)
    p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    p.DoPlot()
    BAL_CA = mod.GetTimeSeries('CA_GOV__FISC_BAL', cutoff=CUT)
    BAL_US = mod.GetTimeSeries('US_GOV__FISC_BAL', cutoff=CUT)
    p = Quick2DPlot([t, t], [BAL_CA, BAL_US], 'Government Financial Balance', run_now=False)
    p.Legend = ['Canada (0% profit)', 'U.S. (10% Profit)']
    p.DoPlot()


if __name__ == '__main__':
    main()
