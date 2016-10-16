from unittest import TestCase

from sfc_models.iterative_machine_generator import IterativeMachineGenerator


class TestIterativeMachineGenerator(TestCase):
    @staticmethod
    def create_example1():
        obj = IterativeMachineGenerator()
        obj.Endogenous = [('x', 'y + 2'), ('y', '.5 * x')]
        obj.Lagged = [('LAG_x', 'x')]
        obj.Exogenous = [('dummy', '[1., 1., 1.]')]
        return obj

    @staticmethod
    def create_example2():
        obj = IterativeMachineGenerator()
        obj.Endogenous = [('x', 'y + 2'), ('y', 'alpha * x + dummy'), ('alpha', '.5')]
        obj.Lagged = [('LAG_x', 'x')]
        obj.Exogenous = [('dummy', '[0., 1., 2.]')]
        return obj

    def compare_files(self, f1, f2):
        """
        Very strict file comparison; might need to relax comparison (line endings, etc.)
        :param f1: str
        :param f2: str
        :return: bool
        """
        with open(f1, 'r') as h_1:
            txt1 = h_1.read()
        with open(f2, 'r') as h_2:
            txt2 = h_2.read()
        self.compare_text_blocks(txt1, txt2)

    def compare_text_blocks(self, txt1, txt2):
        """
        Asserts that the twoi blocks of text are effectively the same; ignores trailing whitespace
        :param txt1: str
        :param txt2: str
        :return: None
        """
        t1 = txt1.split('\n')
        t2 = txt2.split('\n')
        if not len(t1) == len(t2):  # pragma: no cover
            # This will blow up, but gives a more useful difference report
            print('Line counts:', len(t1), len(t2))
            self.assertEqual(txt1, txt2)
        for l1, l2 in zip(t1, t2):
            self.assertEqual(l1.rstrip(), l2.rstrip())

    def test_GenerateEquations(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        self.assertEqual(obj.AllVariables, ['x', 'y', 'LAG_x', 'dummy'])
        self.assertEqual(obj.EquationList, ['y + 2', '.5 * x', 'LAG_x', 'dummy'])

    def test_GenerateFunction(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GenerateFunction()
        target = """    @staticmethod\n    def Iterator(in_vec):
        x, y, LAG_x, dummy = in_vec
        NEW_x = y + 2
        NEW_y = .5 * x
        NEW_LAG_x = LAG_x
        NEW_dummy = dummy
        return NEW_x, NEW_y, NEW_LAG_x, NEW_dummy
"""
        out = out.split('\n')
        target = target.split('\n')
        for r1, r2 in zip(out, target):
            self.assertEqual(r1.strip(), r2.strip())

    def test_CalcError(self):
        self.assertEqual(1., IterativeMachineGenerator.CalcError([.5, .5], [0., 1]))

    def test_GenerateVarDeclaration(self):
        obj = self.create_example1()
        out = obj.GenerateVarDeclaration()
        target = """[indent]self.x = [0., ]
[indent]self.y = [0., ]
[indent]self.dummy = [1., 1., 1.]
[indent]#  Make sure exogenous variables are not longer than time frame
[indent]self.dummy = self.dummy[0:1]
"""
        target = target.replace('[indent]', ' ' * 8)
        self.compare_text_blocks(out, target)

    def test_Orig_Vector(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GenerateOrigVector()
        target = 'x, y, LAG_x, dummy'
        self.assertEqual(out, target)

    def test_GenerateDocEquation(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GenerateDocEquations()
        target = """    Endogenous variables and parameters
    ===================================
    x = y + 2,
    y = .5 * x.
    Where lagged variables are:
    LAG_x(t) = x(k-1).


    Exogenous Variables
    ===================
    dummy.
"""
        self.compare_text_blocks(out, target)

    def test_GenerateDocEquation_initcond(self):
        # NOTE: Since initial conditions are in a dict, order is random.
        obj = IterativeMachineGenerator()
        eqns = """
        t =  y + 2
        y = .5 * t
        y(0) = 20."""
        obj.ParseString(eqns)
        out = obj.GenerateDocEquations()
        target = """    Endogenous variables and parameters
    ===================================
    t = y + 2,
    y = .5 * t.
    Where lagged variables are:

    Initial Conditions:
    y(0) = 20. .

    Exogenous Variables
    ===================
"""
        self.compare_text_blocks(out, target)

    def test_GeneratePackVars(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GeneratePackVars()
        target = """        x = self.x[-1]
        y = self.y[-1]
        LAG_x = self.x[self.STEP -1]
        dummy = self.dummy[self.STEP]
"""
        self.compare_text_blocks(out, target)

    def test_GenerateUnpackVars(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GenerateUnpackVars()
        target = """        x = orig_vector[0]
        self.x.append(x)
        y = orig_vector[1]
        self.y.append(y)
"""
        self.compare_text_blocks(out, target)

    #  Skip this; as it's a pain to validate 2 files if the template changes...
    # def test_GenerateFile(self):
    #     obj = self.create_example1()
    #     obj.GenerateEquations()
    #     obj.GenerateFunction()
    #     obj.MaxTime = 3
    #     obj.GenerateFile('output\\unittest_output_1.py')
    #     self.compare_files('output\\unittest_output_1.py', 'output\\unittest_target_1.py')


    def test_main(self):
        eqns = """
# Test system used in unit tests.
x = y
LAG_x = x(t-1)
y = t + 2.0
z = LAG_x + 1.0
oops
# Exogenous
G = [20., ] * 20
        """
        with self.assertWarns(SyntaxWarning):
            obj = IterativeMachineGenerator(eqns)
        obj.main('output\\unittest_output_2.py')
        self.compare_files('output\\unittest_output_2.py', 'output\\unittest_target_2.py')

    def test_ParseString(self):
        obj = IterativeMachineGenerator()
        eqns = """

        # Comment
        oops
        x = 2*y
        y=.5
        z = y(t-1)
        Exogenous = crunk
        G = [5., 5.]

        """
        with self.assertWarns(SyntaxWarning):
            msg = obj.ParseString(eqns)
        self.assertTrue('oops' in msg)
        self.assertEqual(obj.Endogenous, [('x', '2*y'), ('y', '.5'), ('t', 't_minus_1 + 1.0')])
        self.assertEqual(obj.Lagged, [('z', 'y'), ('t_minus_1', 't')])
        self.assertEqual(obj.Exogenous, [('G', '[5., 5.]'), ])
        self.assertTrue('Ignored' in obj.GeneratedBy)

    def test_ParseString2(self):
        obj = IterativeMachineGenerator()
        obj.MaxTime = 0
        eqns = """

        # Comment

        x = 2*y
        z = 3 = y
        Exogenous
        t = [5., 5.]
        MaxTime = 10
        """
        with self.assertWarns(SyntaxWarning):
            msg = obj.ParseString(eqns)
        self.assertTrue('z = 3 = y' in msg)
        self.assertEqual(obj.Endogenous, [('x', '2*y'), ])
        self.assertEqual(obj.Lagged, [])
        self.assertEqual(obj.Exogenous, [('t', '[5., 5.]'), ])
        self.assertEqual(obj.MaxTime, 10)

    def test_BadMaxIter(self):
        obj = IterativeMachineGenerator()
        obj.MaxTime = 0
        eqns = """

         # Comment
         MaxTime = 4

         x = 2*y
         z = 3
         Exogenous
         y = [5.,]
         MaxTime = Kablooey
         """
        with self.assertRaises(ValueError):
            msg = obj.ParseString(eqns)

    def test_error_toler(self):
        obj = IterativeMachineGenerator('Err_Tolerance = 0.4')
        self.assertEqual(obj.Err_Tolerance,'0.4')

    def test_error_toler_fail(self):
        with self.assertRaises(ValueError):
            obj = IterativeMachineGenerator('Err_Tolerance = SNORTLOO')


    def test_string_ctor(self):
        eqns = """

        # Comment

        x = 2*y

        x = y = z
        Exogenous
        t = [5., 5.]
        MaxTime = 10
        """
        with self.assertWarns(SyntaxWarning):
            obj = IterativeMachineGenerator(eqns)
        self.assertEqual(obj.Endogenous, [('x', '2*y'), ])
        self.assertEqual(obj.Lagged, [])
        self.assertEqual(obj.Exogenous, [('t', '[5., 5.]'), ])
        self.assertEqual(obj.MaxTime, 10)

    def test_initial_conditions(self):
        obj = IterativeMachineGenerator()
        obj.MaxTime = 0
        eqns = """
        # Comment
        y(0) = FOOBAR
        """
        obj.ParseString(eqns)
        self.assertEqual(obj.InitialConditions, {'y': 'FOOBAR'})
