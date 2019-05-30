"""
Example of how to build a model that works in econ_platform.



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

from sfc_models.objects import *

def build_model(scenario):
    """
    Build Model SIM. Parameter scenario chooses a scenario to run.

    :param scenario: str
    :return:
    """
    if scenario == '':
        government_consumption = [15.,]*5 + [20.,]* 50
    else:
        raise ValueError('Unknown scenario for model SIM: {0}'.format(scenario))
    mod = Model()
    country = Country(mod, 'CO')
    Household(country, 'HH')
    ConsolidatedGovernment(country, 'GOV')
    FixedMarginBusiness(country, 'BUS')
    Market(country, 'GOOD')
    Market(country, 'LAB')
    TaxFlow(country, 'TAX', taxrate=.2)
    mod.AddExogenous('GOV', 'DEM_GOOD', government_consumption)
    mod.AddGlobalEquation('DEBT_GDP', 'DEBT-TO-GDP RATIO', '-100.*GOV__F/BUS__SUP_GOOD')
    mod.AddGlobalEquation('DEFICIT', 'DEFICIT-TO-GDP RATIO', '-100.*GOV__INC/BUS__SUP_GOOD')
    mod.EquationSolver.MaxTime = 40
    # print(mod.EquationSolver.ParameterErrorTolerance)
    # mod.EquationSolver.ParameterErrorTolerance = 1e-8
    mod.EquationSolver.ParameterSolveInitialSteadyState = True
    return mod


if __name__ == '__main__':
    mod = build_model('')
    mod.main()