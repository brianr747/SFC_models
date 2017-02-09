"""
End-to-end tests of the framework, using the models from Godley & Lavoie.
"""
from unittest import TestCase

import sfc_models.gl_book.chapter3


class EndToEndTester(TestCase):
    """
    Tests model SIM. We reuse this base class for all the other models by just swapping out the constructor.
    """
    def get_builder(self):
        return sfc_models.gl_book.chapter3.SIM('C', use_book_exogenous=True)

    def test_run_model(self):
        builder = self.get_builder()
        model = builder.build_model()
        model.main()
        expected = builder.expected_output()
        for varname, targ in expected:
            actual = model.GetTimeSeries(varname)
            for k in range(0, len(targ)):
                self.assertAlmostEqual(targ[k], actual[k], places=1, msg='Failure in variable ' + varname)

class TestSIMEX1(EndToEndTester):
    """
    Tests model SIMEX1.
    """
    def get_builder(self):
        return sfc_models.gl_book.chapter3.SIMEX1('C', use_book_exogenous=True)

