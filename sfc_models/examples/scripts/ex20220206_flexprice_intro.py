"""
Initial example of how to incorporate flexprice variables into a model.

Warning: this script is working on a development build, and the code syntax could
change.

This code will not work on the version of sfc_models installed by pip, at least until the
production branch is changed.

See discussion on my Substack post:
https://bondeconomics.substack.com/p/new-sfc-models-feature-flexprice


Short description: create a system with just global variables (for simplicity).

The global variables rely on a variable called "price", and there is a variable "balance"
that is supply-demand, and if the "price" is not "correct", balance is non-zero.

Can run in two modes:
(1) Price is an exogenous constant, at the wrong value, so the balance is non-zero.
(2) Add the code to have the EquationSolver search for the value of price that drives balance
to zero.
"""

# This next line looks bizarre, but is needed for backwards compatibility with Python 2.7.
from __future__ import print_function

import sfc_models
from sfc_models.models import Model

print('*Starting up logging*')
# Log files are based on name of this module, which is given by: __file__
sfc_models.register_standard_logs(output_dir='output',
                                  base_file_name=__file__)
print('*Build Model*')
mod = Model()
# For simplicity, all variables are global.
mod.AddGlobalEquation('supply', 'supply function', 'sqrt(price)')
mod.AddGlobalEquation('demand', 'demand function', '1/price')
mod.AddGlobalEquation('balance', 'supply-demand balance', 'supply-demand')
# Must specify price as exogenous. Note that the is_exogenous parameter was
# added after version 1.0, so this command will not work on the production version of
# sfc_models
# The initial price = 4., which is the "wrong" value to balance supply demand
# The user could experiment with manually changing this, and see what happens.
mod.AddGlobalEquation('price', 'Da price', [4.]*20, is_exogenous=True)
mod.MaxTime=10

# If anyone is still running Python 2.X, this probably needs to be raw_input()
if input('Run with flexprice solver (y/n)? > ') == 'n':
    print("running without flexprice!")
else:
    # Run the Flexprice solver.
    # This step tells the solver to force "balance" to zero via moving "price"
    print('Running with flexprice!')
    print('Note that we are not solving initial conditions, so initial balance is non-zero.')
    mod.EquationSolver.FlexPrice['price'] = 'balance'
mod.main()
