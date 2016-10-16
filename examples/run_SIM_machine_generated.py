from plot_for_examples import Quick2DPlot

import sfc_models.iterative_machine_generator as generator

filename = 'SIM_model.py'

eqn = """
#--------------------------------------------------------------
# Equations to generate model SIM
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
# Initial condition
Hh(0) = 80.
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
Quick2DPlot(obj.t[1:], obj.Y[1:])
Quick2DPlot(obj.t[1:], obj.Hh[1:])



