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
from pprint import pprint
import traceback

from sfc_models.utils import LogicError, replace_token_from_lookup, create_equation_from_terms, Logger
from sfc_models.equation_parser import EquationParser
import sfc_models.iterative_machine_generator as iterative_machine_generator
import sfc_models.equation_solver



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

    def GetModel(self):
        obj = self
        while obj.Parent is not None:
            obj = obj.Parent
        return obj


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
        self.EquationSolver = sfc_models.equation_solver.EquationSolver()

    def main(self, base_file_name=None):  # pragma: no cover
        """

        :param base_file_name: str
        :return:
        """
        # Skip testing, this, rather test underlying steps.
        # Once we have a solid end-to-end test (which is easier now), can test this.
        try:
            if base_file_name is not None:
                log_file = base_file_name + '_log.txt'
                Logger.log_file_handle = open(log_file, 'w')
            self.GenerateFullSectorCodes()
            self.FixAliases()
            self.GenerateEquations()
            self.GenerateRegisteredCashFlows()
            self.GenerateIncomeEquations()
            self.ProcessExogenous()
            self.FinalEquations = self.CreateFinalEquations()
            self.EquationSolver = sfc_models.equation_solver.EquationSolver(self.FinalEquations)
            # The following looks wierd, but we can write out a csv of the time series up until the
            # point when convergence fails
            try:
                converge_error = None
                self.EquationSolver.SolveEquation()
            except sfc_models.equation_solver.ConvergenceError as c:
                converge_error = c
            if base_file_name is not None:
                self.EquationSolver.WriteCSV(base_file_name + '_out.txt')
            if converge_error is not None:
                raise converge_error
            self.LogInfo()
        except Exception as e:
            self.LogInfo(ex=e)
            raise
        finally:
            Logger.cleanup()
        return self.FinalEquations

    def main_deprecated(self, base_file_name=None):  # pragma: no cover
        """
        This method is deprecated; only keeping until examples are reworked to use new system.

        Builds model, once all sector and exogenous definitions are in place.
        :return: str
        """
        # Excluded from unit test coverage for now. The components are all tested; this function is really a
        # end-to-end test. Only include in coverage once output file format is finalised.
        try:
            if base_file_name is not None:
                log_file = base_file_name + '_log.txt'
                Logger.log_file_handle = open(log_file, 'w')
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

        :param sector_fullcode: str
        :param varname: str
        :param value: str
        :return:
        """
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

    def RegisterAlias(self, alias, sector, varname):
        self.Aliases[alias] = (sector, varname)

    def GetSectors(self):
        out = []
        for cntry in self.CountryList:
            for sector in cntry.SectorList:
                out.append(sector)
        return out

    def GetTimeSeries(self, series, cutoff=None):
        if cutoff is None:
            cutoff = self.TimeSeriesCutoff
        try:
            if cutoff is None:
                return self.EquationSolver.TimeSeries[series]
            else:
                return self.EquationSolver.TimeSeries[series][0:(cutoff + 1)]
        except KeyError:
            raise KeyError('Time series "{0}" does not exist'.format(series))

    def FixAliases(self):
        lookup = {}
        for alias in self.Aliases:
            sector, varname = self.Aliases[alias]
            lookup[alias] = sector.GetVariableName(varname)
        for sector in  self.GetSectors():
            sector.ReplaceAliases(lookup)

    def LogInfo(self, generate_full_codes=True, ex=None):  # pragma: no cover
        """
        Write information to a file; if there is an exception, dump the trace.
        The log will normally generate the full sector codes; set generate_full_codes=False
        to leave the Model full codes untouched.

        :param file_name: str
        :param generate_full_codes: bool
        :param ex: Exception
        :return:
        """
        # Not covered with unit tests [for now]. Output format will change a lot.
        if generate_full_codes:
            self.GenerateFullSectorCodes()
            for c in self.CountryList:
                Logger('Country: Code= "%s" %s\n' % (c.Code, c.LongName))
                Logger('='*60 + '\n\n')
                for s in c.SectorList:
                    Logger(s.Dump() + '\n')
            Logger('\n\nFinal Equations:\n')
        Logger(self.FinalEquations + '\n')
        parser = EquationParser()
        parser.ParseString(self.FinalEquations)
        parser.EquationReduction()
        Logger(parser.DumpEquations())
        if ex is not None:
            Logger('\n\nError raised:\n')
            traceback.print_exc(file=Logger.log_file_handle)

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
            sector = self.LookupSector(sector_code)
            if varname not in sector.Equations:
                raise KeyError('Sector %s does not have variable %s' % (sector_code, varname))
            # Need to mark exogenous variables
            sector.Equations[varname] = 'EXOGENOUS ' + eqn

    def GenerateInitialConditions(self):
        out = []
        for sector_code, varname, value in self.InitialConditions:
            sector = self.LookupSector(sector_code)
            if varname not in sector.Equations:
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


class Sector(Entity):
    """
    All sectors derive from this class.
    """

    def __init__(self, country, long_name, code, has_F = True):
        Entity.__init__(self, country)
        country.AddSector(self)
        self.Code = code
        # This is calculated by the Model
        self.FullCode = ''
        self.LongName = long_name
        self.VariableDescription = {}
        self.Equations = {}
        self.HasF = has_F
        if has_F:
            self.AddVariable('F', 'Financial assets', '<TO BE GENERATED>')
            self.AddVariable('LAG_F', 'Previous period''s financial assets.', 'F(k-1)')
        self.CashFlows = []

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
        if varname not in self.Equations:
            raise KeyError('Variable %s not in sector %s' % (varname, self.FullCode))
        if self.FullCode == '':
            alias = '_{0}_{1}'.format(self.ID, varname)
            self.GetModel().RegisterAlias(alias, self, varname)
            return alias
        else:
            return self.FullCode + '_' + varname

    def ReplaceAliases(self, lookup):
        for var in self.Equations:
            self.Equations[var] = replace_token_from_lookup(self.Equations[var], lookup)
        self.CashFlows = [replace_token_from_lookup(flow, lookup) for flow in self.CashFlows]

    def AddCashFlow(self, term, eqn=None, desc=None):
        term = term.strip()
        if len(term) == 0:
            return
        term = term.replace(' ', '')
        if not (term[0] in ('+', '-')):
            term = '+' + term
        if len(term) < 2:
            raise ValueError('Invalid cash flow term')
        self.CashFlows.append(term)
        if eqn is None:
            return
        # Remove the +/- from the term
        term = term[1:]
        if term in self.Equations:
            if len(self.Equations[term]) == 0:
                self.Equations[term] = eqn
        else:
            self.AddVariable(term, desc, eqn)

    def GenerateEquations(self):
        return

    def Dump(self):
        out = '[%s] %s. FullCode = "%s" \n' % (self.Code, self.LongName, self.FullCode)
        out += '-' * 60 + '\n'
        for var in self.Equations:
            out += '%s = %s\n' % (var, self.Equations[var])
        return out

    def GenerateIncomeEquations(self):
        if not self.HasF:
            return
        if len(self.CashFlows) == 0:
            self.Equations['F'] = ''
            self.Equations['LAG_F'] = ''
            return
        self.CashFlows = ['LAG_F', ] + self.CashFlows
        eqn = create_equation_from_terms(self.CashFlows)
        self.Equations['F'] = eqn

    def CreateFinalEquations(self):
        out = []
        lookup = {}
        for varname in self.Equations:
            lookup[varname] = self.GetVariableName(varname)
        # Use GetVariables() so that we re always sorted; needed for unit tests
        for varname in self.GetVariables():
            if len(self.Equations[varname].strip()) == 0:
                continue
            out.append((self.GetVariableName(varname),
                        replace_token_from_lookup(self.Equations[varname], lookup),
                        '[%s] %s' % (varname, self.VariableDescription[varname])))
        return out

    def GenerateAssetWeighting(self, asset_weighting_list, residual_asset_code):
        """
        Generates the asset weighting/allocation equations. If there are N assets, pass N-1 in the list, the residual
        gets the rest.

        The variable asset_weighting_list is a list of pairs, of the form:
        [('asset1code', 'weigthing equation'), ('asset2code','weighting2'), ...]

        Note that weightings are (normally) from 0-1.
        :param asset_weighting_list: list
        :param residual_asset: str
        :return:
        """
        residual_weight = '1.0'
        for code, weight_eqn in asset_weighting_list:
            # Weight variable = 'WGT_{CODE}'
            weight = 'WGT_' + code
            self.AddVariable(weight, 'Asset weight for' + code, weight_eqn)
            self.AddVariable('DEM_'+ code, 'Demand for asset ' + code, 'F * {0}'.format(weight))
            residual_weight += ' - ' + weight
        self.AddVariable('WGT_' + residual_asset_code, 'Asset weight for ' + residual_asset_code, residual_weight)
        self.AddVariable('DEM_'+ residual_asset_code, 'Demand for asset ' + residual_asset_code,
                        'F * {0}'.format('WGT_' + residual_asset_code))



class Market(Sector):
    """
    Market Not really a sector, but keep it in the same list
    """

    def __init__(self, country, long_name, code):
        Sector.__init__(self, country, long_name, code, has_F = False)
        self.NumSupply = 0
        self.AddVariable('SUP_' + code, 'Supply for market ' + code, '')
        self.AddVariable('DEM_' + code, 'Demand for market ' + code, '')

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
                # Since we assume that there is a single supplier, we can set the supply equation to
                # point to the equation in the market.
                s.AddCashFlow(var_name, self.GetVariableName(var_name), long_desc)
                self.NumSupply += 1
            else:
                # Must fill in demand equation in sectors.
                s.AddCashFlow('-' + var_name, 'Error: must fill in demand equation', long_desc)
        eqn = create_equation_from_terms(term_list)
        self.Equations[var_name] = eqn

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


class FinancialAssetMarket(Market):
    """
    Handles the interactions for a market in a financial asset.
    Must be a single issuer.
    """
    def __init__(self, country, long_name, code, issuer_short_code):
        Market.__init__(self, country, long_name, code)
        self.IssuerShortCode = issuer_short_code



