"""
Generate the SIM model using machine-generated code

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

from sfc_models.iterative_machine_generator import IterativeMachineGenerator


def build_model():
    eqn = """
    # From g&L
    Cs = Cd                             # (3.1)
    Gs = Gd                             # (3.2)
    Ts = Td                             # (3.3)
    Ns = Nd                             # (3,4)
    YD = W*Nd - Ts                      # (3.5)  [Need to specify Nd instead of N]
    Td = theta*W*Ns                     # (3.6)
    Cd = alpha1*YD + alpha2*LAG_Hh      # (3.7)
    # Where - lagged variable
    LAG_Hh = Hh(t-1)                     # Def'n
    # Need to clean up the following
    Hh = LAG_Hh + YD - Cd                # (3.9)
    Y = Cs + Gs                          # (3.10)
    Nd = Y/W                             # (3.11)
    # Params
    alpha1 = 0.6
    alpha2 = 0.4
    theta = 0.2
    W = 1
    # Exogenous variable
    Gd = [20., ] * 5 + [25., ] * 20
    # Length of simulation
    MaxTime = 20
    """
    obj = IterativeMachineGenerator(eqn)
    return obj

