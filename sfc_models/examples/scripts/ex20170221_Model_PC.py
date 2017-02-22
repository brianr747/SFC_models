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


import os
from sfc_models.gl_book.chapter4 import PC
from sfc_models.examples.Quick2DPlot import Quick2DPlot


builder_PC = PC(country_code='C1', use_book_exogenous=True)

model = builder_PC.build_model()

model.main(base_file_name=os.path.join('output', 'ex20170221_PC'))


model.TimeSeriesCutoff = 40
# The data at the first time point are initial conditions, which may be incoherent.
# The next line tells the model to suppress those points.
model.TimeSeriesSupressTimeZero = True

time = model.GetTimeSeries('t')
Y_PC = model.GetTimeSeries('GOOD_SUP_GOOD')
r = model.GetTimeSeries('DEP_r')
Y_d = model.GetTimeSeries('HH_AfterTax')
FB = model.GetTimeSeries('TRE_FISCBAL')

Quick2DPlot(time, Y_PC, 'Output (Y) - Model PC')
Quick2DPlot(time, r, 'Interest Rate - Model PC')
Quick2DPlot(time, Y_d, 'Household Disposable Income - Model PC')
# The fiscal balance is incorrect at k=1, as well as k=0 (already suppressed).
Quick2DPlot(time[1:], FB[1:], 'Fiscal Balance - Model PC')


