"""
ex20170209_SIMEX1.py

Build Model SIMEX from Godley & Lavoie (Chapter 3, section 3.7.1.

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
from sfc_models.gl_book.chapter3 import SIMEX1, SIM
from sfc_models.examples.Quick2DPlot import Quick2DPlot


builder_SIMEX = SIMEX1(country_code='C1', use_book_exogenous=True)

model = builder_SIMEX.build_model()

model.main(base_file_name=os.path.join('output', 'ex20170209_SIMEX1'))

builder_SIM = SIM(country_code='C1', use_book_exogenous=True)

model_SIM = builder_SIM.build_model()
model_SIM.main(base_file_name=os.path.join('output', 'ex20170209_SIM'))

model.TimeSeriesCutoff = 20
model_SIM.TimeSeriesCutoff = 20
time = model.GetTimeSeries('k')
Y_SIMEX = model.GetTimeSeries('GOOD_SUP_GOOD')
Y_SIM = model_SIM.GetTimeSeries('GOOD_SUP_GOOD')
income = model.GetTimeSeries('HH_AfterTax')
expected_income =  model.GetTimeSeries('HH_EXP_AfterTax')
F_SIMEX = model.GetTimeSeries('HH_F')
F_SIM = model_SIM.GetTimeSeries('HH_F')


Quick2DPlot(time, Y_SIMEX, 'Output (Y) - Model SIMEX')

q = Quick2DPlot([time, time], [expected_income, income], 'Household Income in Model SIMEX', run_now=False,
                filename='SIMEX1_output.png')
q.Legend = ['Expected', 'Realised']
q.DoPlot()

q = Quick2DPlot([time, time], [Y_SIMEX, Y_SIM], 'Output (Y)', run_now=False)
q.Legend = ['Model SIMEX', 'Model SIM']
q.DoPlot()

q = Quick2DPlot([time, time], [F_SIMEX, F_SIM], 'Household Financial Assets', run_now=False)
q.Legend = ['Model SIMEX', 'Model SIM']
q.DoPlot()