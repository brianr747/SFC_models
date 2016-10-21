from unittest import TestCase

import sfc_models.extras as extras


class TestQuick2DPlot(TestCase):
    def test_DoPlot(self):
        # Kill the matlibplot module; no interactive output in tests
        extras.plt = None
        x = [1., 2., 3.]
        y = [2., 5., 7.]
        obj = extras.Quick2DPlot(x, y)
        self.assertEqual([1., 2., 3.], obj.X)
        self.assertEqual([2., 5., 7.], obj.Y)
        self.assertEqual('', obj.Title)



