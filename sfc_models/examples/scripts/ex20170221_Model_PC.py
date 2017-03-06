"""
ex20170221_Model_PC.py

Build Model PC from Godley & Lavoie (Chapter 4)

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


from sfc_models.gl_book.chapter4 import PC
from sfc_models.examples.Quick2DPlot import Quick2DPlot
from sfc_models import Parameters
import sfc_models

# Set up the standard logs in the "output" subdirectory.
sfc_models.register_standard_logs('output', __file__)

Parameters.TraceStep = 1
builder_PC = PC(country_code='C1', use_book_exogenous=True)

model = builder_PC.build_model()
Parameters.SolveInitialEquilibrium = True
# Generate the file name using an operating system independent tool - os.path.join
model.main()


model.TimeSeriesCutoff = 40

time = model.GetTimeSeries('t')
k = model.GetTimeSeries('k')
Y_PC = model.GetTimeSeries('GOOD__SUP_GOOD')
r = model.GetTimeSeries('DEP__r')
Y_d = model.GetTimeSeries('HH__AfterTax')
FB = model.GetTimeSeries('TRE__FISCBAL')
PB = model.GetTimeSeries('TRE__PRIM_BAL')
w_dep = model.GetTimeSeries('HH__WGT_DEP')
w_mon = model.GetTimeSeries('HH__WGT_MON')

# Quick2DPlot(time, r, 'Interest Rate - Model PC')
# Quick2DPlot(time, Y_PC, 'Output (Y) - Model PC')
# Quick2DPlot(time, Y_d, 'Household Disposable Income - Model PC')
# Quick2DPlot(time, FB, 'Fiscal Balance - Model PC')
# Quick2DPlot(time, PB, 'Primary Fiscal Balance')

Quick2DPlot(k[5:15], w_mon[5:15], 'Money (Currency) Weighting')
Quick2DPlot(k[5:15], r[5:15], 'Interest Rate')
Quick2DPlot(k[5:15], w_dep[5:15], 'Deposit (Treasury Bill) Weighting')
Quick2DPlot(k[5:15], Y_PC[5:15], 'Output')


