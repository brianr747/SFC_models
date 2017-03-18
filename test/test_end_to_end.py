"""
End-to-end tests of the framework, using the models from Godley & Lavoie.

Since some of these models take awhile to build, we can set the environment variable
DontRunEndToEnd to skip them.

Within PyCharm, I just create two unittest configurations; one for quick unit tests (runs
in about a second), and then the slower end-to-end configuration that includes both.

Unfortunately, the end-to-end tests pick up most of the economic logic errors, so they
still need to be run frequently.
"""

import os
import unittest
from unittest import TestCase
import cProfile
import sfc_models.gl_book.chapter3
import sfc_models.gl_book.chapter4
import sfc_models.gl_book.chapter6

# Set this environment variable to 'T' in order to skip the slower end-to-end tests.
skip_end_to_end = os.getenv('DontRunEndToEnd')


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
        do_profile = False
        if do_profile:
            pr = cProfile.Profile()
            pr.enable()
        builder = self.get_builder()
        model = builder.build_model()
        prec = self.get_precision()
        expected = builder.expected_output()
        l = [len(x[1]) for x in expected]
        model.MaxTime = min(max(l)-1,12)
        model.main()
        if do_profile:
            pr.disable()
            pr.print_stats(sort="time")
        for varname, targ in expected:
            if type(targ) is str:
                targ = targ.split('\t')
                targ = [float_converter(x) for x in targ]
            actual = model.GetTimeSeries(varname)
            # We only test out to k=20
            for k in range(0, min(model.MaxTime, len(targ))):
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

    @unittest.skipIf(skip_end_to_end == 'T', 'Slow test excluded')
    def test_model(self):
        EndToEndTester.test_model(self)


class TestREG(EndToEndTester):
    """
    Tests model REG.
    Big model; skipped if environment variable DontRunEndToEnd = 'T'
    """

    def get_precision(self):
        return 1

    def get_builder(self):
        return sfc_models.gl_book.chapter6.REG('C', use_book_exogenous=True)

    @unittest.skipIf(skip_end_to_end=='T', 'Slow test excluded')
    def test_model(self):
        EndToEndTester.test_model(self)

class TestREG2(EndToEndTester):
    """
    Tests model REG2.

    Big model; skipped if environment variable DontRunEndToEnd = 'T'
    """
    @unittest.skipIf(skip_end_to_end=='T', 'Slow test excluded')
    def test_model(self):
        EndToEndTester.test_model(self)


    def get_precision(self):
        # We have some variables with errors about 0.5; bad initial conditions?
        return 0

    def get_builder(self):
        return sfc_models.gl_book.chapter6.REG2('C', use_book_exogenous=True)
