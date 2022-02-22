from unittest import TestCase
import os
import unittest

from sfc_models.models import Model, Country
from sfc_models.sector import Sector, Market
from sfc_models.external import ExternalSector, ExchangeRates, ForexTransactions
from sfc_models.sector_definitions import GoldStandardCentralBank, GoldStandardGovernment, Treasury, MoneyMarket, DepositMarket
from sfc_models.utils import LogicError


# Set this environment variable to 'T' in order to skip the slower end-to-end tests.
skip_end_to_end = os.getenv('DontRunEndToEnd')

class TestExternalSector(TestCase):
    def test_ctor_1(self):
        mod = Model()
        ext = ExternalSector(mod)
        # Check that these sectors exist
        xr = ext['XR']
        fx = ext['FX']
        self.assertIs(ExchangeRates, type(xr))
        self.assertIn('NUMERAIRE', xr.EquationBlock)
        self.assertIs(ForexTransactions, type(fx))

    def test_GetCrossRate(self):
        mod = Model()
        ext = ExternalSector(mod)
        c1 = Country(mod, 'C1', 'C1')
        c2 = Country(mod, 'C2', 'C2')
        mod._GenerateFullSectorCodes()
        xr = ext['XR']
        self.assertIn('C1', xr.EquationBlock)
        self.assertIn('C2', xr.EquationBlock)
        self.assertNotIn('C1_C2', xr.EquationBlock)
        xrate = ext.GetCrossRate('C1', 'C2')
        self.assertEqual('EXT_XR__C1_C2', xrate)
        self.assertIn('C1_C2', xr.EquationBlock)
        self.assertEqual('C1/C2', xr.EquationBlock['C1_C2'].RHS())

    def test_SendMoney(self):
        mod = Model()
        ext = ExternalSector(mod)
        ca = Country(mod, 'CA', 'Canada', currency='CAD')
        hh_ca = Sector(ca, 'HH', 'Canada HH')
        hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
        fx = ext['FX']
        mod._GenerateFullSectorCodes()
        fx._SendMoney(hh_ca, 'GIFT')
        self.assertEqual('CA_HH__GIFT', fx.EquationBlock['NET_CAD'].RHS())

    def test_ReceiveMoney(self):
        mod = Model()
        ext = ExternalSector(mod)
        ca = Country(mod, 'CA', 'Canada', currency='CAD')
        us = Country(mod, 'US', 'U.S.', currency='USD')
        hh_ca = Sector(ca, 'HH', 'Canada HH')
        hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
        hh_us = Sector(us, 'HH', 'Household')
        fx = ext['FX']
        mod._GenerateFullSectorCodes()
        fx._ReceiveMoney(hh_us, hh_ca, 'GIFT')
        self.assertEqual('-CA_HH__GIFT*EXT_XR__CAD_USD', fx.EquationBlock['NET_USD'].RHS())

    def test_GetCrossRate_CurrencyZone(self):
        mod = Model()
        ext = ExternalSector(mod)
        c1 = Country(mod, 'C1', 'C1')
        c2 = Country(mod, 'C2', 'C2')
        mod._GenerateFullSectorCodes()
        xr = ext['XR']
        xrate = ext.GetCrossRate(c1.CurrencyZone, c2.CurrencyZone)
        self.assertEqual('EXT_XR__C1_C2', xrate)

    def test_CashFlow(self):
        mod = Model()
        ext = ExternalSector(mod)
        ca = Country(mod, 'CA', 'Canada', currency='CAD')
        us = Country(mod, 'US', 'United States', currency='USD')
        hh_ca = Sector(ca, 'HH', 'Canada HH')
        hh_us = Sector(us, 'HH', 'US HH')
        hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
        xr = ext['XR']
        xr.SetExogenous('CAD', '[1.5,]*100')
        mod.EquationSolver.MaxTime = 3
        mod.RegisterCashFlow(hh_ca, hh_us, 'GIFT', False, True)
        mod.main()
        testfn = mod.GetTimeSeries
        self.assertEqual([0., -5., -10., -15.], testfn('CA_HH__F'))
        self.assertEqual([5., 5., 5., 5.], testfn('EXT_FX__NET_CAD'))
        self.assertEqual([-7.5, -7.5, -7.5, -7.5], testfn('EXT_FX__NET_USD'))
        self.assertEqual([0., 0., 0., 0.], testfn('EXT_FX__NET_NUMERAIRE'))

    def test_Market_handling(self):
        mod = Model()
        ext = ExternalSector(mod)
        ca = Country(mod, 'CA', 'Canada', currency='CAD')
        us = Country(mod, 'US', 'United States', currency='USD')
        # gov_us.AddVariable('T', 'Government Taxes', '0.')
        gov_ca = Sector(ca, 'GOV', 'Gummint')
        gov_ca.AddVariable('DEM_GOOD', 'desc', '20.')
        market = Market(ca, 'GOOD', 'Market')
        supplier_ca = Sector(ca, 'BUS', 'Canada supplier')
        supplier_us = Sector(us, 'BUS', 'US Supplier')
        # Set supply so that CAD$10 is paid to each supplier.
        market.AddSupplier(supplier_ca)
        market.AddSupplier(supplier_us, '10.')
        # Set CAD = 2, so 2 USD = 1 CAD (USD is weaker.)
        mod.AddExogenous('EXT_XR', 'CAD', '[2.0,]*3')
        mod.EquationSolver.MaxTime = 1
        mod.main()
        mod.TimeSeriesSupressTimeZero = True
        # The business sector nets USD$20
        self.assertEqual([20.], mod.GetTimeSeries('US_BUS__F'))
        # The USD market is unbalanced; shortage of 20 USD
        self.assertEqual([-20.], mod.GetTimeSeries('EXT_FX__NET_USD'))
        # The CAD market is unbalanced; excess of 10 CAD
        self.assertEqual([10.], mod.GetTimeSeries('EXT_FX__NET_CAD'))
        # The supply in the US sector is USD $20
        self.assertEqual([20.], mod.GetTimeSeries('US_BUS__SUP_CA_GOOD'))
        # THe supply on the Canadian side is CAD $10
        self.assertEqual([10.], mod.GetTimeSeries('CA_GOOD__SUP_US_BUS'))

    def test_Market_fail_no_external(self):
        mod = Model()
        ca = Country(mod, 'CA', 'Canada', currency='CAD')
        us = Country(mod, 'US', 'United States', currency='USD')
        # gov_us.AddVariable('T', 'Government Taxes', '0.')
        gov_ca = Sector(ca, 'GOV', 'Gummint')
        gov_ca.AddVariable('DEM_GOOD', 'desc', '20.')
        market = Market(ca, 'GOOD', 'Market')
        supplier_ca = Sector(ca, 'BUS', 'Canada supplier')
        supplier_us = Sector(us, 'BUS', 'US Supplier')
        # Set supply so that CAD$10 is paid to each supplier.
        market.AddSupplier(supplier_ca)
        market.AddSupplier(supplier_us, '10.')
        # Set CAD = 2, so 2 USD = 1 CAD (USD is weaker.)
        with self.assertRaises(LogicError):
            mod._GenerateFullSectorCodes()
            market._GenerateEquations()

    @unittest.skipIf(skip_end_to_end == 'T', 'Slow test excluded')
    def test_GoldSectors(self):
        # Relatively big test, but it takes a lot of work to get a model
        # where we can create a GoldStandardCentralBank, and to set up the
        # equations so that they need to intervene.
        # Consider this an end-to-end test.
        mod = Model()
        ext = ExternalSector(mod)
        ca = Country(mod, 'CA', 'Canada', currency='CAD')
        us = Country(mod, 'US', 'United States', currency='USD')
        gov_us = GoldStandardGovernment(us, 'GOV')

        # gov_ca = GoldStandardGovernment(ca, 'CA Gov', 'GOV', 200.)
        tre_ca = Treasury(ca, 'TRE', 'Ministry of Finance')
        cb_ca = GoldStandardCentralBank(ca, 'CB', treasury=tre_ca)
        mon = MoneyMarket(ca, issuer_short_code='CB')
        dep = DepositMarket(ca, issuer_short_code='TRE')
        gov_us.AddVariable('T', 'Government Taxes', '0.')
        tre_ca.AddVariable('T', 'Government Taxes', '0.')

        tre_ca.SetEquationRightHandSide('DEM_GOOD', '20.')
        market = Market(ca, 'GOOD', 'Market')
        supplier_ca = Sector(ca, 'BUS', 'Canada supplier')
        supplier_us = Sector(us, 'BUS', 'US Supplier')
        market.AddSupplier(supplier_ca)
        market.AddSupplier(supplier_us, '10.')
        mod.EquationSolver.MaxTime = 1
        mod.EquationSolver.MaxIterations = 90
        mod.EquationSolver.ParameterErrorTolerance = 1e-1
        mod.main()
        mod.TimeSeriesSupressTimeZero = True
        # markets should be balanced
        self.assertAlmostEqual(0., mod.GetTimeSeries('EXT_FX__NET_CAD')[0], places=2)
        self.assertAlmostEqual(0., mod.GetTimeSeries('EXT_FX__NET_USD')[0], places=2)
        # U.S. buys 10 units of GOLD
        self.assertAlmostEqual(10., mod.GetTimeSeries('US_GOV__GOLDPURCHASES')[0], places=2)
        # Canada sells 10 units
        self.assertAlmostEqual(-10., mod.GetTimeSeries('CA_CB__GOLDPURCHASES')[0], places=2)

    def test_MissingExternalForGoldSectors(self):
        mod = Model()
        ca = Country(mod, 'CA', 'Canada')
        gov = GoldStandardGovernment(ca, 'GOV', ' ', 1000.)
        with self.assertRaises(LogicError):
            gov._GenerateEquations()
        tre = Treasury(ca, 'TRE', 'FinMin')
        cb = GoldStandardCentralBank(ca, 'CB', 'desc', treasury=tre)
        with self.assertRaises(LogicError):
            cb._GenerateEquations()


