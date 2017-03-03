"""
End-to-end tests of the framework, using the models from Godley & Lavoie.
"""

from unittest import TestCase

import sfc_models.gl_book.chapter3
import sfc_models.gl_book.chapter4
import sfc_models.gl_book.chapter6


def float_converter(x):
    # noinspection PyBroadException
    try:
        return float(x)
    except:
        return None


class EndToEndTester(TestCase):
    """
    Tests model SIM. We reuse this base class for all the other models by just swapping out the constructor.
    """

    def get_builder(self):
        return sfc_models.gl_book.chapter3.SIM('C', use_book_exogenous=True)

    def get_precision(self):
        return 1

    def test_model(self):
        builder = self.get_builder()
        model = builder.build_model()
        model.MaxTime = 20
        model.main()
        prec = self.get_precision()
        expected = builder.expected_output()
        for varname, targ in expected:
            if type(targ) is str:
                targ = targ.split('\t')
                targ = [float_converter(x) for x in targ]
            actual = model.GetTimeSeries(varname)
            # We only test out to k=20
            for k in range(0, min(20, len(targ))):
                if targ[k] is None:
                    continue
                self.assertAlmostEqual(targ[k], actual[k], places=prec,
                                       msg='Failure in variable {0} at k={1}'.format(varname, k))


class TestSIMEX1(EndToEndTester):
    """
    Tests model SIMEX1.
    """

    def get_builder(self):
        return sfc_models.gl_book.chapter3.SIMEX1('C', use_book_exogenous=True)


class TestPC(EndToEndTester):
    """
    Tests model SIMEX1.
    """

    def get_builder(self):
        return sfc_models.gl_book.chapter4.PC('C', use_book_exogenous=True)


class TestREG(EndToEndTester):
    """
    Tests model REG.
    """

    def get_precision(self):
        return 1

    def get_builder(self):
        return sfc_models.gl_book.chapter6.REG('C', use_book_exogenous=True)
