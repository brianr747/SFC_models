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
from sfc_models.utils import register_standard_logs
from sfc_models.models import Model, Country
from sfc_models.sector import Market
from sfc_models.utils import Logger, get_file_base
from sfc_models.sector_definitions import Household, DoNothingGovernment, TaxFlow, FixedMarginBusiness, Capitalists


def CreateCountry(mod, name, code):
    # Create the country.
    cntry = Country(mod, code, name)
    # Create sectors
    DoNothingGovernment(cntry, 'GOV', 'Government')
    Household(cntry, 'HH', 'Household')
    Capitalists(cntry, 'CAP', 'Capitalists')
    # A literally non-profit business sector
    FixedMarginBusiness(cntry, 'BUS', 'Business Sector')
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    TaxFlow(cntry, 'TF', 'TaxFlow', .2)
    Market(cntry, 'LAB', 'Labour market')
    Market(cntry, 'GOOD', 'Goods market')
    return cntry


def main():
    # The next line of code sets the name of the output files based on the code file's name.
    # This means that if you paste this code into a new file, get a new log name.
    register_standard_logs('output', __file__)
    # Create model, which holds all entities
    mod = Model()
    can = CreateCountry(mod, 'Canada', 'CA')
    us = CreateCountry(mod, 'United states', 'US')
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('CA_GOV', 'DEM_GOOD', '[20.,] * 105')
    mod.AddExogenous('US_GOV', 'DEM_GOOD', '[20.,] * 105')
    mod.main()


if __name__ == '__main__':
    main()
