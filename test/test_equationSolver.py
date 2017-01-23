from unittest import TestCase
import math

from sfc_models.equation_solver import EquationSolver


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


    def test_SoolveStep_1(self):
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


