"""
objects.py

"Convenience module" that imports the high level objects into the name space.

Users can use:

from sfc_models.objects import *

to load up the standard objects.

This could have been done inside sfc_models, but that seemed somewhat riskier (and currently
does not work, as circular imports are created).

Note that syntax like "from sfc_models.objects import *" is frowned upon as being dangerous.
I have just added this in to avoid bloated import statements in example code.


Copyright/License
-----------------

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



from sfc_models.examples.install_examples import install_examples
from sfc_models.utils import register_standard_logs, LogicError
from sfc_models.models import Model, Country, Region
from sfc_models.sector import Market
from sfc_models.sector_definitions import Household, HouseholdWithExpectations, ConsolidatedGovernment
from sfc_models.sector_definitions import Treasury, CentralBank, TaxFlow
from sfc_models.sector_definitions import GoldStandardCentralBank, GoldStandardGovernment
from sfc_models.sector_definitions import FixedMarginBusiness, FixedMarginBusinessMultiOutput
from sfc_models.sector_definitions import MoneyMarket, DepositMarket
from sfc_models.external import ExchangeRates, ForexTransations, ExternalSector