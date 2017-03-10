from unittest import TestCase
import warnings
import math
import sys

from sfc_models.equation_solver import EquationSolver, ConvergenceError, NoEquilibriumError
from sfc_models import Parameters as Parameters

is_python_3 = sys.version_info[0] >= 3

class TestEquationSolver(TestCase):
    def test_init(self):
        obj = EquationSolver()
        self.assertEqual(0, len(obj.Parser.AllEquations))

    def test_init2(self):
        obj = EquationSolver('x=1.')
        self.assertIn('x', obj.Parser.AllEquations)

    def test_ParseString(self):
        obj = EquationSolver()
        obj.ParseString('x=1.')
        self.assertIn('x', obj.Parser.AllEquations)

    def test_ParseString_2(self):
        obj = EquationSolver()
        if is_python_3:
            with self.assertWarns(expected_warning=SyntaxWarning):
                obj.ParseString('x= y = 1')

    def test_ExtractVariableList_1(self):
        obj = EquationSolver()
        obj.ExtractVariableList()
        self.assertEqual([], obj.VariableList)

    def test_ExtractVariableList_2(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
        x=t
        z=x
        exogenous
        t=[10.]*20""")
        obj.ExtractVariableList()
        self.assertEqual(['t', 'x', 'z'], obj.VariableList)

    def test_ExtractVariableList_3(self):
        obj = EquationSolver()
        obj.RunEquationReduction = True
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x
         exogenous
         t=[10.]*20""")
        obj.ExtractVariableList()
        self.assertEqual(['t', 'x', 'z'], obj.VariableList)

    def test_ExtractVariableList_4(self):
        obj = EquationSolver()
        obj.RunEquationReduction = True
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x
         exogenous
         t=[10.]*20
         MaxTime=10""")
        obj.ExtractVariableList()
        self.assertEqual(['t', 'x', 'z'], obj.VariableList)

    def test_SetInitialConditions_1(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x
         z(0) = sqrt(20.)
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        v = obj.TimeSeries
        self.assertEqual([10., ] * 4, v['t'])
        self.assertEqual([0, 1, 2, 3], v['k'])
        self.assertEqual([0.], v['x'])
        self.assertEqual([math.sqrt(20)], v['z'])

    def test_SolveStep_1(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x+1
         z(0) = 2.
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.SolveStep(1)
        self.assertEqual([0., 10.], obj.TimeSeries['x'])
        # Note that equation does not hold at t=0
        self.assertEqual([2., 11.], obj.TimeSeries['z'])
        obj.SolveStep(2)
        self.assertEqual([0., 10., 10.], obj.TimeSeries['x'])
        # Note that equation does not hold at t=0
        self.assertEqual([2., 11., 11.], obj.TimeSeries['z'])

    def test_SolveStep_2(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x(k-1)
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.SolveStep(1)
        obj.SolveStep(2)
        self.assertEqual([0., 10., 10.], obj.TimeSeries['x'])
        self.assertEqual([0., 0., 10.], obj.TimeSeries['z'])

    def test_SolveStep_3(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x(k-1)
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.MaxIterations = 0
        with self.assertRaises(ConvergenceError):
            obj.SolveStep(1)

    def test_initial_conditions_bad_ic(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x(k-1)
         z(0) = Kaboom!
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        with self.assertRaises(ValueError):
            obj.SetInitialConditions()

    def test_initial_conditions_bad_ic2(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x(k-1)
         exogenous
         t=kaboom
         MaxTime=3""")
        obj.ExtractVariableList()
        with self.assertRaises(ValueError):
            obj.SetInitialConditions()

    def test_initial_conditions_const_exo(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
          x=t
          z=x(k-1)
          exogenous
          t=1.0
          MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        self.assertEqual([1., 1., 1., 1., ], obj.TimeSeries['t'])

    def test_initial_conditions_const_endo(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
           x=1.
           z=2
           exogenous
           t=1.0
           MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        self.assertEqual([1., ], obj.TimeSeries['x'])
        self.assertEqual([2., ], obj.TimeSeries['z'])

    def test_initial_conditions_const_decoration(self):
        obj = EquationSolver()
        obj.RunEquationReduction = True
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
           x=1.
           z=y
           y =x
           exogenous
           t=1.0
           MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        self.assertTrue(len(obj.Parser.Decoration) > 0)
        self.assertEqual([1., ], obj.TimeSeries['x'])
        self.assertEqual([1., ], obj.TimeSeries['z'])
        self.assertEqual([1., ], obj.TimeSeries['y'])

    def test_initial_conditions_with_float_exo(self):
        obj = EquationSolver()
        obj.RunEquationReduction = True
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
           x=1.
           z=y
           y =x
           exogenous
           t=1.0
           MaxTime=3""")
        obj.ExtractVariableList()
        self.assertEqual([('t', '1.0'), ], obj.Parser.Exogenous)
        # Turn it into a float.
        obj.Parser.Exogenous = [('t', 1.)]
        obj.SetInitialConditions()
        self.assertEqual([1., 1., 1., 1.], obj.TimeSeries['t'])

    def test_initial_conditions_too_short(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
          x=t
          z=x(k-1)
          exogenous
          t=[1., 1.]
          MaxTime=3""")
        # t is set too short
        obj.ExtractVariableList()
        with self.assertRaises(ValueError):
            obj.SetInitialConditions()

    def test_decoration1(self):
        obj = EquationSolver()
        obj.RunEquationReduction = True
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
          x=t
          w=y
          y=z
          z=x
          exogenous
          t=1.
          MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.SolveStep(1)
        obj.SolveStep(2)
        self.assertEqual([1., 1., 1.], obj.TimeSeries['w'])
        self.assertEqual([1., 1., 1.], obj.TimeSeries['y'])
        self.assertEqual([1., 1., 1.], obj.TimeSeries['z'])

    def test_decoration_fail(self):
        obj = EquationSolver()
        obj.RunEquationReduction = True
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
           x=2*t
           y=z
           z=x
           exogenous
           t=1.
           MaxTime=3""")
        # Need to break the decoration values;
        obj.Parser.Decoration = [('y', 'x'), ('z', 'foo')]
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        with self.assertRaises(ValueError):
            obj.SolveStep(1)

    def test_SolveEquation(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
         x=t
         z=x+1
         z(0) = 2.
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.SolveStep(1)
        obj.SolveStep(2)
        obj.SolveStep(3)
        obj2 = EquationSolver()
        obj2.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj2.ParseString("""
         x=t
         z=x+1
         z(0) = 2.
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj2.SolveEquation()
        self.assertEqual(obj.TimeSeries['x'], obj2.TimeSeries['x'])

    def test_SolveEquation_with_initial_equilibrium(self):
        obj2 = EquationSolver()
        obj2.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj2.ParseString("""
         x=t
         z=x+1
         z(0) = 2.
         exogenous
         t=[10.]*20
         MaxTime=3""")
        Parameters.SolveInitialEquilibrium = True
        obj2.SolveEquation()
        # Must be reset
        self.assertFalse(Parameters.SolveInitialEquilibrium)
        # The Initial equilibrium calculation overrides the initial condition.
        self.assertEqual([11., 11., 11., 11.], obj2.TimeSeries['z'])

    def test_DivideZeroSkip(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # This equation will initially have a divide by zero error; the algorithm will step over that.
        # This is because the initial guess for Z = 0.
        obj.ParseString("""
         z = t
         x=1/z
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.SolveStep(1)
        obj.SolveStep(2)
        self.assertEqual([0., .1, .1], obj.TimeSeries['x'])

    def test_FailLog0(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # This equation will initially have a divide by zero error; the algorithm will step over that.
        # This is because the initial guess for Z = 0.
        obj.ParseString("""
         x = log10(0)
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        with self.assertRaises(ValueError):
            obj.SolveStep(1)

    def test_FailLog0_maxiter(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # This equation will initially have a divide by zero error; the algorithm will step over that.
        # This is because the initial guess for Z = 0.
        # This test is used to hit the case where we do not converge
        obj.ParseString("""
         z = t
         y = z
         w = y
         x = log10(0)
         exogenous
         t=[10.]*20
         MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        obj.MaxIterations = 1
        with self.assertRaises(ValueError):
            obj.SolveStep(1)

    def test_csv_text(self):
        obj = EquationSolver()
        # Make the time series int so we do not test how floats are formatted...
        obj.TimeSeries = {
            'k': [0, 1],
            'foo': [10, 11],
            'cat': [0, 3],
        }
        targ = """k\tcat\tfoo
0\t0\t10
1\t3\t11
"""
        self.assertEqual(targ, obj.GenerateCSVtext())

    def test_csv_text_empty(self):
        obj = EquationSolver()
        # Make the time series int so we do not test how floats are formatted...
        obj.TimeSeries = {}
        targ = ''
        self.assertEqual(targ, obj.GenerateCSVtext())

    def test_csv_text2(self):
        obj = EquationSolver()
        # Make the time series int so we do not test how floats are formatted...
        obj.TimeSeries = {
            'k': [0, 1],
            'foo': [10, 11],
            't': [0, 3],
        }
        targ = """k\tt\tfoo
0\t0\t10
1\t3\t11
"""
        self.assertEqual(targ, obj.GenerateCSVtext())

    def test_InitialEquilibrium(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
             x=t
             z=x+1
             w=z(k-1)
             z(0) = 2.
             exogenous
             t=[10.]*20
             MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        Parameters.InitialEquilbriumMaxTime = 3
        copied_solver = obj.CalculateInitialEquilibrium()
        self.assertEqual([10., ], obj.TimeSeries['x'])
        self.assertEqual([11., ], obj.TimeSeries['z'])
        self.assertEqual([11., ], obj.TimeSeries['w'])
        self.assertEqual([2., 11., 11., 11.], copied_solver.TimeSeries['z'])
        self.assertEqual([0., 2., 11., 11.], copied_solver.TimeSeries['w'])

    def test_InitialEquilibrium_fail_convergence(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
             x=t + z
             z=x+1
             z(0) = 2.
             exogenous
             t=[10.]*20
             MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        Parameters.InitialEquilbriumMaxTime = 3
        obj.MaxIterations = 2
        with self.assertRaises(ValueError):
            obj.CalculateInitialEquilibrium()

    def test_InitialEquilibrium_fail_bad_eqn(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
             x=foo
             exogenous
             t=[10.]*20
             MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        Parameters.InitialEquilbriumMaxTime = 3
        obj.MaxIterations = 2
        with self.assertRaises(NameError):
            obj.CalculateInitialEquilibrium()

    def test_InitialEquilibrium_no_convergence(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
             x=t
             u = v+1
             v = u(k-1)
             exogenous
             t=[10.]*20
             MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        Parameters.InitialEquilbriumMaxTime = 3
        Parameters.InitialEquilibriumExcludedVariables = ['x']
        with self.assertRaises(NoEquilibriumError):
            obj.CalculateInitialEquilibrium()

    def test_InitialEquilibrium_zero(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
             x=y(t-1)
             y=x(t-1)
             x(0) = 0
             y(0) = 1
             exogenous
             t=[10.]*20
             MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()
        Parameters.InitialEquilbriumMaxTime = 2
        Parameters.InitialEquilibriumExcludedVariables = []
        with self.assertRaises(NoEquilibriumError):
            obj.CalculateInitialEquilibrium()

    def test_SolveWithFunction(self):
        obj = EquationSolver()
        obj.RunEquationReduction = False
        # By forcing 't' into the variable list, no automatic creation of time variables
        obj.ParseString("""
          x=t
          z=f(x)
          exogenous
          t=[10.]*20
          MaxTime=3""")
        obj.ExtractVariableList()
        obj.SetInitialConditions()

        def squarer(x):
            return x * x

        obj.AddFunction('f', squarer)
        obj.SolveStep(1)
        self.assertEqual([0., 10.], obj.TimeSeries['x'])
        # Note that equation does not hold at t=0
        self.assertEqual([0., 100.], obj.TimeSeries['z'])
        obj.SolveStep(2)
