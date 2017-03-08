"""
ex20170307_Model_REG2.py

Build Model REG2. Second Version of Model REG from Godley & Lavoie (Chapter 6)

Uses the model builder from the sfc_models.gl_book sub-package.

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


import sfc_models
from sfc_models.gl_book.chapter6 import REG2
from sfc_models.examples.Quick2DPlot import Quick2DPlot
from sfc_models import Parameters

sfc_models.register_standard_logs('output', __file__)
Parameters.TraceStep = 1
builder_REG = REG2(country_code='C1', use_book_exogenous=True)

model = builder_REG.build_model()
Parameters.InitialEquilibriumStepError = 1e-5
Parameters.SolveInitialEquilibrium = False
Parameters.TraceStep = 1


# Generate the file name using an operating system independent tool - os.path.join
model.main()


model.TimeSeriesCutoff = 40

time = model.GetTimeSeries('t')
# Y_PC = model.GetTimeSeries('GOOD_SUP_GOOD')
# r = model.GetTimeSeries('DEP_r')
# Y_d = model.GetTimeSeries('HH_AfterTax')
# FB = model.GetTimeSeries('TRE_FISCBAL')
# PB = model.GetTimeSeries('TRE_PRIM_BAL')
#
# Quick2DPlot(time, r, 'Interest Rate - Model PC')
# Quick2DPlot(time, Y_PC, 'Output (Y) - Model PC')
# Quick2DPlot(time, Y_d, 'Household Disposable Income - Model PC')
# Quick2DPlot(time, FB, 'Fiscal Balance - Model PC')
# Quick2DPlot(time, PB, 'Primary Fiscal Balance')


