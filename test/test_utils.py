from unittest import TestCase
import doctest

import sfc_models.utils as utils


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


class TestCreate_equation_from_terms(TestCase):
    def test_create_equation_from_terms_1(self):
        self.assertEqual('', utils.create_equation_from_terms([]))
