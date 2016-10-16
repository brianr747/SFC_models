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

model_list = {
    'TEST': """# Test model for internal testing purposes...
t = 1.0""",
    'SIM': """# Model SIM - Simplest model with government money.
# Chapter 3 of [G&L 2012], pages 91-92.
#
# [G&L 2012] "Monetary Economics: An Integrated Approach to credit, Money, Income, Production
# and Wealth; Second Edition", by Wynne Godley and Marc Lavoie, Palgrave Macmillan, 2012.
# ISBN 978-0-230-30184-9
Cs = Cd                             # (3.1)
Gs = Gd                             # (3.2)
Ts = Td                             # (3.3)
Ns = Nd                             # (3,4)
YD = W*Nd - Ts                      # (3.5)  [Need to specify Nd instead of N]
Td = theta*W*Ns                     # (3.6)
Cd = alpha1*YD + alpha2*LAG_Hh      # (3.7)
# -----------------------
# Where - lagged variables
LAG_Hh = Hh(k-1)                     # Def'n
LAG_Hs = Hs(k-1)                     # Def'n
# ---------------------------------------------
# Need to clean up the following
Hs = LAG_Hs + Gd - Td                # (3.8) Was: delta_Hs = Hs - LAG_Hs = Gd - Td
                                     # Government-supplied money
                                     # Note that there is no dependence upon Hs;
                                     # redundant equation.
Hh = LAG_Hh + YD - Cd                # (3.9) Was: delta_Hh = Hh- LAG_Hs = YD - Cd
#-----------------------------------------------
Y = Cs + Gs                          # (3.10)
Nd = Y/W                             # (3.11)
# Params
alpha1 = 0.6
alpha2 = 0.4
theta = 0.2
W = 1.0
# Initial conditions
Hh(0) = 80.0
Hs(0) = 80.0
# Exogenous variable
Gd = [20., ] * 35 + [25., ] * 66
# Length of simulation
MaxTime = 100""",
}


def get_models():
    kys = list(model_list.keys())
    kys.remove('TEST')
    out = ''
    for k in kys:
        description = model_list[k].split('\n')[0]
        out += '[%s] %s\n' % (k, description)
    return out


def build_model(model_name):
    try:
        eqn = model_list[model_name]
    except KeyError:
        raise ValueError('Unknown model - "' + model_name + '"; run get_models() for list')
    obj = IterativeMachineGenerator(eqn)
    return obj
