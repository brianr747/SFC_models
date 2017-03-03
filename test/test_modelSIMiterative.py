from unittest import TestCase

import sfc_models.gl_book.model_SIM_iterative as model


class TestModelSIMiterative(TestCase):
    def test_RunStep(self):
        obj = model.ModelSIMiterative()
        obj.RunStep()
        self.assertEqual(round(obj.Y[1], 2), 100.)

    def test_RunMethod2(self):
        obj = model.ModelSIMiterative()
        obj.RunMethod2()
        self.assertEqual(round(obj.Y[1], 2), 100.)

    def test_run_main(self):
        obj = model.ModelSIMiterative()
        obj.G = [20., ] * 2 + [25., ] * 3
        obj.main()
        self.assertEqual(round(obj.Y[1], 2), 100.)
