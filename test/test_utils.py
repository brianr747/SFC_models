import doctest
from unittest import TestCase

import sfc_models.utils as utils
from sfc_models.utils import Logger
import sfc_models.examples


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
        Logger.log_file_handle = None
        # Nothing should happen,...
        Logger('test')

    def test_write_2(self):
        mock = MockFile()
        Logger.log_file_handle = mock
        Logger('text')
        self.assertEqual(['text\n'], mock.buffer)
        Logger('text2\n', priority=0)
        self.assertEqual(['text\n', 'text2\n'], mock.buffer)
        Logger.priority_cutoff = 5
        Logger("low_priority", priority=6)
        self.assertEqual(['text\n', 'text2\n'], mock.buffer)
        Logger('higher', priority=5)
        # Low priority messages have an indent.
        self.assertEqual(['text\n', 'text2\n', (' '*4) + 'higher\n'], mock.buffer)

    def test_cleanup(self):
        mock = MockFile()
        Logger.log_file_handle = mock
        self.assertFalse(mock.is_closed)
        Logger.cleanup()
        self.assertTrue(mock.is_closed)



