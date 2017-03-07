import doctest
from unittest import TestCase

import sfc_models.equation_parser


def load_tests(loader, tests, ignore):
    """
    Load doctests, so unittest discovery can find them.
    """
    tests.addTests(doctest.DocTestSuite(sfc_models.equation_parser))
    return tests


class TestEquationParser(TestCase):
    """
    Pretty much the whole class is covered by doctests.

    Can fill in more tests if desired.
    """

    def test_ParseString(self):
        pass

    def test_GenerateTokenList(self):
        pass

    def test_ValidateInputs(self):
        pass

    def test_EquationReduction(self):
        pass

    def test_empty(self):
        obj = sfc_models.equation_parser.EquationParser()
        self.assertIn('ignored line', obj.ParseString('Cat!').lower())

    def test_bad_maxIter(self):
        obj = sfc_models.equation_parser.EquationParser()
        with self.assertRaises(ValueError):
            obj.ParseString('MaxTime=CAT')

    def test_bad_ErrToler(self):
        obj = sfc_models.equation_parser.EquationParser()
        with self.assertRaises(ValueError):
            obj.ParseString('Err_Tolerance=CAT')

    def test_CleanupRightHandSide(self):
        obj = sfc_models.equation_parser.EquationParser()
        self.assertEqual('', obj.CleanupRightHandSide(' '))
        self.assertEqual('x', obj.CleanupRightHandSide('+x '))
        self.assertEqual('x', obj.CleanupRightHandSide(' +x'))
        self.assertEqual('-x', obj.CleanupRightHandSide('-x'))

    def test_FindExactMatches(self):
        pass

    def test_RebuildEquations(self):
        pass

    def test_MoveDecorative(self):
        pass
