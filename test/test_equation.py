from unittest import TestCase
import doctest

from sfc_models.equation import Term, Equation, EquationBlock
from sfc_models.utils import LogicError
import sfc_models.equation

def load_tests(loader, tests, ignore):
    """
    Load doctests, so unittest discovery can find them.
    """
    tests.addTests(doctest.DocTestSuite(sfc_models.equation))
    return tests


class TestTerm(TestCase):
    def test_fail_bracket(self):
        with self.assertRaises(SyntaxError):
            Term('+(x ')

    def test_sign_1(self):
        t = Term('x')
        self.assertEqual(1.0, t.Constant)

    def test_sign_2(self):
        t = Term(' -x')
        self.assertEqual(-1.0, t.Constant)

    def test_sign_3(self):
        t = Term('-(-x)')
        self.assertEqual(1.0, t.Constant)

    def test_sign_4(self):
        t = Term('-(+x)')
        self.assertEqual(-1.0, t.Constant)

    def test_interior_1(self):
        with self.assertRaises(LogicError):
            t = Term('-(y-x)')

    def test_interior_2(self):
        with self.assertRaises(LogicError):
            t = Term('-(y+x)')

    def test_simple_1(self):
        t = Term('-x')
        self.assertTrue(t.IsSimple)
        self.assertEqual('x', t.Term)

    def test_simple_2(self):
        # Original comment: constants not supported yet as "Simple"
        # 2019-05-04: Not sure why no support for constants?
        t = Term('2')
        self.assertTrue(t.IsSimple)
        self.assertEqual('2', t.Term)
        # with self.assertRaises(NotImplementedError):
        #     t = Term('2')


    def test_simple_3(self):
        t = Term('x')
        self.assertTrue(t.IsSimple)
        self.assertEqual('x', t.Term)

    def test_copy(self):
        t = Term('x')
        t2 = Term(t)
        self.assertEqual('x', t2.Term)

    def test_str(self):
        t = Term('x')
        t.Constant = 0.
        self.assertEqual('', str(t))
        t.Constant = 1.
        self.assertEqual('+x', str(t))
        t.Constant = -1.
        self.assertEqual('-x', str(t))
        t.Constant = 2.
        self.assertEqual('+{0}*x'.format(str(2.)), str(t))
        t.Constant = -2.
        self.assertEqual('-{0}*x'.format(str(2.)), str(t))

    def test_blob(self):
        t = Term('(bazoonga*kablooie)^2', is_blob=True)
        self.assertEqual('(bazoonga*kablooie)^2', str(t))

    def test_not_simple(self):
        with self.assertRaises(NotImplementedError):
            t = Term('f(x)')
        # self.assertFalse(t.IsSimple)

    def test_multiply(self):
        t = Term('a*b')
        self.assertEqual('+a*b', str(t))

    def test_str_not_simple(self):
        with self.assertRaises(NotImplementedError):
            t = Term('f(x)')
        # self.assertFalse(t.IsSimple)
        # with self.assertRaises(NotImplementedError):
        #     str(t)


class TestEquation(TestCase):
    def test_str_1(self):
        t1 = Term('y')
        t2 = Term('-z')
        eq = Equation('x', 'define x', (t1, t2))
        self.assertEqual('y-z', eq.GetRightHandSide())

    def bad_ctor(self):
        t1 = Term('x')
        t2 = Term('y^2', is_blob=True)
        with self.assertRaises(LogicError):
            Equation('lhs', '', (t1,t2))

    def test_str_2(self):
        t1 = Term('y')
        t2 = Term('-z')
        eq = Equation('x', 'define x', (t2, t1))
        self.assertEqual('-z+y', eq.GetRightHandSide())

    def test_Addterm(self):
        eq = Equation('x', 'define x')
        eq.AddTerm('y')
        self.assertEqual('y', eq.GetRightHandSide())
        eq.AddTerm('y')
        self.assertEqual('2.0*y', eq.GetRightHandSide())

    def test_Addterm_2(self):
        eq = Equation('x', 'define x')
        eq.AddTerm('y')
        self.assertEqual('y', eq.GetRightHandSide())
        eq.AddTerm('-y')
        self.assertEqual('0.0', eq.GetRightHandSide())

    def test_Addterm_3(self):
        eq = Equation('x', 'define x')
        eq.AddTerm('y')
        self.assertEqual('y', eq.GetRightHandSide())
        eq.AddTerm('w*z')
        self.assertEqual('y+w*z', eq.GetRightHandSide())

    def test_AddTermFail(self):
        eq = Equation('x', 'desc', 'y')
        t2 = Term('y^2', is_blob=True)
        with self.assertRaises(LogicError):
            eq.AddTerm(t2)

    def test_String_ctor(self):
        eq3 = Equation("e = m*c^2 # Einstein's thingy")
        self.assertEqual("e=m*c^2 # Einstein's thingy", str(eq3))

    def test_string_ctor_fail(self):
        eq = Equation('x=(y)+1')
        # There's a syntax error, but ParseString eats it.
        self.assertEqual('(y)+1', str(eq.TermList[0]))

class TestEquationBlock(TestCase):
    def test_access(self):
        block = EquationBlock()
        eq = Equation('x', rhs=[Term('y')])
        block.AddEquation(eq)
        out = block['x']
        self.assertEqual('y', out.RHS())

    def test_list(self):
        block = EquationBlock()
        eq = Equation('x', rhs=[Term('y')])
        block.AddEquation(eq)
        block.AddEquation(Equation('a'))
        # Always sorted
        self.assertEqual(['a', 'x'], block.GetEquationList())
