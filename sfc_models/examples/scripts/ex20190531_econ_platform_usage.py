"""
This is an example of how to run sfc_models from within econ_platform.
(econ_platform: available at: https://github.com/brianr747/platform)

It assumes that the sfc_models extension has been installed into econ_platform, and the model_sim.py
model builder file is available in the correct directory. (It is included in the source repository.)

See the econ_platform_extension directory (package) to see the installation script.

Note that the installation is not heavily documented at the time of writing, since the extension handling may
be heavily overhauled. As such, the documentation would likely be out of date rapidly. It will require
some Python programming knowledge to do the installation now.

- The econ_platform package is only for Python 3.7+. So even though sfc_models works on earlier Python versions,
you will need to update for econ_platform to work.
- For this script to work, econ_platform has to be on the PYTHONPATH.
- The time axis for sfc_models consists of real numbers (which are standing for integers). The sqlite database
handles such time series, but not all of them will.

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


# Import everything, and start up econ_platform. (The "start" script does an initialisation step; if you
# just import econ_platform, you need to explicitly call the init_package() function.
from econ_platform.start import *

# This is it!
x = fetch('SFC@SIM|DEFICIT', database='TMP')
# This returns a time series (pandas.Series) to the variable x.
# 1) 'SFC@SIM|DEFICIT' is the variable ticker.
# 2) SFC = go to the SFCModels data provider. (Other providers are data providers like FRED or DB.nomics).
# 3) SIM|DEFICIT: the ticker structure for the SFCModels provider is {model}|{time series}.
#    SIM -> runs the model in the file "model_sim.py". Note that model names are converted to lower case,
#    so 'sim|DEFICIT' would give the same result.
#    DEFICIT: variable name from the model. (Case sensitive!)
#  Note: fetch() is dyamic.
# (a) It goes to the database if the series exists, and is considered up-to-date.
# (b) Otherwise, it goes to the provider (SFC). In this case, model SIM will be run, and all series will
# be pushed onto the database. The series that is requested will be returned. However, other fetches for other
# series will be returned from the database, at least until they are considered out-of-date, at which point the
# model will be re-run.
# (Management of when to refresh series is not yet settled for sfc_models.)

# Finally, plot the series.
quick_plot(x)