from unittest import TestCase

from sfc_models.models import Model, Country, Market
from sfc_models.sectors import *


def kill_spaces(s):
    """
    remove spaces from a string; makes testing easier as white space conventions may change in equations
    :param s:
    :return:
    """
    s = s.replace(' ', '')
    return s


class TestHouseHold(TestCase):
    def test_GenerateEquations_alpha(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        hh = Household(can, 'Household', 'HH', alpha_fin=.2, alpha_income=.9)
        hh.GenerateEquations()
        self.assertEqual(hh.Equations['AlphaFin'], '0.2000')
        self.assertEqual(hh.Equations['AlphaIncome'], '0.9000')

class TestMultiSupply(TestCase):
    def test_constructor_nosupply(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        with self.assertRaises(utils.LogicError):
            bus= FixedMarginBusinessMultiOutput(can, 'Business', 'BUS', market_list=[])


    def test_ctor_default(self):
        mod = Model()
        can = Country(mod, 'Canada', 'CA')
        marca = Market(can, 'market', 'GOOD')
        us = Country(mod, 'US', 'US')
        marus = Market(us, 'market', 'GOOD')
        bus = FixedMarginBusinessMultiOutput(can, 'Business', 'BUS',
                                             market_list=[marca, marus])
        bus2 = FixedMarginBusinessMultiOutput(us, 'Business', 'BUS',
                                             market_list=[marca, marus], profit_margin=.1)

        self.assertIn('SUP_GOOD', bus.Equations)
        self.assertIn('SUP_US_GOOD', bus.Equations)
        marus.SupplyAllocation = [[[bus2, 'allocation_equation'],], bus]
        mod.GenerateFullSectorCodes()
        marus.GenerateEquations()
        self.assertFalse(marus.ShareParent(bus))
        self.assertEqual('US_GOOD_SUP_CA_BUS', bus.Equations['SUP_US_GOOD'])
        self.assertEqual('US_GOOD_SUP_US_BUS', bus2.Equations['SUP_GOOD'])
        bus2.GenerateEquations()
        self.assertEqual('0.900 * SUP', bus2.Equations['DEM_LAB'])
        self.assertEqual('SUP_CA_GOOD+SUP_GOOD', bus2.Equations['SUP'])

class TestDoNothingGovernment(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        gov.GenerateEquations()
        self.assertEqual(gov.Equations['DEM_GOOD'], '0.0')


class TestTreasury(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = Treasury(can, 'Government', 'GOV')
        gov.GenerateEquations()
        self.assertEqual(gov.Equations['DEM_GOOD'], '0.0')


class TestCentralBank(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        tre = Treasury(can, 'Treasury', 'TRE')
        cb = CentralBank(can, 'Central Bank', 'CB', tre)
        mod.GenerateFullSectorCodes()
        cb.GenerateEquations()
        self.assertEqual(cb.Treasury, tre)


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
        self.assertEqual('0.900*GOOD_SUP_GOOD', bus.Equations['DEM_LAB'].replace(' ', ''))


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


class TestMoneyMarket(TestCase):
    def test_all(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        hou = Household(can, 'Household', 'HH', .5, .5)
        hou2 = Household(can, 'Household2', 'HH2', .5, .5)
        mm = MoneyMarket(can)
        mod.GenerateFullSectorCodes()
        mod.GenerateEquations()
        # Supply = Demand
        self.assertEqual('GOV_SUP_MON', mm.Equations['SUP_MON'])
        # Demand = Demand of two sectors
        self.assertEqual('HH_DEM_MON+HH2_DEM_MON', mm.Equations['DEM_MON'].replace(' ', ''))
        # At the sector level, demand = F
        self.assertEqual('HH_F', hou.Equations['DEM_MON'])
        self.assertEqual('HH2_F', hou2.Equations['DEM_MON'])


class TestDepositMarket(TestCase):
    def test_all(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        hou = Household(can, 'Household', 'HH', .5, .5)
        dummy = Sector(can, 'Dummy', 'DUM')
        mm = MoneyMarket(can)
        dep = DepositMarket(can)
        # Need to add demand functions in household sector
        mod.GenerateFullSectorCodes()
        hou.AddVariable('DEM_MON', 'Demand for Money', '0.5 * ' + hou.GetVariableName('F'))
        hou.AddVariable('DEM_DEP', 'Demand for Deposits', '0.5 * ' + hou.GetVariableName('F'))
        mod.GenerateEquations()
        # Supply = Demand
        self.assertEqual('GOV_SUP_DEP', dep.Equations['SUP_DEP'])
        # Demand = Demand of two sectors
        self.assertEqual('HH_DEM_DEP', dep.Equations['DEM_DEP'].replace(' ', ''))
        # At the sector level, demand = F
        self.assertEqual('0.5*HH_F', kill_spaces(hou.Equations['DEM_MON']))
        self.assertEqual('0.5*HH_F', kill_spaces(hou.Equations['DEM_DEP']))
        # Make sure the dummy does not have cash flows
        self.assertEqual([], dummy.CashFlows)
        # Household has a deposit interest cash flow
        self.assertIn('+INTDEP', hou.CashFlows)
