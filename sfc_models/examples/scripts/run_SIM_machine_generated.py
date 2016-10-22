"""
run_SIM_machine_generated.py

Script to generate model SIM from [G&L 2012] from text equation specification.
"""

import sfc_models.iterative_machine_generator as generator
from sfc_models.examples.Quick2DPlot import Quick2DPlot

filename = 'SIM_model.py'

eqn = """# Model SIM - Simplest model with government money.
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
MaxTime = 100
"""

obj = generator.IterativeMachineGenerator(eqn)
obj.main(filename)

# Can only import now...
import SIM_model
obj = SIM_model.SFCModel()
obj.main()

# Lop off t = 0 because it represents hard-coded initial conditions
Quick2DPlot(obj.t[1:], obj.Y[1:], 'Y - National Production')
Quick2DPlot(obj.t[1:], obj.Y[1:], 'G - Government Consumption')
print("Validate that Hh = Hs")
Quick2DPlot(obj.t[1:], obj.Hh[1:], 'Hh - Household Money Holdings')
Quick2DPlot(obj.t[1:], obj.Hs[1:], 'Hs - Money Supplied by the Gummint')



