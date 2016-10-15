from unittest import TestCase

from sfc_models.iterative_machine_generator import IterativeMachineGenerator

class TestIterativeMachineGenerator(TestCase):
    def create_example1(self):
        obj = IterativeMachineGenerator()
        obj.Endogenous = [('x', 'y + 2'), ('y', '.5 * x')]
        obj.Lagged = [('LAG_x', 'x')]
        obj.Exogenous = [('dummy', '[1., 1., 1.]')]
        return obj

    def create_example2(self):
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
        txt1 = ''
        txt2 = ''
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
        self.assertEqual(obj.EquationList, ['y + 2', '.5 * x', 'LAG_x', 'dummy' ])

    def test_GenerateFunction(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GenerateFunction()
        target = """    def Iterator(self, in_vec):
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
        target = """[indent]self.x = [0.000000,]
[indent]self.y = [0.000000,]
[indent]self.dummy = [1., 1., 1.]
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
    y = .5 * x,
    where lagged variables are:
    LAG_x(t) = x(t-1)


    Exogenous Variables
    ===================
    dummy
"""
        self.compare_text_blocks(out, target)

    def test_GeneratePackVars(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        out = obj.GeneratePackVars()
        target = """        x = self.x[-1]
        y = self.y[-1]
        LAG_x = self.x[self.T -1]
        dummy = self.dummy[self.T]
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

    def test_GenerateFile(self):
        obj = self.create_example1()
        obj.GenerateEquations()
        obj.GenerateFunction()
        obj.MaxTime = 3
        obj.GenerateFile('output\\unittest_output_1.py')
        self.compare_files('output\\unittest_output_1.py', 'output\\unittest_target_1.py')


    def test_main(self):
        obj = self.create_example2()
        obj.MaxTime = 3
        obj.main('output\\unittest_output_2.py')
        self.compare_files('output\\unittest_output_2.py', 'output\\unittest_target_2.py')


