"""
This module creates a Provider for the econ_platform package. It allows you to bring sfc_models output
into the econ_platform database. Obviously only useful if you heve econ_platform installed.

Since this is in development, not much documentation yet. When it works, I will add an example script.

Unlike sfc_models, not compatible with Python versions before 3.7.

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
import importlib
import pandas

import sfc_models.model_runner

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
            model, series = str(series_meta.ticker_query).split('|', 1)
        except:
            raise econ_platform_core.PlatformError('sfc_models tickers are of the form "<model>|<series>"')
        model_runner = sfc_models.model_runner.ModelRunner()
        model_runner.Directory = self.Directory
        # Preface 'model_' in front of the model name. So "sim" = "model_sim.py"
        model_runner.RunModel('model_' + model, '')
        containers = (model_runner.Model.EquationSolver.TimeSeries,
                      model_runner.Model.EquationSolver.TimeSeriesStepTrace,
                      model_runner.Model.EquationSolver.TimeSeriesInitialSteadyState)
        prefixes = ('', 'D>', '0>')
        groups = ('Solution', 'Debug Step', 'Initial Conditions')
        self.TableSeries = {}
        self.TableWasFetched = True
        for container, prefix, group_name in zip(containers, prefixes, groups):
            try:
                t = container['t']
            except KeyError:
                continue
            for sername in container.keys():
                valz = container[sername]
                decorated_name = prefix + sername
                ser = pandas.Series(valz)
                ser.index = t
                ser.name = decorated_name
                self.TableSeries[decorated_name] = ser
                meta = econ_platform_core.SeriesMetadata()
                meta.ticker_query = f'{model}|{decorated_name}'
                meta.series_provider_code = self.ProviderCode
                meta.ticker_full = econ_platform_core.tickers.create_ticker_full(meta.series_provider_code,
                                                                             meta.ticker_query)
                try:
                    eqn = model_runner.Model.FinalEquationBlock[sername]
                    eqn_str = '{0} = {1}'.format(sername, eqn.GetRightHandSide())
                    desc = eqn.Description
                    meta.series_name = f'{sername} in {group_name}'
                    meta.series_description = f'{sername} in {group_name} for SFC Model {model}'
                    meta.ProviderMetadata['Equation'] = eqn_str
                    meta.ProviderMetadata['Description'] = eqn.Description
                except KeyError:
                    pass
                self.TableMeta[decorated_name] = meta
        try:
            ser = self.TableSeries[str(series_meta.ticker_full)]
            meta = self.TableMeta[str(series_meta.ticker_full)]
        except KeyError:
            raise econ_platform_core.entity_and_errors.TickerNotFoundError('{0} was not found'.format(str(series_meta.ticker_full))) \
                from None
        return ser, meta

