"""
intro_3_02_example.py

First example code from Section 3.2 of "Introduction to SFC Models With Python."

Implements model SIM from Godley and Lavoie.


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


# Step 1: Import modules
# sfc_models code objects. Using "from <module> import *" is frowned upon, but I wanted to
# have less lines of code for beginners to parse.
from sfc_models.objects import *
# Quick2DPlot() - Plotting functions used by examples; relies upon matplotlib
from sfc_models.examples.Quick2DPlot import Quick2DPlot

# Step 1.5: set up logging
# The next line of code sets the name of the output files based on the code file's name.
# This means that if you paste this code into a new file, get a new log name.
register_standard_logs('output', __file__)

# Step 2: build the model objects
# Create model, which holds all entities
mod = Model()
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
mod.AddExogenous('GOV', 'DEM_GOOD', '[20.,] * 105')
# Step 3: Invoke the method ("main") that builds the model.
mod.main()

# Once the framework has built and solved the model equations, we can either work with the output files,
# or within Python. Here, we do a plot with Quick2DPlot.
mod.TimeSeriesCutoff = 20
time = mod.GetTimeSeries('k')
Y_SIM = mod.GetTimeSeries('GOOD__SUP_GOOD')
Quick2DPlot(time, Y_SIM, 'Output (Y) - Model SIM', filename='intro_3_02_Y.png')
