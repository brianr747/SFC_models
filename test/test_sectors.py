from unittest import TestCase

from sfc_models.models import Model, Country
from sfc_models.sectors import *


class TestHouseHold(TestCase):
    def test_GenerateEquations_alpha(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        hh = Household(can, 'Household', 'HH', alpha_fin=.2, alpha_income=.9)
        hh.GenerateEquations()
        self.assertEqual(hh.Equations['AlphaFin'], '0.2000')
        self.assertEqual(hh.Equations['AlphaIncome'], '0.9000')


class TestDoNothingGovernment(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        gov.GenerateEquations()
        self.assertEqual(gov.Equations['DEM_GOOD'], '0.0')


class TestTaxFlow(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        tf = TaxFlow(can, 'Taxation Flows', 'Tax', .1)  # Supply side for the win!
        self.assertTrue('T' in tf.Equations)
        self.assertTrue('TaxRate' in tf.Equations)
        hh = Household(can, 'Household', 'HH', alpha_fin=.2, alpha_income=.9)
        gov = DoNothingGovernment(can, 'Gummint', 'GOV')
        mod.GenerateFullSectorCodes()
        tf.GenerateEquations()
        self.assertEqual('0.1000', tf.Equations['TaxRate'])
        self.assertEqual('TaxRate*HH_SUP_LAB', tf.Equations['T'].replace(' ', ''))
        self.assertEqual(['-T', ], hh.CashFlows)
        self.assertEqual('Tax_T', hh.Equations['T'])
        self.assertEqual(['+T', ], gov.CashFlows)
        self.assertEqual('Tax_T', gov.Equations['T'])


class TestFixedMarginBusiness(TestCase):
    def test_ctor_default(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        bus = FixedMarginBusiness(can, 'Business', 'BUS')
        self.assertEqual('GOOD_SUP_GOOD', bus.Equations['DEM_LAB'])

    def test_ctor_nonzero_profit(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        bus = FixedMarginBusiness(can, 'Business', 'BUS', profit_margin=0.1)
        self.assertEqual('0.900*GOOD_SUP_GOOD', bus.Equations['DEM_LAB'].replace(' ',''))


