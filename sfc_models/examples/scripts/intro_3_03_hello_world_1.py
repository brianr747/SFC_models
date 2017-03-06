"""
intro_3_03_hello_world_1.py

Example code from Section 3.3 of "Introduction to SFC Models Using Python."

This example does not create a useful model, but it and following examples demonstrate
how models are built up by examining the log file.

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

# This next line looks bizarre, but is needed for backwards compatibility with Python 2.7.
from __future__ import print_function

import sfc_models
from sfc_models.models import Model

print('*Starting up logging*')
# Log files are based on name of this module, which is given by: __file__
sfc_models.register_standard_logs(output_dir='output',
                                  base_file_name=__file__)
print('*Build Model*')
mod = Model()
print('*Running main()*')
print('*(This will cause a warning...)*')
mod.main()
