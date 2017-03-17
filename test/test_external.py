from unittest import TestCase

from sfc_models.models import Model, Country
from sfc_models.sector import Sector
from sfc_models.external import ExternalSector, ExchangeRates, ForexTransations

class TestExternalSector(TestCase):
    def test_ctor_1(self):
        mod = Model()
        ext = ExternalSector(mod)
        # Check that these sectors exist
        xr = ext['XR']
        fx = ext['FX']
        self.assertIs(ExchangeRates, type(xr))
        self.assertIn('NUMERAIRE', xr.EquationBlock)
        self.assertIs(ForexTransations, type(fx))

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
        ca = Country(mod, 'Canada', 'CA', currency='CAD')
        hh_ca = Sector(ca, 'Canada HH', 'HH')
        hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
        fx = ext['FX']
        mod._GenerateFullSectorCodes()
        fx._SendMoney(hh_ca, 'GIFT')
        self.assertEqual('CA_HH__GIFT', fx.EquationBlock['NET_CAD'].RHS())

    def test_ReceiveMoney(self):
        mod = Model()
        ext = ExternalSector(mod)
        ca = Country(mod, 'Canada', 'CA', currency='CAD')
        us = Country(mod, 'U.S.', 'US', currency='USD')
        hh_ca = Sector(ca, 'Canada HH', 'HH')
        hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
        hh_us = Sector(us, 'Household', 'HH')
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
        ca = Country(mod, 'Canada', 'CA', currency='CAD')
        us = Country(mod, 'United States', 'US', currency='USD')
        hh_ca = Sector(ca, 'Canada HH', 'HH')
        hh_us = Sector(us, 'US HH', 'HH')
        hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
        xr = ext['XR']
        xr.SetExogenous('CAD', '[1.5,]*100')
        mod.EquationSolver.MaxTime = 3
        mod.RegisterCashFlow(hh_ca, hh_us, 'GIFT', False, True)
        mod.main()
        testfn = mod.GetTimeSeries
        self.assertEqual([0., -5., -10., -15.], testfn('CA_HH__F'))
        self.assertEqual([5., 5., 5., 5.], testfn('EXT_FX__NET_CAD'))
        self.assertEqual([0, -7.5, -7.5, -7.5], testfn('EXT_FX__NET_USD'))
        self.assertEqual([0., 0., 0., 0.], testfn('EXT_FX__NET_NUMERAIRE'))


