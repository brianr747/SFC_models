from unittest import TestCase
import warnings
import math

from sfc_models.equation_solver import EquationSolver, ConvergenceError


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
        self.assertEqual([10.,]*4, v['t'])
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
        self.assertEqual([1., 1., 1., 1.,], obj.TimeSeries['t'])


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
        self.assertEqual([0., 1., 1.], obj.TimeSeries['w'])
        self.assertEqual([0., 1., 1.], obj.TimeSeries['y'])
        self.assertEqual([0., 1., 1.], obj.TimeSeries['z'])

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
        obj2. SolveEquation()
        self.assertEqual(obj.TimeSeries['x'], obj2.TimeSeries['x'])


    def test_SolveEquation_3(self):
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
        obj2.MaxIterations = 0
        with self.assertRaises(ConvergenceError):
            obj2.SolveEquation()
        # Validate that the exogenous variable is truncated to the same length as calculated vars
        self.assertEqual([10.,], obj2.TimeSeries['t'])



