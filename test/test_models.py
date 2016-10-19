from unittest import TestCase

from sfc_models.models import Entity, Model, Country, Sector

class TestEntity(TestCase):
    def test_ctor(self):
        Entity.ID = 0
        a = Entity()
        self.assertEqual(a.ID, 0)
        b = Entity(a)
        self.assertEqual(b.ID, 1)
        self.assertEqual(b.Parent.ID, 0)


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


class TestSector(TestCase):
    def test_ctor_chain(self):
        mod = Model()
        country = Country(mod, 'USA!', 'US')
        household = Sector(country, 'Household', 'HH')
        self.assertEqual(household.Parent.Code, 'US')
        self.assertEqual(household.Parent.Parent.Code, '')

    def test_GetVariables(self):
        mod = Model()
        can = Country(mod, 'Canada', 'Eh')
        can_hh = Sector(can, 'Household', 'HH')
        can_hh.AddVariable('y', 'Vertical axis', '2.0')
        can_hh.AddVariable('x', 'Horizontal axis', 'y - t')
        self.assertEqual(can_hh.GetVariables(), ['x', 'y'])



