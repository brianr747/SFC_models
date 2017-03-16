from unittest import TestCase

from sfc_models.models import Model, Country
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


