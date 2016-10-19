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
