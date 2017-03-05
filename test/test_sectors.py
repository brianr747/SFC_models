from unittest import TestCase

from sfc_models.models import Model, Country
from sfc_models.sector_definitions import *


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
        hh._GenerateEquations()
        self.assertEqual(hh.EquationBlock['AlphaFin'].RHS(), '0.2000')
        self.assertEqual(hh.EquationBlock['AlphaIncome'].RHS(), '0.9000')

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
        self.assertIn('SUP_GOOD', bus.EquationBlock.Equations)
        self.assertIn('SUP_US_GOOD', bus.EquationBlock.Equations)
        marus.SupplyAllocation = [[[bus2, 'allocation_equation'],], bus]
        mod._GenerateFullSectorCodes()
        marus._GenerateEquations()
        self.assertFalse(marus.ShareParent(bus))
        self.assertEqual('US_GOOD__SUP_CA_BUS', bus.EquationBlock['SUP_US_GOOD'].RHS())
        self.assertEqual('US_GOOD__SUP_US_BUS', bus2.EquationBlock['SUP_GOOD'].RHS())
        bus2._GenerateEquations()
        self.assertEqual('0.900*SUP', bus2.EquationBlock['DEM_LAB'].RHS())
        self.assertEqual('SUP_CA_GOOD+SUP_GOOD', bus2.EquationBlock['SUP'].RHS())

class TestDoNothingGovernment(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        gov._GenerateEquations()
        self.assertEqual(gov.EquationBlock['DEM_GOOD'].RHS(), '0.0')


class TestTreasury(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = Treasury(can, 'Government', 'GOV')
        gov._GenerateEquations()
        self.assertEqual(gov.EquationBlock['DEM_GOOD'].RHS(), '0.0')


class TestCentralBank(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        tre = Treasury(can, 'Treasury', 'TRE')
        cb = CentralBank(can, 'Central Bank', 'CB', tre)
        mod._GenerateFullSectorCodes()
        cb._GenerateEquations()
        self.assertEqual(cb.Treasury, tre)


class TestTaxFlow(TestCase):
    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        tf = TaxFlow(can, 'Taxation Flows', 'Tax', .1)  # Supply side for the win!
        self.assertTrue('T' in tf.EquationBlock.Equations)
        self.assertTrue('TaxRate' in tf.EquationBlock.Equations)
        hh = Household(can, 'Household', 'HH', alpha_fin=.2, alpha_income=.9)
        gov = DoNothingGovernment(can, 'Gummint', 'GOV')
        mod._GenerateFullSectorCodes()
        tf._GenerateEquations()
        self.assertEqual('0.1000', tf.EquationBlock['TaxRate'].RHS())
        self.assertEqual('Tax__TaxRate*HH__INC', tf.EquationBlock['T'].RHS().replace(' ', ''))
        self.assertIn('-T',hh.EquationBlock['F'].RHS())
        self.assertEqual('Tax__TaxRate*HH__INC', hh.EquationBlock['T'].RHS())
        self.assertEqual('LAG_F+T', gov.EquationBlock['F'].RHS())
        self.assertEqual('Tax__T', gov.EquationBlock['T'].RHS())

    def test_GenerateEquationsSpecialised(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        tf = TaxFlow(can, 'Taxation Flows', 'Tax', .1)
        self.assertTrue('T' in tf.EquationBlock.Equations)
        self.assertTrue('TaxRate' in tf.EquationBlock.Equations)
        hh = Household(can, 'Household', 'HH', alpha_fin=.2, alpha_income=.9)
        hh.AddVariable('TaxRate', 'Sector level tax rate', '0,2')
        gov = DoNothingGovernment(can, 'Gummint', 'GOV')
        mod._GenerateFullSectorCodes()
        tf._GenerateEquations()
        self.assertEqual('0.1000', tf.EquationBlock['TaxRate'].RHS())
        self.assertEqual('HH__TaxRate*HH__INC', tf.EquationBlock['T'].RHS().replace(' ', ''))
        self.assertIn('-T', hh.EquationBlock['F'].RHS())
        self.assertEqual('HH__TaxRate*HH__INC', hh.EquationBlock['T'].RHS())
        # self.assertEqual(['+T', ], gov.CashFlows)
        self.assertEqual('Tax__T', gov.EquationBlock['T'].RHS())


class TestFixedMarginBusiness(TestCase):
    def test_ctor_default(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        bus = FixedMarginBusiness(can, 'Business', 'BUS')
        self.assertEqual(0., bus.ProfitMargin)
        mar = Market(can, 'market', 'GOOD')
        mod._GenerateFullSectorCodes()
        bus._GenerateEquations()
        self.assertEqual('GOOD__SUP_GOOD', bus.EquationBlock['DEM_LAB'].RHS().replace(' ', ''))

    def test_GenerateEquations(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        bus = FixedMarginBusiness(can, 'Business', 'BUS', profit_margin=0.1)
        mar = Market(can, 'market', 'GOOD')
        mod._GenerateFullSectorCodes()
        bus._GenerateEquations()
        self.assertEqual('0.900*GOOD__SUP_GOOD', bus.EquationBlock['DEM_LAB'].RHS().replace(' ', ''))


class TestCapitalists(TestCase):
    def test_dividend(self):
        mod = Model()
        can = Country(mod, 'Canada', 'CA')
        us = Country(mod, 'US of A', 'US')
        bus = FixedMarginBusiness(can, 'Business', 'BUS', profit_margin=.1)
        mar = Market(can, 'market', 'GOOD')
        cap = Capitalists(can, 'Capitalists', 'CAP', .4, .4)
        mod._GenerateFullSectorCodes()
        bus._GenerateEquations()
        self.assertEqual('CA_BUS__PROF', cap.EquationBlock['DIV'].RHS())


class TestMoneyMarket(TestCase):
    def test_all(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        hou = Household(can, 'Household', 'HH', .5, .5)
        hou2 = Household(can, 'Household2', 'HH2', .5, .5)
        mm = MoneyMarket(can)
        mod._GenerateFullSectorCodes()
        mod._GenerateEquations()
        # Supply = Demand
        self.assertEqual('GOV__SUP_MON', mm.EquationBlock['SUP_MON'].RHS())
        # Demand = Demand of two sectors
        self.assertEqual('HH__DEM_MON+HH2__DEM_MON', mm.EquationBlock['DEM_MON'].RHS().replace(' ', ''))
        # At the sector level, demand = F
        self.assertEqual('HH__F', hou.EquationBlock['DEM_MON'].RHS())
        self.assertEqual('HH2__F', hou2.EquationBlock['DEM_MON'].RHS())


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
        mod._GenerateFullSectorCodes()
        hou.AddVariable('DEM_MON', 'Demand for Money', '0.5 * ' + hou.GetVariableName('F'))
        hou.AddVariable('DEM_DEP', 'Demand for Deposits', '0.5 * ' + hou.GetVariableName('F'))
        mod._GenerateEquations()
        # Supply = Demand
        self.assertEqual('GOV__SUP_DEP', dep.EquationBlock['SUP_DEP'].RHS())
        # Demand = Demand of two sectors
        self.assertEqual('HH__DEM_DEP', dep.EquationBlock['DEM_DEP'].RHS().replace(' ', ''))
        # At the sector level, demand = F
        self.assertEqual('0.5*HH__F', kill_spaces(hou.EquationBlock['DEM_MON'].RHS()))
        self.assertEqual('0.5*HH__F', kill_spaces(hou.EquationBlock['DEM_DEP'].RHS()))
        # Make sure the dummy does not have cash flows
        self.assertEqual('LAG_F', dummy.EquationBlock['F'].RHS())
        # Household has a deposit interest cash flow
        self.assertIn('INTDEP', hou.EquationBlock['F'].RHS())
