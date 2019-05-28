"""
This module creates a Provider for the econ_platform package. It allows you to bring sfc_models output
into the econ_platform database. Obviously only useful if you heve econ_platform installed.

Since this is in development, not much documentation yet. When it works, I will add an example script.

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

import os
import sys
import importlib

import econ_platform_core

class SFCModelProvider(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super().__init__(name='sfc_models', default_code='SFC')
        self.Directory = None

    def fetch(self, series_meta):
        """
        Run model in response to a fetch.

        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        if self.Directory is None:
            try:
                self.Directory = econ_platform_core.PlatformConfiguration['sfc_models']['directory']
            except KeyError:
                self.Directory = os.path.dirname(__file__)
                print('[sfc_models] directory is not set in config file')
                print('Using directory in sfc_models: {0}'.format(self.Directory))
        try:
            model, series = series_meta.ticker_fetch.split('|', 1)
        except:
            raise econ_platform_core.PlatformError('sfc_models tickers are of the form "<model>|<series>"')
        # Put the directory on the path.
        # Alternatively, could do the following:
        # (From https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path)
        # import importlib.util
        # spec = importlib.util.spec_from_file_location(model, os.path.join(self.Directory, model+'.py'))
        # module = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(module)
        if self.Directory not in sys.path:
            sys.path.append(self.Directory)
        try:
            module = importlib.import_module(model)
        except ImportError:
            raise econ_platform_core.PlatformError('Python module {0} does not exist in {1}'.format(
                model, self.Directory
            )) from None




        raise NotImplementedError()
        try:
            ser = self.TableSeries[str(series_meta.ticker_full)]
            meta = self.TableMeta[str(series_meta.ticker_full)]
        except KeyError:
            raise econ_platform_core.entity_and_errors.TickerNotFoundError('{0} was not found'.format(str(series_meta.ticker_full))) \
                from None
        return ser, meta

