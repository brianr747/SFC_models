from unittest import TestCase
import doctest

import sfc_models.utils as utils
from sfc_models.utils import replace_token

def load_tests(loader, tests, ignore):
    """
    Load doctests, so unittest discovery can find them.
    """
    tests.addTests(doctest.DocTestSuite(utils))
    return tests


class TestReplace_token(TestCase):
    def test_replace_token_1(self):
        self.assertEqual(utils.replace_token('','foo','bar'), '')

class TestReplaceTokenLookup(TestCase):
    def test_replace_1(self):
        self.assertEqual('a =y ', utils.replace_token_from_lookup('a=b', {'b': 'y'}))

    def test_replace_block(self):
        eqns = 'y = x + 1\nx = t'
        lookup = {'y': 'H_y', 'x': 'H_x'}
        self.assertEqual('H_y =H_x +1 \n'+'H_x =t ', utils.replace_token_from_lookup(eqns, lookup))
