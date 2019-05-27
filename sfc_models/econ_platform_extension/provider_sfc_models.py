"""
This module creates a Provider for the econ_platform package. It allows you to bring sfc_models output
into the econ_platform database. Obviously only useful if you heve econ_platform installed.

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

import econ_platform_core

class SFCModelProvider(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super().__init__(name='sfc_models')

