"""
models.py
==========


Core classes for machine-generated equations.
"""

from sfc_models.utils import LogicError

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

    def GenerateEquations(self):
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                sector.GenerateEquations()

    def DumpEquations(self):  # pragma: no cover
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                sector.DumpEquations()

    def GenerateIncomeEquations(self):
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                if sector.HasSectorVariables:
                    sector.GenerateIncomeEquations()




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

    def LookupSector(self, code):
        """
        Get the sector object via code
        :param code: str
        :return: Sector
        """
        for s in self.SectorList:
            if s.Code == code:
                return s
        raise KeyError('Sector does not exist - ' + code)


class Sector(Entity):
    """
    All sectors derive from this class.
    """
    def __init__(self, country, long_name, code, has_sector_variables=True):
        Entity.__init__(self, country)
        self.HasSectorVariables = has_sector_variables
        self.IsMarket = False
        country.AddSector(self)
        self.Code = code
        # This is calculated by the Model
        self.FullCode = ''
        self.LongName = long_name
        self.VariableDescription = {}
        self.Equations = {}
        if has_sector_variables:
            self.AddVariable('INC', 'Income', '<TO BE GENERATED>')
            self.AddVariable('NET', 'Net Income', '<TO BE GENERATED>')
            self.AddVariable('F', 'Financial assets', 'LAG_F + INC')
            self.AddVariable('LAG_F', 'Previous period''s financial assets.', 'F(k-1)')
            self.INC = []
            self.NET = []

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

    def GetVariableName(self, varname):
        """

        :param varname: str
        :return: str
        """

        if self.FullCode == '':
            raise LogicError('Must generate FullCode before calling GetVariableName')
        if varname not in self.Equations:
            raise KeyError('Variable %s not in sector %s' % (varname, self.FullCode))
        return self.FullCode + '_' + varname

    def AddCashFlow(self, term, affects_net):
        term = term.strip()
        if len(term) == 0:
            return
        if not (term[0] in ('+', '-')):
            term = '+' + term
        self.INC.append(term)
        if affects_net:
            self.NET.append(term)

    def GenerateEquations(self):
        pass

    def DumpEquations(self):  # pragma: no cover
        print('[%s - %s]' % (self.Code, self.LongName))
        for var in self.Equations:
            print('%s = %s' % (var, self.Equations[var]))


    def GenerateIncomeEquations(self):
        if not self.HasSectorVariables:
            raise LogicError('Does not have income equations')
        self.GenerateIncomeLowLevel('INC', self.INC)
        self.GenerateIncomeLowLevel('NET', self.NET)

    def GenerateIncomeLowLevel(self, varname, terms):
        if len(terms) == 0:
            self.Equations[varname] = ''
            return
        if terms[0][0] == '+':
            terms[0] = terms[0].replace('+', '')
        eqn = ''.join(terms)
        self.Equations[varname] = eqn



class Household(Sector):
    def __init__(self, country, long_name, code, alpha_income, alpha_fin):
        Sector.__init__(self, country, long_name, code)
        self.AlphaIncome = alpha_income
        self.AlphaFin = alpha_fin
        self.AddVariable('AlphaIncome', 'Parameter for consumption out of income', '%0.4f' % (self.AlphaIncome,))
        self.AddVariable('AlphaFin', 'Parameter for consumption out of financial assets', '%0.4f' % (self.AlphaFin,))
        self.AddVariable('DEM_GOOD', 'Expenditure on goods consumption', 'alphaIncome * NET + alphaFin * LAG_F')
        self.AddVariable('SUP_LAB', 'Supply of Labour', '<To be determined>')

    def GenerateEquations(self):
        """
        Set up the equations for the household
        :return: None
        """
        self.Equations['SUP_LAB'] = 'INFINITY!'

class DoNothingGovernment(Sector):
    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')

    def GenerateEquations(self):
        """
        Set up the equations for the household
        :return: None
        """



class TaxFlow(Sector):
    """
    TaxFlow: Not really a sector, but keep it in the same list
    """

    def __init__(self, country, long_name, code, taxrate):
        Sector.__init__(self, country, long_name, code, has_sector_variables=False)
        self.TaxRate = taxrate

    def GenerateEquations(self):
        hh = self.Parent.LookupSector('HH')
        hh_name = hh.GetVariableName('INC')
        self.AddVariable('TaxRate', 'Tax rate', '%0.4f' % (self.TaxRate,))
        self.AddVariable('T', 'Taxes Paid', 'TaxRate * %s' % (hh_name, ))
        tax_fullname = self.GetVariableName('T')
        hh.AddCashFlow('-T', affects_net=True)
        gov = self.Parent.LookupSector('GOV')
        gov.AddCashFlow('T', affects_net=True)


class Market(Sector):
    """
    Market Not really a sector, but keep it in the same list
    """

    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code, has_sector_variables=False)
        self.IsMarket = True

    def GenerateEquations(self):
        self.GenerateTermsLowLevel('SUP', 'Supply')
        self.GenerateTermsLowLevel('DEM', 'Demand')
        # Cash flows...



    def GenerateTermsLowLevel(self, prefix, long_desc):
        country = self.Parent
        var_name = prefix + '_' + self.Code
        self.AddVariable(var_name,long_desc + ' for Market ' + self.Code, '')
        term_list = []
        for s in country.SectorList:
            if s.ID == self.ID:
                continue
            try:
                supply = s.GetVariableName(var_name)
            except KeyError:
                continue
            term_list.append('+ ' + supply)
        self.GenerateIncomeLowLevel(var_name, term_list)























