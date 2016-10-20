from unittest import TestCase

from sfc_models.base_solver import BaseSolver

class TestBaseSolver(TestCase):
    def test_CsvString(self):
        obj = BaseSolver(['x', 'y', 't'])
        obj.x = [1., 1., 1.]
        obj.y = [2., 2., 2.]
        obj.t = [0., 1., 2.]
        out = obj.CreateCsvString()
        targ = """t\tx\ty
0.0\t1.0\t2.0
1.0\t1.0\t2.0
2.0\t1.0\t2.0
"""
        self.assertEqual(targ, out)