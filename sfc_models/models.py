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
import traceback

import sfc_models.equation_solver
import sfc_models.iterative_machine_generator as iterative_machine_generator
from sfc_models.equation_parser import EquationParser
from sfc_models.utils import Logger


class Entity(object):
    """
    Entity class
    Base class for all model entities. Gives them a unique numeric id to make debugging easier.

    Can create function for displaying, etc.
    """
    ID = 0

    def __init__(self, parent=None):
        self.ID = Entity.ID
        Entity.ID += 1
        self.Parent = parent
        self.Code = ''
        self.LongName = ''
        Logger('{0} Created, ID={1}', priority=2, data_to_format=(type(self), self.ID))

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

        :param base_file_name: str
        :return:
        """
        # Skip testing, this, rather test underlying steps.
        # Once we have a solid end-to-end test (which is easier now), can test this.
        try:
            if base_file_name is not None:
                Logger.register_standard_logs(base_file_name)
            Logger('Starting Model main()')
            self.GenerateFullSectorCodes()
            self.GenerateEquations()
            self.FixAliases()
            self.GenerateRegisteredCashFlows()
            self.GenerateIncomeEquations()
            self.ProcessExogenous()
            self.FinalEquations = self.CreateFinalEquations()
            self.EquationSolver.ParseString(self.FinalEquations)
            self.EquationSolver.SolveEquation()
            self.LogInfo()
        except Exception as e:
            self.LogInfo(ex=e)
            raise
        finally:
            Logger(self.EquationSolver.GenerateCSVtext(), 'timeseries')
            Logger.cleanup()
        return self.FinalEquations

    def _main_deprecated(self, base_file_name=None):  # pragma: no cover
        """
        This method is deprecated; only keeping until examples are reworked to use new system.

        Builds model, once all sector and exogenous definitions are in place.
        :return: str
        """
        # Excluded from unit test coverage for now. The components are all tested; this function is really a
        # end-to-end test. Only include in coverage once output file format is finalised.
        try:
            if base_file_name is not None:
                Logger.register_standard_logs(base_file_name)
            self.GenerateFullSectorCodes()
            self.GenerateEquations()
            self.GenerateRegisteredCashFlows()
            self.GenerateIncomeEquations()
            self.ProcessExogenous()
            self.FinalEquations = self.CreateFinalEquations()
            if base_file_name is not None:
                model_file = base_file_name + '.py'
                obj = iterative_machine_generator.IterativeMachineGenerator(self.FinalEquations,
                                                                            run_equation_reduction=True)
                obj.main(model_file)
                self.LogInfo()
            else:
                # noinspection PyUnusedLocal
                solver = sfc_models.equation_solver.EquationSolver(self.FinalEquations)
        except Exception as e:
            self.LogInfo(ex=e)
            raise
        finally:
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
        self.IncomeExclusions.append((sector, cash_flow_name))

    def RegisterAlias(self, alias, sector, varname):
        self.Aliases[alias] = (sector, varname)

    def AddGlobalEquation(self, var, description, eqn):
        """
        Add a variable that is not associated with a sector.
        :param var: str
        :param description: str
        :param eqn: str
        :return: None
        """
        self.GlobalVariables.append((var, eqn, description))

    def GetSectors(self):
        out = []
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out.append(sector)
        return out

    def GetTimeSeries(self, series, cutoff=None):
        """

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

    def FixAliases(self):
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
        if generate_full_codes:
            self.GenerateFullSectorCodes()
            for c in self.CountryList:
                Logger('Country: Code= "%s" %s\n' % (c.Code, c.LongName))
                Logger('=' * 60 + '\n\n')
                for s in c.SectorList:
                    Logger(s.Dump() + '\n')
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
        self.CountryList.append(country)

    def GenerateFullSectorCodes(self):
        """
        Create full sector names (which is equal to '[country.Code]_[sector.Code]' - if there is more than one country.
        Equals the sector code otherwise.
        :return: None
        """
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
        :param sector:
        :return:
        """
        return '{0}_{1}'.format(sector.Parent.Code, sector.Code)

    def RegisterCashFlow(self, source_sector, target_sector, amount_variable):
        # if amount_variable not in source_sector.Equations:
        #     raise KeyError('Must define the variable that is the amount of the cash flow')
        self.RegisteredCashFlows.append((source_sector, target_sector, amount_variable))

    def GenerateRegisteredCashFlows(self):
        for source_sector, target_sector, amount_variable in self.RegisteredCashFlows:
            full_variable_name = source_sector.GetVariableName(amount_variable)
            source_sector.AddCashFlow('-' + full_variable_name, eqn=None)
            target_sector.AddCashFlow('+' + full_variable_name, eqn=None)

    def LookupSector(self, fullcode):
        for cntry in self.CountryList:
            try:
                s = cntry.LookupSector(fullcode, is_full_code=True)
                return s
            except KeyError:
                pass
        raise KeyError('Sector with FullCode does not exist: ' + fullcode)

    def ProcessExogenous(self):
        for sector_code, varname, eqn in self.Exogenous:
            if type(sector_code) is str:
                sector = self.LookupSector(sector_code)
            else:
                sector = sector_code
            if varname not in sector.EquationBlock.Equations:
                raise KeyError('Sector %s does not have variable %s' % (sector_code, varname))
            # Need to mark exogenous variables
            sector.SetEquationRightHandSide(varname, 'EXOGENOUS ' + eqn)

    def GenerateInitialConditions(self):
        out = []
        for sector_code, varname, value in self.InitialConditions:
            sector = self.LookupSector(sector_code)
            if varname not in sector.EquationBlock.Equations:
                raise KeyError('Sector %s does not have variable %s' % (sector_code, varname))
            out.append(('%s(0)' % (sector.GetVariableName(varname),), value, 'Initial Condition'))
        return out

    def GenerateEquations(self):
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                sector.GenerateEquations()

    def DumpEquations(self):
        out = ''
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out += sector.Dump()
        return out

    def GenerateIncomeEquations(self):
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
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
        out.extend(self.GenerateInitialConditions())
        out.extend(self.GlobalVariables)
        return self.FinalEquationFormatting(out)

    def FinalEquationFormatting(self, out):
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


