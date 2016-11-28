from unittest import TestCase

from sfc_models.models import Model, Country, Market
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
        self.assertEqual('Tax_TaxRate*HH_PreTax', tf.Equations['T'].replace(' ', ''))
        self.assertEqual(['-T', ], hh.CashFlows)
        self.assertEqual('Tax_TaxRate * HH_PreTax', hh.Equations['T'])
        self.assertEqual(['+T', ], gov.CashFlows)
        self.assertEqual('Tax_T', gov.Equations['T'])

    def test_GenerateEquationsSpecialised(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        tf = TaxFlow(can, 'Taxation Flows', 'Tax', .1)
        self.assertTrue('T' in tf.Equations)
        self.assertTrue('TaxRate' in tf.Equations)
        hh = Household(can, 'Household', 'HH', alpha_fin=.2, alpha_income=.9)
        hh.AddVariable('TaxRate', 'Sector level tax rate', '0,2')
        gov = DoNothingGovernment(can, 'Gummint', 'GOV')
        mod.GenerateFullSectorCodes()
        tf.GenerateEquations()
        self.assertEqual('0.1000', tf.Equations['TaxRate'])
        self.assertEqual('HH_TaxRate*HH_PreTax', tf.Equations['T'].replace(' ', ''))
        self.assertEqual(['-T', ], hh.CashFlows)
        self.assertEqual('HH_TaxRate * HH_PreTax', hh.Equations['T'])
        self.assertEqual(['+T', ], gov.CashFlows)
        self.assertEqual('Tax_T', gov.Equations['T'])


class TestFixedMarginBusiness(TestCase):
    def test_ctor_default(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        bus = FixedMarginBusiness(can, 'Business', 'BUS')
        self.assertEqual(0., bus.ProfitMargin)
        mar = Market(can, 'market', 'GOOD')
        mod.GenerateFullSectorCodes()
        bus.GenerateEquations()
        self.assertEqual('GOOD_SUP_GOOD', bus.Equations['DEM_LAB'].replace(' ', ''))

    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        bus = FixedMarginBusiness(can, 'Business', 'BUS', profit_margin=0.1)
        mar = Market(can, 'market', 'GOOD')
        mod.GenerateFullSectorCodes()
        bus.GenerateEquations()
        self.assertEqual('0.900*GOOD_SUP_GOOD', bus.Equations['DEM_LAB'].replace(' ',''))

class TestCapitalists(TestCase):
    def test_dividend(self):
        mod = Model()
        can = Country(mod, 'Canada', 'CA')
        us = Country(mod, 'US of A', 'US')
        bus = FixedMarginBusiness(can, 'Business', 'BUS', profit_margin=.1)
        mar = Market(can, 'market', 'GOOD')
        cap = Capitalists(can, 'Capitalists', 'CAP', .4, .4)
        mod.GenerateFullSectorCodes()
        bus.GenerateEquations()
        self.assertEqual('CA_BUS_PROF', cap.Equations['DIV'])
