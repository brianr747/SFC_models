import doctest
from unittest import TestCase

import sfc_models.utils as utils
from sfc_models.utils import Logger
from sfc_models.equation_solver import EquationSolver
import sfc_models.examples
from sfc_models import Parameters


def load_tests(loader, tests, ignore):
    """
    Load doctests, so unittest discovery can find them.
    """
    tests.addTests(doctest.DocTestSuite(utils))
    return tests


class TestReplace_token(TestCase):
    def test_replace_token_1(self):
        self.assertEqual(utils.replace_token('', 'foo', 'bar'), '')


class TestReplaceTokenLookup(TestCase):
    def test_replace_1(self):
        self.assertEqual('a =y ', utils.replace_token_from_lookup('a=b', {'b': 'y'}))

    def test_replace_block(self):
        eqns = 'y = x + 1\nx = t'
        lookup = {'y': 'H_y', 'x': 'H_x'}
        self.assertEqual('H_y =H_x +1 \n' + 'H_x =t ', utils.replace_token_from_lookup(eqns, lookup))


class TestGetValid(TestCase):
    def test_list(self):
        bad = utils.get_invalid_variable_names()
        self.assertIn('self', bad)
        self.assertIn('import', bad)
        self.assertIn('sqrt', bad)

    def test_examples_fn(self):
        self.assertEqual('cat', sfc_models.examples.get_file_base('C:\\temp\\cat.txt'))
        self.assertEqual('cat', sfc_models.examples.get_file_base('C:\\temp\\cat'))

    def test_token_list(self):
        bad = utils.get_invalid_tokens()
        self.assertIn('self', bad)
        self.assertIn('import', bad)
        # We allow some builtin mathematical operators
        # Full list in the source code.
        self.assertNotIn('max', bad)
        # Also: functions in "math"
        self.assertNotIn('sqrt', bad)


class TestCreate_equation_from_terms(TestCase):
    def test_create_equation_from_terms_1(self):
        self.assertEqual('', utils.create_equation_from_terms([]))


class MockFile(object):
    def __init__(self):
        self.buffer = []
        self.is_closed = False

    def write(self, msg):
        self.buffer.append(msg)

    def close(self):
        self.is_closed = True


class TestLogger(TestCase):
    def test_write_1(self):
        # Nothing should happen,...
        Logger('test')

    def test_write_2(self):
        mock = MockFile()
        Logger.log_file_handles = {'log': mock}
        Logger('text')
        self.assertEqual(['text\n'], mock.buffer)
        Logger('text2\n', priority=0)
        self.assertEqual(['text\n', 'text2\n'], mock.buffer)
        Logger.priority_cutoff = 5
        Logger("low_priority", priority=6)
        self.assertEqual(['text\n', 'text2\n'], mock.buffer)
        Logger('higher', priority=5)
        # Low priority messages have an indent.
        self.assertEqual(['text\n', 'text2\n', (' ' * 4) + 'higher\n'], mock.buffer)

    def test_cleanup(self):
        mock = MockFile()
        Logger.log_file_handles = {'log': mock}
        self.assertFalse(mock.is_closed)
        Logger.cleanup()
        self.assertTrue(mock.is_closed)

    def test_register(self):
        Logger.cleanup()
        Logger.register_log('filename', 'log')
        self.assertEqual({'log': 'filename'}, Logger.log_file_handles)
        with self.assertRaises(ValueError):
            Logger.register_log('fname2', 'log')


class TestEquationSolverLogging(TestCase):
    def test_solver_logging(self):
        Logger.cleanup()
        mock = MockFile()
        Logger.log_file_handles = {'step': mock}
        Parameters.TraceStep = 2
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
        self.assertEqual([], mock.buffer)
        obj.SolveStep(1)
        self.assertEqual([], mock.buffer)
        obj.SolveStep(2)
        # I do not care what the contents are; I just want to validate
        # that it triggers
        self.assertTrue(len(mock.buffer) > 0)
        # Reset the buffer
        mock.buffer = []
        obj.SolveStep(3)
        self.assertEqual([], mock.buffer)
