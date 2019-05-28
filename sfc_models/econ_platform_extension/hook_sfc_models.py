"""
Python script that hooks in the sfc_models code (found in the sfc_models package, must be installed).

This file is copied into the econ_platform.extensions directory from sfc_models.

To work, sfc_models must be on the path.

Copyright 2019 Brian Romanchuk

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

import econ_platform_core
import sfc_models.econ_platform_extension.provider_sfc_models


extension_name = 'Data provided by sfc_models'

def main():
    """
    Insert the provider into the platform list
    :return:
    """
    obj = sfc_models.econ_platform_extension.provider_sfc_models.SFCModelProvider()
    econ_platform_core.Providers.AddProvider(obj)