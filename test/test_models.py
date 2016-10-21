from unittest import TestCase

from sfc_models.models import *


class TestEntity(TestCase):
    def test_ctor(self):
        Entity.ID = 0
        a = Entity()
        self.assertEqual(a.ID, 0)
        b = Entity(a)
        self.assertEqual(b.ID, 1)
        self.assertEqual(b.Parent.ID, 0)

class Stub(object):
    """
    Use the stub_fun to count how many times a method has been called.
    Used for testing the iteration in the Model class; the output depends upon the sector,
    which are tested separately.
    """
    def __init__(self):
        self.Count = 0

    def stub_fun(self):
        self.Count += 1

    def stub_return(self):
        self.Count += 1
        return [(str(self.Count), 'a', 'b')]

class TestModel(TestCase):
    def test_GenerateFullCodes_1(self):
        mod = Model()
        country = Country(mod, 'USA!', 'US')
        household = Sector(country, 'Household', 'HH')
        mod.GenerateFullSectorCodes()
        self.assertEqual(household.FullCode, 'HH')

    def test_GenerateFullCodes_2(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        can = Country(mod, 'Canada', 'Eh?')
        household = Sector(us, 'Household', 'HH')
        can_hh = Sector(can, 'Household', 'HH')
        mod.GenerateFullSectorCodes()
        self.assertEqual(household.FullCode, 'US_HH')
        self.assertEqual(can_hh.FullCode, 'Eh?_HH')

    def test_LookupSector(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        can = Country(mod, 'Canada', 'Eh?')
        household = Sector(us, 'Household', 'HH')
        can_hh = Sector(can, 'Household', 'HH')
        mod.GenerateFullSectorCodes()
        self.assertEqual(household, mod.LookupSector('US_HH'))
        self.assertEqual(can_hh, mod.LookupSector('Eh?_HH'))
        with self.assertRaises(KeyError):
            mod.LookupSector('HH')

    def test_ForceExogenous(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        household = Sector(us, 'Household', 'HH')
        mod.GenerateFullSectorCodes()
        mod.Exogenous = [('HH', 'F', 'TEST')]
        mod.ForceExogenous()
        self.assertEqual('EXOGENOUS TEST', household.Equations['F'])

    def test_ForceExogenous2(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        household = Sector(us, 'Household', 'HH')
        mod.GenerateFullSectorCodes()
        mod.Exogenous = [('HH', 'Foo', 'TEST')]
        with self.assertRaises(KeyError):
            mod.ForceExogenous()

    def test_GenerateEquations(self):
        # Just count the number if times the stub is called
        stub = Stub()
        mod = Model()
        us = Country(mod, 'USA', 'US')
        h1 = Sector(us, 'Household', 'HH')
        h2 = Sector(us, 'Capitalists', 'CAP')
        h1.GenerateEquations = stub.stub_fun
        h2.GenerateEquations = stub.stub_fun
        mod.GenerateEquations()
        self.assertEqual(2, stub.Count)

    def test_GenerateIncomeEquations(self):
        stub = Stub()
        mod = Model()
        us = Country(mod, 'USA', 'US')
        h1 = Sector(us, 'Household', 'HH')
        h1.GenerateIncomeEquations = stub.stub_fun
        mod.GenerateIncomeEquations()
        self.assertEqual(1, stub.Count)

    def test_CreateFinalFunctions(self):
        stub = Stub()
        mod = Model()
        us = Country(mod, 'USA', 'US')
        h1 = Sector(us, 'Household', 'HH')
        h2 = Sector(us, 'Household2', 'H2')
        h1.CreateFinalEquations = stub.stub_return
        h2.CreateFinalEquations = stub.stub_return
        out = mod.CreateFinalEquations()
        out = out.split('\n')
        self.assertTrue('1' in out[0])
        self.assertTrue('2' in out[1])

    def test_FinalEquationFormating(self):
        eq = [('x', 'y + 1', 'comment_x'),
              ('y', 'EXOGENOUS 20', 'comment_y'),
              ('z', 'd', 'comment_z')]
        out = Model.FinalEquationFormatting(eq)
        # Remove spaces; what matters is the content
        out = out.replace(' ', '').split('\n')
        target = ['x=y+1#comment_x', 'z=d#comment_z', '', '#ExogenousVariables', '', 'y=20#comment_y']
        self.assertEqual(target, out)





    # def test_CreateFinalFunctions2(self):
    #     stub = Stub()
    #     mod = Model()
    #     us = Country(mod, 'USA', 'US')
    #     h1 = Sector(us, 'Household', 'HH')
    #     h2 = Sector(us, 'Household2', 'H2')
    #     h1.CreateFinalEquations = stub.stub_return
    #     h2.CreateFinalEquations = stub.stub_return
    #     out = mod.CreateFinalEquations()
    #     out = out.split('\n')
    #     self.assertTrue('1' in out[0])
    #     self.assertTrue('2' in out[1])

class TestSector(TestCase):
    def test_ctor_chain(self):
        mod = Model()
        country = Country(mod, 'USA! USA!', 'US')
        household = Sector(country, 'Household', 'HH')
        self.assertEqual(household.Parent.Code, 'US')
        self.assertEqual(household.Parent.Parent.Code, '')

    def test_GetVariables(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        can_hh = Sector(can, 'Household', 'HH')
        can_hh.AddVariable('y', 'Vertical axis', '2.0')
        can_hh.AddVariable('x', 'Horizontal axis', 'y - t')
        self.assertEqual(can_hh.GetVariables(), ['F', 'LAG_F', 'x', 'y'])

    def test_GetVariableName_2(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        can = Country(mod, 'Canada', 'Eh?')
        household = Household(us, 'Household', 'HH', .9, .2)
        mod.GenerateFullSectorCodes()
        household.GenerateEquations()
        self.assertEqual(household.GetVariableName('AlphaFin'), 'US_HH_AlphaFin')


    def test_GetVariableName_1(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        household = Household(us, 'Household', 'HH', .9, .2)
        mod.GenerateFullSectorCodes()
        household.GenerateEquations()
        self.assertEqual(household.GetVariableName('AlphaFin'), 'HH_AlphaFin')

    def test_AddCashFlow(self):
        mod = Model()
        us = Country(mod, 'USA', 'US')
        s = Sector(us, 'Household', 'HH')
        s.AddCashFlow('A', 'H_A', 'Desc A')
        s.AddCashFlow('- B', 'H_B', 'Desc B')
        s.AddCashFlow(' - C', 'H_C', 'Desc C')
        self.assertEqual(['+A','-B','-C'], s.CashFlows)


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


class TestCountry(TestCase):
    def test_AddSector(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        self.assertEqual(can.SectorList[0].ID, gov.ID)


    def test_LookupSector(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        gov = DoNothingGovernment(can, 'Government', 'GOV')
        hh = Household(can, 'Household', 'HH', .9, .2)
        self.assertEqual(can.LookupSector('HH').ID, hh.ID)
        self.assertEqual(can.LookupSector('GOV').ID, gov.ID)
        with self.assertRaises(KeyError):
            can.LookupSector('Smurf')



