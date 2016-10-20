"""
models.py
==========


Core classes for machine-generated equations.

Copyright 2016 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from sfc_models.utils import LogicError, replace_token_from_lookup

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
        self.Exogenous = []

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

    def LookupSector(self, fullcode):
        for cntry in self.CountryList:
            try:
                s = cntry.LookupSector(fullcode, is_full_code=True)
                return s
            except KeyError:
                pass
        raise KeyError('Sector with FullCode does not exist: ' + fullcode)

    def ForceExogenous(self):
        for sector_code, varname, eqn in self.Exogenous:
            sector = self.LookupSector(sector_code)
            if varname not in sector.Equations:
                raise KeyError('Sector %s does not have variable %s' % (sector_code, varname))
            # Need to mark exogenous variables
            sector.Equations[varname] = 'EXOGENOUS '+eqn


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


    def CreateFinalEquations(self):
        """
        Create Final equations.

        Final output, which is a text block of equations
        :return: str
        """
        out = []
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out.extend(sector.CreateFinalEquations())
        endo = []
        exo = []
        for row in out:
            if 'EXOGENOUS' in row[1]:
                new_eqn = row[1].replace('EXOGENOUS', '')
                exo.append((row[0], new_eqn, row[2]))
            else:
                endo.append(row)
        max0 = max([len(x[0]) for x in out])
        max1 = max([len(x[1]) for x in out])
        formatter = '%<max0>s = %-<max1>s  # %s'
        formatter = formatter.replace('<max0>', str(max0))
        formatter = formatter.replace('<max1>', str(max1))
        endo = [formatter % x for x in endo]
        exo = [formatter % x for x in exo]
        s = '\n'.join(endo) + '\n\n# Exogenous Variables\n\n' + '\n'.join(exo)
        return s


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

    def LookupSector(self, code, is_full_code=False):
        """
        Get the sector object via code or fullcode
        :param code: str
        :param is_full_code: bool
        :return: Sector
        """
        if is_full_code:
            for s in self.SectorList:
                if s.FullCode == code:
                    return s
        else:
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
        self.CreateEquationFromTerms('INC', self.INC)
        self.CreateEquationFromTerms('NET', self.NET)

    def CreateEquationFromTerms(self, varname, terms):
        if len(terms) == 0:
            self.Equations[varname] = ''
            return
        if terms[0][0] == '+':
            terms[0] = terms[0].replace('+', '')
        eqn = ''.join(terms)
        self.Equations[varname] = eqn

    def CreateFinalEquations(self):
        out = []
        lookup = {}
        if self.Code == 'HH':
            print('in')
        for varname in self.Equations:
            lookup[varname] = self.GetVariableName(varname)
        for varname in self.Equations:
            out.append((self.GetVariableName(varname),
                        replace_token_from_lookup(self.Equations[varname], lookup),
                        self.VariableDescription[varname]))
        return out





class Household(Sector):
    def __init__(self, country, long_name, code, alpha_income, alpha_fin):
        Sector.__init__(self, country, long_name, code)
        self.AlphaIncome = alpha_income
        self.AlphaFin = alpha_fin
        self.AddVariable('AlphaIncome', 'Parameter for consumption out of income', '%0.4f' % (self.AlphaIncome,))
        self.AddVariable('AlphaFin', 'Parameter for consumption out of financial assets', '%0.4f' % (self.AlphaFin,))
        self.AddVariable('DEM_GOOD', 'Expenditure on goods consumption', 'AlphaIncome * NET + AlphaFin * LAG_F')
        self.AddVariable('SUP_LAB', 'Supply of Labour', '<To be determined>')

    def GenerateEquations(self):
        """
        Set up the equations for the household
        :return: None
        """
        pass

class DoNothingGovernment(Sector):
    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code)
        self.AddVariable('DEM_GOOD', 'Government Consumption of Goods', '0.0')

    def GenerateEquations(self):
        """
        Set up the equations for the household
        :return: None
        """
        pass



class TaxFlow(Sector):
    """
    TaxFlow: Not really a sector, but keep it in the same list
    """

    def __init__(self, country, long_name, code, taxrate):
        Sector.__init__(self, country, long_name, code, has_sector_variables=False)
        self.TaxRate = taxrate

    def GenerateEquations(self):
        hh = self.Parent.LookupSector('HH')
        hh_name = hh.GetVariableName('SUP_LAB')
        self.AddVariable('TaxRate', 'Tax rate', '%0.4f' % (self.TaxRate,))
        self.AddVariable('T', 'Taxes Paid', 'TaxRate * %s' % (hh_name, ))
        tax_fullname = self.GetVariableName('T')
        hh.AddCashFlow('-' + tax_fullname, affects_net=True)
        gov = self.Parent.LookupSector('GOV')
        gov.AddCashFlow(tax_fullname, affects_net=True)


class Market(Sector):
    """
    Market Not really a sector, but keep it in the same list
    """

    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code, has_sector_variables=False)
        self.IsMarket = True
        self.AffectsNet = True
        self.NumSupply = 0

    def GenerateEquations(self):
        self.NumSupply = 0
        self.GenerateTermsLowLevel('SUP', 'Supply')
        if self.NumSupply == 0:
            raise ValueError('No supply for market: ' + self.FullCode)
        if self.NumSupply > 1:
            raise NotImplementedError('More than one supply for a market is not yet supported: ' + self.Code)
        self.GenerateTermsLowLevel('DEM', 'Demand')
        if self.NumSupply == 1:
            self.FixSingleSupply()

    def GenerateTermsLowLevel(self, prefix, long_desc):
        if prefix not in ('SUP', 'DEM'):
            raise LogicError('Input to function must be "SUP" or "DEM"')
        country = self.Parent
        var_name = prefix + '_' + self.Code
        self.AddVariable(var_name, long_desc + ' for Market ' + self.Code, '')
        term_list = []
        for s in country.SectorList:
            if s.ID == self.ID:
                continue
            try:
                term = s.GetVariableName(var_name)
            except KeyError:
                continue
            term_list.append('+ ' + term)
            if prefix == 'SUP':
                s.AddCashFlow(term, affects_net=True)
                self.NumSupply += 1
            else:
                s.AddCashFlow('-' + term, affects_net=self.AffectsNet)
        self.CreateEquationFromTerms(var_name, term_list)

    def FixSingleSupply(self):
        if self.NumSupply != 1:
            raise LogicError('Can only call this function with a single supply source!')
        country = self.Parent
        sup_name = 'SUP_' + self.Code
        dem_name = 'DEM_' + self.Code
        self.Equations[sup_name] = dem_name
        for s in country.SectorList:
            if s.ID == self.ID:
                continue
            if sup_name in s.Equations:
                s.Equations[sup_name] = self.Equations[dem_name]
                return
























