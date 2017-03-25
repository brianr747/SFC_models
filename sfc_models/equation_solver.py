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
import copy

import sfc_models.equation_parser
from sfc_models.utils import Logger, TimeSeriesHolder
from sfc_models import Parameters as Parameters


class ConvergenceError(ValueError):
    pass


class NoEquilibriumError(ValueError):
    pass


class EquationSolver(object):
    """
    EquationSolver - Object to solve equations.

    """

    def __init__(self, equation_string='', run_equation_reduction=True):
        self.TraceStep = None
        self.EquationString = equation_string
        self.RunEquationReduction = run_equation_reduction
        self.Parser = sfc_models.equation_parser.EquationParser()
        self.VariableList = []
        self.TimeSeries = TimeSeriesHolder('k')
        self.TimeSeriesInitialSteadyState = TimeSeriesHolder('k')
        self.TimeSeriesStepTrace = TimeSeriesHolder('iteration')
        self.MaxIterations = 400
        self.MaxTime = None
        self.Functions = {}
        self.ParameterErrorTolerance = None
        self.ParameterSolveInitialSteadyState = False
        self.ParameterInitialSteadyStateMaxTime = 200
        self.ParameterInitialSteadyStateErrorToler = 1e-4
        self.ParameterInitialSteadyStateExcludedVariables = ['t']
        self.ParameterInitialSteadyStateStepError = 1e-6

        if len(equation_string) > 0:
            self.ParseString(equation_string)

    def ParseString(self, equation_string):
        """
        Read in a mutliline string to populate variable and equation lists.

        :param equation_string: str
        :return: str
        """
        self.EquationString = equation_string
        parser = sfc_models.equation_parser.EquationParser()
        msg = parser.ParseString(equation_string)
        parser.ValidateInputs()
        if self.RunEquationReduction:
            parser.EquationReduction()
        self.Parser = parser
        if self.MaxTime is not None:
            self.Parser.MaxTime = self.MaxTime
        if len(msg) > 0:
            warnings.warn('Could not parse some sections of input. Examine ParseString() output to view issues.',
                          SyntaxWarning)
        return msg

    def AddFunction(self, function_name, function_object):
        """
        Add a function with the given name so that it can be used when solving equations.
        :param function_name: str
        :param function_object: function
        :return: None
        """
        self.Functions[function_name] = function_object

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
        Logger('Set Initial Conditions')
        variables = TimeSeriesHolder('k')
        # variables['k'] = list(range(0, self.Parser.MaxTime+1))
        time_zero_constants = dict()
        # First pass: include exogenous
        for var in self.VariableList:
            if var in self.Parser.InitialConditions:
                try:
                    ic = eval(self.Parser.InitialConditions[var], globals())
                    ic = float(ic)
                    time_zero_constants[var] = ic
                except:
                    raise ValueError('Cannot parse initial conditions for: ' + var)
            else:
                ic = 0.
            variables[var] = [ic, ]
        if 'k' not in variables:
            k_series = list(range(0, self.Parser.MaxTime + 1))
            k_series = [float(x) for x in k_series]
            self.Parser.Exogenous.append(('k', k_series))

        # Second pass: overwrite exogenous
        for var, eqn in self.Parser.Exogenous:
            if type(eqn) == str:
                try:
                    val = eval(eqn, globals())
                except:
                    raise ValueError('Cannot parse exogenous variable: ' + var)
                if type(val) is float:
                    val = [val, ] * (self.Parser.MaxTime + 1)
                try:
                    val = list(val)
                except:  # pragma: no cover     I cannot trigger this error, but I will leave in place
                    raise ValueError('Exogenous must be of the list type: ' + var)
            else:
                if type(eqn) == float:
                    val = [eqn, ] * (self.Parser.MaxTime + 1)
                else:
                    try:
                        val = list(eqn)
                    except:  # pragma: no cover   Hard time figuring how to trigger this
                        raise ValueError('Initial conditions must be directly convertible to a list: ' + var)
            if len(val) < self.Parser.MaxTime + 1:
                raise ValueError('Exogenous variable list too short: ' + var)
            variables[var] = val[0:self.Parser.MaxTime + 1]
            time_zero_constants[var] = val[0]
        # Third pass: clean up constant endogenous
        changes_made = True
        while changes_made:
            changes_made = False
            for var, eqn in self.Parser.Endogenous:
                # noinspection PyBroadException
                if (var in time_zero_constants.keys()) or (var in self.Parser.InitialConditions.keys()):
                    continue
                try:
                    val = eval(eqn, globals(), time_zero_constants)
                    if type(val) is int:
                        val = float(val)
                    if type(val) is float:
                        variables[var] = [val, ]
                        time_zero_constants[var] = val
                        changes_made = True
                except:
                    # If not a constant, we will blow up. We step over any problems.
                    continue
        # Fourth pass: constant decoration
        did_any = True
        while did_any:
            did_any = False
            for var, eqn in self.Parser.Decoration:
                if var in time_zero_constants:
                    continue
                # noinspection PyBroadException
                try:
                    val = eval(eqn, globals(), time_zero_constants)
                except:
                    # We do not care what the exception is here; it is probably
                    # a NameError. We just step over it.
                    continue
                did_any = True
                time_zero_constants[var] = val
                variables[var] = [val, ]
        self.TimeSeries = variables

    def CalculateInitialSteadyState(self):
        """
        Attempt to calculate initial conditions. Very little guarantee
        the system will converge.

        Methodology:
        [1] Create a (deep) copy of this solver object.
        [2] Set the exogenous variables to be constants, equal to their
             k = 0 value.
        [3] Set k to be [-T, T-1, ... 0]
        [3] Solve the copied system normally.
            Number of time steps = Parameters.InitialEquilbriumMaxTime
        [4] If variables are essentially constant in the last time point,
            we treat that as equilibrium.
            If they are not constant, throw a NoEquilibriumError.
            Tolerance for error is Parameters.InitialEquilibriumErrorTolerance
            The algorithm ignores variables listed in
            Parameters.InitialEquilibriumExcludedVariables
        [5] Copy equilibrium values into the initial values (endogenous,
            decoration, lagged.)

        Returns the new solver for inspection.

        :return: EquationSolver
        """
        # Create a deep copy of the solver object.
        # A "deep copy" means that all data members are copied,
        # so that changes to the copy do not affect this object!
        Logger('Starting to calculate initial steady state')
        new_solver = self._GetCopy()
        # DO not allow step tracing in in the initial steady state;
        # as we will end up with two traces in the same file.
        # The user can run the system normally to examine convergence errors.
        new_solver.TraceStep = None
        T = self.ParameterInitialSteadyStateMaxTime
        new_solver.Parser.MaxTime = T
        new_solver.MaxIterations = 1000
        new_solver.Parser.Err_Tolerance = self.ParameterInitialSteadyStateErrorToler
        # Fix exogenous to be constants
        for var, dummy in new_solver.Parser.Exogenous:
            val = [new_solver.TimeSeries[var][0], ] * (T + 1)
            new_solver.TimeSeries[var] = val
        # Force 'k' to be negative.
        time_axis = list(range(0, T + 1))
        time_axis = [-float(x) for x in time_axis]
        time_axis.reverse()
        new_solver.TimeSeries['k'] = time_axis
        try:
            for step in range(1, T + 1):
                new_solver.SolveStep(step)
        except ConvergenceError:
            raise ValueError('No convergence in initial equilibrium')
        except:
            raise
        finally:
            self.TimeSeriesInitialSteadyState = new_solver.TimeSeries
            Logger(new_solver.GenerateCSVtext(), 'steadystate_0')
        # Now: look at which variables are not constant.
        bad_variables = []
        excluded = ['k', ] + self.ParameterInitialSteadyStateExcludedVariables
        for var in self.TimeSeries.keys():
            if var in excluded:
                continue
            TS = new_solver.TimeSeries[var]
            lastval = TS[-1]
            prev = TS[-2]
            bad = False
            if abs(lastval-prev) > self.ParameterInitialSteadyStateErrorToler:
                if abs(lastval) < 1e-4:
                    if not abs(prev) < 1e-4:
                        bad = True
                else:
                    err = abs(lastval - prev) / lastval
                    if err > self.ParameterInitialSteadyStateErrorToler:
                        bad = True
            if bad:
                bad_variables.append(var)
            else:
                self.TimeSeries[var][0] = lastval
        if len(bad_variables) > 0:
            Logger('Variables that did not converge in initial equilibrium')
            for var in bad_variables:
                Logger(var)
            raise NoEquilibriumError('Variables did not converge')
        return new_solver

    def _GetCopy(self):
        """
        Get a (deep) copy of this object. This copy may be modified without
        affecting this object.
        :return: EquationSolver
        """
        return copy.deepcopy(self)

    def SolveStep(self, step):
        """
        Solve a step. (Assumed to be called in order.)
        :param step: int
        :return:
        """
        is_trace_step = step == self.TraceStep
        if is_trace_step:
            Logger('Starting convergence tracing.', log='step')
            Logger('Step {0}'.format(step), log='step')
            self.TimeSeriesStepTrace = TimeSeriesHolder('iteration')
            self.TimeSeriesStepTrace['iteration'] = []
            self.TimeSeriesStepTrace['iteration_error'] = []
            Logger("""
        Values at beginning of step. (Only includes variables that are solved within
        iteration. Decorative variables calculated later).""", log='step')
        try:
            self._SolveStep(step, is_trace_step)
        finally:
            if is_trace_step:
                Logger(self.TimeSeriesStepTrace.GenerateCSVtext(), log='step')

    def _SolveStep(self, step, is_trace_step):
        # Set up starting condition (for step)
        initial = {}
        # Probably could just do a shallow copy...
        for key, value in self.Functions.items():
            initial[key] = value
        Logger('Step: {0}'.format(step))
        # The exogenous and lagged variables are always fixed for a time period
        for var, dummy in self.Parser.Exogenous:
            initial[var] = self.TimeSeries[var][step]
        for lag_var, original_var in self.Parser.Lagged:
            initial[lag_var] = self.TimeSeries[original_var][step - 1]
        # This is an initial guess
        for var, dummy in self.Parser.Endogenous:
            initial[var] = self.TimeSeries[var][step - 1]
        # NOTE:
        # We are missing the decorative variables, but they have no effect on the convergence
        relative_error = 1.
        if self.ParameterErrorTolerance is None:
            err_toler = float(self.Parser.Err_Tolerance)
        else:
            err_toler = self.ParameterErrorTolerance
        num_tries = 0
        trace_keys = list(initial.keys())
        trace_keys.sort()
        # Logger('\t'.join(['Iteration', 'PreviousError'] + trace_keys), log='step')
        # The following two assignments not really necessary, but the code inspection
        # was unhappy if they were not set.
        had_evaluation_errors = False
        last_error = False
        while relative_error > err_toler:
            if is_trace_step:
                #Logger('\t'.join([str(num_tries), str(relative_error)] + [str(initial[x]) for x in trace_keys]),
                #       log='step')
                self.TimeSeriesStepTrace['iteration'].append(float(num_tries))
                self.TimeSeriesStepTrace['iteration_error'].append(relative_error)
                for k in trace_keys:
                    self.TimeSeriesStepTrace.AppendValue(k, initial[k])
            # Need to create a copy of the dictionary; saying new_value = initial means that they are
            # the same object.
            new_value = dict()
            for key, val in initial.items():
                new_value[key] = val
            relative_error = 0.
            had_evaluation_errors = False
            last_error = ''
            for var, eqn in self.Parser.Endogenous:
                # NOTE: We will try to step over some errors. For example, we can get a lot of
                # divisions by zero in the initial interation. The algorithm just notes the error,
                # and uses the previous value.
                # If the condition persists, we throw a ValueError to prevent going forward with the
                # invalid data.
                try:
                    new_value[var] = eval(eqn, globals(), initial)
                except ZeroDivisionError as er:
                    # We can add new error types that we are willing to temporarily accept.
                    new_value[var] = initial[var]
                    had_evaluation_errors = True
                    last_error = 'Error evaluating variable {0} = {1}'.format(var, str(er))
                except ValueError as er:
                    # We get a ValueError thrown by evaluating log10(0)
                    new_value[var] = initial[var]
                    had_evaluation_errors = True
                    last_error = 'Error evaluating variable {0}. Error message: {1}'.format(var, str(er))
                difference = abs(new_value[var] - initial[var])
                if difference < 1e-3:
                    relative_error += difference
                else:
                    # Scale by variable size if large
                    relative_error += difference / (max(abs(new_value[var]), abs(initial[var])))
            if num_tries > 10:
                # Allow initial iterations to swing a lot, but we clamp down the
                # movement later. (We want constants to immediately move to the correct value,
                # and there might be other variables where it takes a few steps to snap to the
                # correct value.)
                # New value equals average of originally calculated new value and previous;
                # that is, it moves half as much.
                # This slower movement reduces the odds of oscillation.
                for var, dummy in self.Parser.Endogenous:
                    new_value[var] = (new_value[var] + initial[var]) / 2.
            # Use new_value as the initial at the next step
            initial = new_value
            num_tries += 1
            if num_tries > self.MaxIterations:
                if had_evaluation_errors:
                    raise ValueError(last_error)
                raise ConvergenceError('Equations do not converge - step {0}'.format(step))
        if had_evaluation_errors:
            Logger('Had evaluation errors')
            raise ValueError(last_error)
        Logger('Number of iterations: {0}'.format(num_tries), priority=3)
        # Then: append values to the time series
        varlist = [x[0] for x in self.Parser.Endogenous] + [x[0] for x in self.Parser.Lagged]
        for var in varlist:
            assert (len(self.TimeSeries[var]) == step)
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
                # NOTE: We should not get here; it means that the decoration variables are
                # created incorrectly. Leave check to break infinite loops.
                out = ''
                Logger('Failure computing decoration equations!')
                for var, eqn in vars_to_compute:
                    out += '{0} = {1}\n'.format(var, eqn)
                    Logger(out)
                raise ValueError('Cannot solve decoration equations!\n'+out)
            vars_to_compute = failed

    def SolveEquation(self):
        if len(self.VariableList) == 0:
            self.ExtractVariableList()
        self.SetInitialConditions()
        if self.ParameterSolveInitialSteadyState:
            self.CalculateInitialSteadyState()
            # Reset the parameter; it needs to be set before every call to SolveEquation()
            Parameters.SolveInitialEquilibrium = False
        for step in range(1, self.Parser.MaxTime + 1):
            self.SolveStep(step)

    def WriteCSV(self, fname):  # pragma: no cover   We should not be writing files as part of unit tests...
        """
        Write time series to a tab-delimited text file.

        :param fname: str
        :return:
        """
        f = open(fname, 'w')
        f.write(self.GenerateCSVtext())

    def GenerateCSVtext(self, format_str='%.5g'):
        """
        :format_str: str
        Generates the text that goes into the csv.

        Implementation has migrated to the TimeSeriesHolder class.
        :return: str
        """
        return self.TimeSeries.GenerateCSVtext(format_str)
