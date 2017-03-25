"""
intro_3_05_variable_names_2.py

Example code from Section 3.5 of <Introduction to SFC Models Using Python.>

Demonstration how variable names are built up.

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

# Imports
# This next line looks bizarre, but is needed for backwards compatibility with Python 2.7.
from __future__ import print_function

import sfc_models
from sfc_models.models import Model, Country
from sfc_models.sector import Sector

mod = Model()
can = Country(mod, 'CA', 'Canada')
# has_F=False: turns off creation of financial asset variables.
sector_yy = Sector(can, 'YY', has_F=False)
sector_yy.AddVariable('W', 'Variable W <constant>', '4.0')
sector_yy.AddVariable('Y', 'Variable Y - depends on local variable', '2*W')
# Only the next two lines have changed: put sector_xx into a another Country
us = Country(mod, 'US') 
sector_xx = Sector(us, 'XX', has_F=False)
variable_name = sector_yy.GetVariableName('Y')
print("Name of variable before binding:", variable_name)
# format: inserts variable_name where {0} is
eqn = '{0} + 2.0'.format(variable_name)
sector_xx.AddVariable('X', 'Variable x; depends on other sector', eqn)
# Bind the model; solve
eqns = mod.main()
print(eqns)

print('Variable name after binding:', sector_yy.GetVariableName('Y'))



