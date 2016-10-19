"""
models.py
==========


Core classes for machine-generated equations.
"""


class Entity(object):
    """
    Entity class
    Base class for all model entities. Gives them a unique numeric id to make debugging easier.

    Can create function for displaying, etc.
    """
    ID = 0

    def __init__(self, parent = None):
        self.ID = Entity.ID
        Entity.ID += 1
        self.Parent = parent
        self.Code = ''
        self.LongName = ''


class Model(Entity):
    """
    Model class.
    All other entities live within a model.
    """

    def __init__(self):
        Entity.__init__(self)
        self.CountryList = []

    def AddCountry(self, country):
        """
        Add a country to the list.
        :param country: Country
        :return: None
        """
        self.CountryList.append(country)

    def GenerateFullSectorCodes(self):
        """
        Create full sector names (which is equal to '[country.Code]_[sector.Code]' - if there is more than one country.
        Equals the sector code otherwise.
        :return: None
        """
        add_country_code =  len(self.CountryList) > 1
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                if add_country_code:
                    sector.FullCode = cntry.Code + '_' + sector.Code
                else:
                    sector.FullCode = sector.Code


class Country(Entity):
    """
    Country class. Somewhat redundant in a closed economy model, but we need for multi-region models.
    """

    def __init__(self, model, long_name, code):
        Entity.__init__(self, model)
        self.Code = code
        self.LongName = long_name
        model.AddCountry(self)
        self.SectorList = []

    def AddSector(self, sector):
        self.SectorList.append(sector)


class Sector(Entity):
    """
    All sectors derive from this class.
    """
    def __init__(self, country, long_name, code):
        Entity.__init__(self, country)
        country.AddSector(self)
        self.Code = code
        # This is calculated by the Model
        self.FullCode = ''
        self.LongName = long_name
        self.VariableDescription = {}
        self.Equations = {}

    def AddVariable(self, varname, desc, eqn):
        self.VariableDescription[varname] = desc
        self.Equations[varname] = eqn

    def GetVariables(self):
        """
        Return a sorted list of variables.

        (Need to sort to make testing easier; dict's store in "random" hash order.
        :return: list
        """
        variables = list(self.Equations.keys())
        variables.sort()
        return variables













