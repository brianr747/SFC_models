"""
equation_solver.py

Take in a system of equations, and solve.

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

# We want to be able to have access to math functions, like sqrt.
from math import *
import warnings

import sfc_models.utils as utils
from sfc_models.utils import Logger as Logger

class ConvergenceError(ValueError):
    pass

class EquationSolver(object):
    def __init__(self, equation_string='', run_equation_reduction=True):
        self.EquationString = equation_string
        self.RunEquationReduction = run_equation_reduction
        self.Parser = utils.EquationParser()
        self.VariableList = []
        self.TimeSeries = {}
        self.MaxIterations = 400

        if len(equation_string) > 0:
            self.ParseString(equation_string)

    def ParseString(self, equation_string):
        """
        Read in a mutliline string to populate variable and equation lists.

        :param equation_string: str
        :return: str
        """
        self.EquationString = equation_string
        parser = utils.EquationParser()
        msg = parser.ParseString(equation_string)
        parser.ValidateInputs()
        if self.RunEquationReduction:
            parser.EquationReduction()
        self.Parser = parser
        if len(msg) > 0:
            warnings.warn('Could not parse some sections of input. Examine ParseString() output to view issues.',
                          SyntaxWarning)
        return msg

    def ExtractVariableList(self):
        self.VariableList = []
        endo = [x[0] for x in self.Parser.Endogenous]
        self.VariableList.extend(endo)
        lagged = [x[0] for x in self.Parser.Lagged]
        self.VariableList.extend(lagged)
        exo = [x[0] for x in self.Parser.Exogenous]
        self.VariableList.extend(exo)
        deco = [x[0] for x in self.Parser.Decoration]
        self.VariableList.extend(deco)
        # Sort the variables
        self.VariableList.sort()

    def SetInitialConditions(self):
        variables = {}
        variables['k'] = list(range(0, self.Parser.MaxTime+1))
        # First pass: include exogenous
        for var in self.VariableList:
            if var in self.Parser.InitialConditions:
                try:
                    ic = eval(self.Parser.InitialConditions[var], globals())
                    ic = float(ic)
                except:
                    raise ValueError('Cannot parse initial conditions for: ' + var)
            else:
                ic = 0.
            variables[var] = [ic, ]
        # Second pass: overwrite exogenous
        for var, eqn in self.Parser.Exogenous:
            try:
                val = eval(eqn, globals())
            except:
                raise ValueError('Cannot parse exogenous variable: ' + var)
            if type(val) is float:
                val = [val, ] * (self.Parser.MaxTime+1)
            try:
                val = list(val)
            except: # pragma: no cover     I cannot trigger this error, but I will leave in place
                raise ValueError('Initial condition must be of the list type: ' + var)
            if len(val) < self.Parser.MaxTime+1:
                raise ValueError('Initial condition list too short: ' + var)
            variables[var] = val[0:self.Parser.MaxTime+1]
        self.TimeSeries = variables

    def SolveStep(self, step):
        # Set up starting condition (for step)
        initial = {}
        Logger('Step: {0}'.format(step))
        # The exogenous and lagged variables are always fixed
        for var, dummy in self.Parser.Exogenous:
            initial[var] = self.TimeSeries[var][step]
        for lag_var, original_var in self.Parser.Lagged:
            initial[lag_var] = self.TimeSeries[original_var][step-1]
        # This is an initial guess
        for var, dummy in self.Parser.Endogenous:
            initial[var] = self.TimeSeries[var][step-1]
        # NOTE:
        # We are missing the decorative variables, but they have no effect on the solution
        relative_error = 1.
        err_toler = float(self.Parser.Err_Tolerance)
        num_tries = 0
        while relative_error > err_toler:
            # Need to create a copy of the dictionary; saying new_value = initial means that they are
            # the same object.
            new_value = dict()
            for key, val in initial.items():
                new_value[key] = val
            relative_error = 0.
            for var, eqn in self.Parser.Endogenous:
                new_value[var] = eval(eqn, globals(), initial)
                difference = abs(new_value[var] - initial[var])
                if difference < 1e-3:
                    relative_error += difference
                else:
                    # Scale by variable size if large
                    relative_error += difference/(max(abs(new_value[var]), abs(initial[var])))
            # Use new_value as the initial at the next step
            initial = new_value
            num_tries += 1
            if num_tries > self.MaxIterations:
                raise ConvergenceError('Equations do not converge - step {0}'.format(step))
        # Then: append values to the time series
        varlist = [x[0] for x in self.Parser.Endogenous] + [x[0] for x in self.Parser.Lagged]
        for var in varlist:
            assert(len(self.TimeSeries[var]) == step)
            self.TimeSeries[var].append(initial[var])
        # Finally: augment with decorative variables
        # This is complicated as decorative variables may depend upon other decorative variables
        # Create a holding variable that lists the equations, and keep iterating through the list
        vars_to_compute = []
        for var, eqn in self.Parser.Decoration:
            vars_to_compute.append((var, eqn))
        while len(vars_to_compute) > 0:
            failed = []
            for var, eqn in vars_to_compute:
                assert (len(self.TimeSeries[var]) == step)
                try:
                    val = eval(eqn, globals(), initial)
                    initial[var] = val
                    self.TimeSeries[var].append(val)
                except NameError:
                    failed.append((var, eqn))
            # If we failed on every single decoration variable, something is wrong.
            if len(failed) == len(vars_to_compute):
                # NOTE: We should not get here; it manes that the decoration variables are
                # created incorrectly. Leave check to break infinite loops.
                raise ValueError('Cannot solve decoration equations! <?>')
            vars_to_compute = failed

    def SolveEquation(self):
        if len(self.VariableList) == 0:
            self.ExtractVariableList()
        self.SetInitialConditions()
        for step in range(1, self.Parser.MaxTime+1):
            try:
                self.SolveStep(step)
            except ConvergenceError:
                # Truncate so all time series are same length
                for var in self.TimeSeries:
                    self.TimeSeries[var] = self.TimeSeries[var][0:step]
                raise

    def GenerateCSVtext(self):
        """
        Convert time series data into a text string that can be written to a csv. (Tab-delimited file.)
        :return: str
        """
        vars = tuple(self.TimeSeries.keys())
        if len(vars) < 1:
            return ''
        out = '\t'.join(vars) + '\n'
        # We assume that all time series are the same length.
        L = len(self.TimeSeries[vars[0]])
        for i in range(0,L):
            row = []
            for v in vars:
                row.append("{0}".format(self.TimeSeries[v][i]))
            out += '\t'.join(row) + '\n'
        return out









