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
from __future__ import print_function

import traceback

import sfc_models.equation_solver
from sfc_models.equation_parser import EquationParser
from sfc_models.utils import Logger


class Entity(object):
    """
    Entity class
    Base class for model entities. Gives them a unique numeric id to make debugging and
    some coding tasks easier. For example, if two Entity's have a different ID, they are distinct,
    and so an Entity can exclude itself when iterating through a list of Sector objects.

    Can create function for displaying, etc.
    """
    ID = 0

    def __init__(self, parent=None):
        self.ID = Entity.ID
        Entity.ID += 1
        self.Parent = parent
        self.Code = ''
        self.LongName = ''
        Logger('Entity Created: {0} ID = {1}', priority=1, data_to_format=(type(self),self.ID))

    def GetModel(self):
        """
        Get the base object of the hierarchy (which should be a Model).
        :return: Model
        """
        obj = self
        while obj.Parent is not None:
            obj = obj.Parent
        return obj

    def ShareParent(self, other):
        """
        Does this entity have the same parent?
        :param other:  Entity
        :return: bool
        """
        return self.Parent == other.Parent

class Model(Entity):
    """
    Model class.

    All other entities live within a model.
    """

    def __init__(self):
        """
        Create the Model object. All the economic class objects (Country, Sector) live within
        a Model.

        Unlike other Entity subclasses, the Model object is a base object, and has no parent.

        It is possible for two Model objects to coexist; there is no interaction between them
        (other than side effects from global Parameters).
        """
        Entity.__init__(self)
        self.CountryList = []
        self.Exogenous = []
        self.InitialConditions = []
        self.FinalEquations = '<To be generated>'
        self.MaxTime = 100
        self.RegisteredCashFlows = []
        self.Aliases = {}
        self.TimeSeriesCutoff = None
        self.TimeSeriesSupressTimeZero = False
        self.EquationSolver = sfc_models.equation_solver.EquationSolver()
        self.GlobalVariables = []
        self.IncomeExclusions = []

    def main(self, base_file_name=None):  # pragma: no cover
        """
        Routine that does most of the work of model building. The model is build based upon
        the Sector objects that have been registered as children of this Model.

        The base_file_name is the base filename that is used for Logging operations; just used
        to call Logger.register_standard_logs(base_file_name). It is recommended that you call
        Logger.register_standard_logs() before main, so that Sector creation can be logged.

        The major operations:
        [1] Call GenerateEquations() on all Sectors. The fact that GenerateEquations() is only
         called now at the Sector level means that Sectors can be created independently, and the
        GenerateEquations() call which ties it to other sectors is only called after all other sectors
        are created. (There is at least one exception where Sectors have to be created in a specific
        order, which we want to avoid.)

        [2] Cleanup work: processing initial conditions, exogenous variables, replacing
            aliases in equations.

        [3] Tie the sector level equations into a single block of equations. (Currently strings, not
            Equation objects.)

        [4] The equations are passed to self.EquationSolver, and they are solved.

        The user can then use GetTimeSeries() to access the output time series (if they can be
        calculated.)

        :param base_file_name: str
        :return: None
        """
        # Skip testing, this, rather test underlying steps.
        # Once we have a solid end-to-end test (which is easier now), can test this.
        try:
            if base_file_name is not None:
                Logger.register_standard_logs(base_file_name)
            Logger('Starting Model main()')
            self._GenerateFullSectorCodes()
            self._GenerateEquations()
            self._FixAliases()
            self._GenerateRegisteredCashFlows()
            self._ProcessExogenous()
            self.FinalEquations = self._CreateFinalEquations()
            self.EquationSolver.ParseString(self.FinalEquations)
            self.EquationSolver.SolveEquation()
            self.LogInfo()
        except Warning as e:
            self.LogInfo(ex=e)
            print('Warning triggered: ' + str(e))
            return self.FinalEquations
        except Exception as e:
            self.LogInfo(ex=e)
            raise
        finally:
            Logger(self.EquationSolver.GenerateCSVtext(), 'timeseries')
            Logger.cleanup()
        return self.FinalEquations

    def AddExogenous(self, sector_fullcode, varname, value):
        """
        Add an exogenous variable to the model. Overwrites an existing variable definition.
        Need to use the full sector code.

        Exogenous variables are sepcified as time series, which are implemented as list variables ([1, 2, 3,...])
        The exogenous variable can either be specified as a string (which can be evaluated to a list), or else
        as a list object. The list object will be converted into a string representation using repr(), which
        means that it may be much longer than using something like '[20,] * 100'.

        At present, does not support the usage of specifying a constant value. For example value='20.' does
        not work, you need '[20.]*100.'

        :param sector_fullcode: str
        :param varname: str
        :param value: str
        :return:
        """
        Logger('Adding exogenous variable: {0} in {1}', priority=5,
               data_to_format=(varname, sector_fullcode))
        # If the user passes in a list or tuple, convert it to a string representation.
        if type(value) in (list, tuple):
            value = repr(value)
        self.Exogenous.append((sector_fullcode, varname, value))

    def AddInitialCondition(self, sector_fullcode, varname, value):
        """
        Set the initial condition for a variable. Need to use the full code of the sector.

        :param sector_fullcode: str
        :param varname: str
        :param value: float
        :return:
        """
        Logger('Adding initial condition: {0} in {1}', priority=5,
               data_to_format=(varname, sector_fullcode))
        # Convert the "value" to a float, in case someone uses a string
        try:
            value = float(value)
        except:
            raise ValueError('The "value" parameter for initial conditions must be a float.')
        self.InitialConditions.append((sector_fullcode, varname, str(value)))

    def AddCashFlowIncomeExclusion(self, sector, cash_flow_name):
        """
        Specify that a cash flow is to be excluded from the list of flows that go into
        income.

        Examples of such flows within economics:
        - Household consumption of goods.
        - Business investment.
        - Dividend outflows for business (inflow is income for household).
        - (Financing flows - do not really appear?)

        Note that these exclusions are generally implemented at the sector code level.
        :param sector: Sector
        :param cash_flow_name: str
        :return: None
        """
        Logger('Registering cash flow exclusion: {0} for ID={1}', priority=5,
               data_to_format=(cash_flow_name, sector.ID))
        self.IncomeExclusions.append((sector, cash_flow_name))

    def _RegisterAlias(self, alias, sector, local_variable_name):
        """
        Used by Sector objects to register aliases for local variables.

        :param alias: str
        :param sector: Sector
        :param local_variable_name: str
        :return:
        """
        Logger('Registering alias {0} for {1} in ID={2}', priority=5,
               data_to_format=(alias, local_variable_name, sector.ID))
        self.Aliases[alias] = (sector, local_variable_name)

    def AddGlobalEquation(self, var, description, eqn):
        """
        Add a variable that is not associated with a sector.
        Typical example: 't'

        :param var: str
        :param description: str
        :param eqn: str
        :return: None
        """
        Logger('Registering global equation: {0} = {1}', priority=5, data_to_format=(var, eqn))
        self.GlobalVariables.append((var, eqn, description))

    def GetSectors(self):
        """
        Returns a list of Sector objects held within this Model.

        :return: list
        """
        out = []
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out.append(sector)
        return out

    def GetTimeSeries(self, series, cutoff=None):
        """
        Convenience function to retrieve time series from the EquationSolver.

        Use cutoff to truncate the length of the output.

        If self.TimeSeriesSupressZero is True, the first point is removed (the initial
        conditions period).

        :param series: str
        :param cutoff: int
        :return: list
        """
        if cutoff is None:
            cutoff = self.TimeSeriesCutoff
        try:
            if cutoff is None:
                val = self.EquationSolver.TimeSeries[series]
            else:
                val = self.EquationSolver.TimeSeries[series][0:(cutoff + 1)]
        except KeyError:
            raise KeyError('Time series "{0}" does not exist'.format(series))
        if self.TimeSeriesSupressTimeZero:
            val.pop(0)
        return val

    def _FixAliases(self):
        """
        Assign the proper names to variables in Sector objects (that were perviously aliases).
        :return:
        """
        Logger('Fixing aliases (Model._FixAliases)', priority=3)
        lookup = {}
        for alias in self.Aliases:
            sector, varname = self.Aliases[alias]
            lookup[alias] = sector.GetVariableName(varname)
        for sector in self.GetSectors():
            sector._ReplaceAliases(lookup)

    def LogInfo(self, generate_full_codes=True, ex=None):  # pragma: no cover
        """
        Write information to a file; if there is an exception, dump the trace.
        The log will normally generate the full sector codes; set generate_full_codes=False
        to leave the Model full codes untouched.

        :param generate_full_codes: bool
        :param ex: Exception
        :return:
        """
        # Not covered with unit tests [for now]. Output format will change a lot.
        if ex is not None:
            Logger('\nError or Warning raised:\n')
            traceback.print_exc(file=Logger.get_handle())
        Logger('-'*30)
        Logger('Starting LogInfo() Data Dump')
        Logger('-'*30)
        if generate_full_codes:
            self._GenerateFullSectorCodes()
            for c in self.CountryList:
                Logger('Country: Code= "%s" %s\n' % (c.Code, c.LongName))
                Logger('=' * 60 + '\n\n')
                for s in c.SectorList:
                    Logger(s.Dump() + '\n')
        Logger('Writing LogInfo to log="eqn"')
        Logger('\n\nFinal Equations:\n', log='eqn')
        Logger(self.FinalEquations + '\n', log='eqn')
        parser = EquationParser()
        parser.ParseString(self.FinalEquations)
        parser.EquationReduction()
        Logger('\n\nReduced Equations', log='eqn')
        Logger(parser.DumpEquations(), log='eqn')
        if ex is not None:
            Logger('\n\nError raised:\n')
            traceback.print_exc(file=Logger.get_handle())

    def AddCountry(self, country):
        """
        Add a country to the list.

        :param country: Country
        :return: None
        """
        Logger('Adding Country: {0} ID={1}', data_to_format=(country.Code, country.ID))
        self.CountryList.append(country)

    def _GenerateFullSectorCodes(self):
        """
        Create full sector names (which is equal to '[country.Code]_[sector.Code]' - if there is more than one country.
        Equals the sector code otherwise.

        :return: None
        """
        Logger('Generating FullSector codes (Model._GenerateFullSectorCodes()', priority=3)
        add_country_code = len(self.CountryList) > 1
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                if add_country_code:
                    sector.FullCode = cntry.Code + '_' + sector.Code
                else:
                    sector.FullCode = sector.Code

    @staticmethod
    def GetSectorCodeWithCountry(sector):
        """
        Return the sector code including the country information.
        Need to use this if we want the FullCode before the model information
        is bound in main().

        We should not need to use this function often; generally only when we need
        FullCodes in constructors. For example, the multi-supply business sector
        needs the full codes of markets passed into the constructor.
        :param sector: Sector
        :return: str
        """
        return '{0}_{1}'.format(sector.Parent.Code, sector.Code)

    def RegisterCashFlow(self, source_sector, target_sector, amount_variable):
        """
        Register a cash flow between two sectors.

        The amount_variable is the name of the local variable within the source sector.

        TODO: Add variable indicating whether the flow affects incomes for the source and
        destination.

        :param source_sector: Sector
        :param target_sector: Sector
        :param amount_variable: str
        :return:
        """
        # if amount_variable not in source_sector.Equations:
        #     raise KeyError('Must define the variable that is the amount of the cash flow')
        Logger('Cash flow registered {0}: {1} -> {2}  [ID: {3} -> {4}]', priority=3,
               data_to_format=(amount_variable, source_sector.Code, target_sector.Code,
                               source_sector.ID, target_sector.ID))
        self.RegisteredCashFlows.append((source_sector, target_sector, amount_variable))

    def _GenerateRegisteredCashFlows(self):
        """
        Create cash flows based on those previously registered.

        :return:
        """
        Logger('Model._GenerateRegisteredCashFlows()')
        Logger('Adding {0} cash flows to sectors', priority=3,
               data_to_format=(len(self.RegisteredCashFlows),))
        for source_sector, target_sector, amount_variable in self.RegisteredCashFlows:
            full_variable_name = source_sector.GetVariableName(amount_variable)
            source_sector.AddCashFlow('-' + full_variable_name, eqn=None)
            target_sector.AddCashFlow('+' + full_variable_name, eqn=None)

    def LookupSector(self, fullcode):
        """
        Find a sector based on its FullCode.
        :param fullcode: str
        :return: Sector
        """
        for cntry in self.CountryList:
            try:
                s = cntry.LookupSector(fullcode, is_full_code=True)
                return s
            except KeyError:
                pass
        raise KeyError('Sector with FullCode does not exist: ' + fullcode)

    def _ProcessExogenous(self):
        """
        Handles the exogenous variables.

        :return: None
        """
        Logger('Processing {0} exogenous variables', priority=3, data_to_format=(len(self.Exogenous),))
        for sector_code, varname, eqn in self.Exogenous:
            if type(sector_code) is str:
                sector = self.LookupSector(sector_code)
            else:
                sector = sector_code
            if varname not in sector.EquationBlock.Equations:
                raise KeyError('Sector %s does not have variable %s' % (sector_code, varname))
            # Need to mark exogenous variables
            sector.SetEquationRightHandSide(varname, 'EXOGENOUS ' + eqn)

    def _GenerateInitialConditions(self):
        """
        Create block of equations for initial conditions.

        Validates that the variables exist.
        :return:
        """
        Logger('Generating {0} initial conditions', priority=3,
               data_to_format=(len(self.InitialConditions),))
        out = []
        for sector_code, varname, value in self.InitialConditions:
            sector = self.LookupSector(sector_code)
            if varname not in sector.EquationBlock.Equations:
                raise KeyError('Sector %s does not have variable %s' % (sector_code, varname))
            out.append(('%s(0)' % (sector.GetVariableName(varname),), value, 'Initial Condition'))
        return out

    def _GenerateEquations(self):
        """
        Call _GenerateEquations on all child Sector objects.

        :return:
        """
        Logger('Model._GenerateEquations()', priority=1)
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                sector._GenerateEquations()

    def DumpEquations(self):
        """
        Returns a string with basic information about the entities within this Model.
        Output is primitive, and aimed at debugging purposes. In other words, the format
        will change without warning.

        If you want information of a specific format, please create a specific reporting
        function for your needs.

        :return: str
        """
        out = ''
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out += sector.Dump()
        return out

    def _CreateFinalEquations(self):
        """
        Create Final equations.

        Final output, which is a text block of equations
        :return: str
        """
        Logger('Model._CreateFinalEquations()')
        out = []
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out.extend(sector._CreateFinalEquations())
        out.extend(self._GenerateInitialConditions())
        out.extend(self.GlobalVariables)
        if len(out) == 0:
            raise Warning('There are no equations in the system.')
        return self._FinalEquationFormatting(out)

    def _FinalEquationFormatting(self, out):
        """
        Convert equation information in list into formatted strings.

        :param out: list
        :return:
        """
        Logger('_FinalEquationFormatting()', priority=5)
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
        s += '\n\nMaxTime = {0}\nErr_Tolerance=0.001'.format(self.MaxTime)
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
        """
        Add a sector to this country.

        :param sector: Sector
        :return:
        """
        Logger('Adding Sector {0} To Country {1}', priority=1,
               data_to_format=(sector.Code, self.Code))
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


