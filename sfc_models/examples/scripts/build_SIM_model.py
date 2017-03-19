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

# This next line imports all of the objects used.
# The syntax "from <module> import *" is frowned upon, but I want to reduce the number of lines of
# code in these simpler examples.
from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot


def main():
    # The next line of code sets the name of the output files based on the code file's name.
    # This means that if you paste this code into a new file, get a new log name.
    register_standard_logs('output', __file__)
    # Create model, which holds all entities
    mod = Model()
    mod.EquationSolver.TraceStep = 10
    # Create first country - Canada. (This model only has one country.)
    can = Country(mod, 'CA', 'Canada')
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
    mod.AddExogenous('GOV', 'DEM_GOOD', '[0.,]*5 + [20.,] * 105')
    # Build the model
    mod.main()
    CUT = 30
    k = mod.GetTimeSeries('k', cutoff=CUT)
    goods_produced = mod.GetTimeSeries('BUS__SUP_GOOD', cutoff=CUT)
    Quick2DPlot(k, goods_produced, 'Goods Produced (National Output)')




if __name__ == '__main__':
    main()
