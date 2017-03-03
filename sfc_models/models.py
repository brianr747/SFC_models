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
        Logger('{0} Created, ID={1}', priority=2, data_to_format=(type(self), self.ID))

    def GetModel(self):
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

    def GetSectorCodeWithCountry(self, sector):
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
        Logger('[ID={0}] Variable Added: {1} = {2} # {3}', priority=5,
               data_to_format=(self.ID, varname, desc, eqn))

    def SetExogenous(self, varname, val):
        """
        Set an exogenous variable for a sector. The variable must already be defined (by AddVariable()).
        :param varname: str
        :param val: str
        :return:
        """
        self.GetModel().AddExogenous(self, varname, val)

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
            eqn = self.Equations[var]
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

    def GenerateAssetWeighting(self, asset_weighting_dict, residual_asset_code, is_absolute_weighting=False):
        """
        Generates the asset weighting/allocation equations. If there are N assets, pass N-1 in the list, the residual
        gets the rest.

        The variable asset_weighting_list is a
        dictionary, of the form:
        {'asset1code': 'weighting equation',
        'asset2code': 'weighting2')}

        The is_absolute_weighting parameter is a placeholder; if set to true, asset demands are
        absolute. There is a TODO marking where code should be added.

        Note that weightings are (normally) from 0-1.
        :param asset_weighting_dict: dict
        :param residual_asset: str
        :param is_absolute_weighting: bool
        :return:
        """
        if is_absolute_weighting:
            # TODO: Implement absolute weightings.
            raise NotImplementedError('Absolute weightings not implemented')
        residual_weight = '1.0'
        if type(asset_weighting_dict) in (list, tuple):
            # Allow asset_weighting_dict to be a list of key: value pairs.
            tmp = dict()
            for code, eqn in asset_weighting_dict:
                tmp[code] = eqn
            asset_weighting_dict = tmp
        for code, weight_eqn in asset_weighting_dict.items():
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
        self.SupplyAllocation = []

    def SearchSupplier(self):
        """
        Find the sector that is a single supplier in a country.
        Throws a LogicError if more than one, or none.

        Need to set SupplyAllocation if you want to do something not
        covered by this default behaviour.

        :return: Sector
        """
        ret_value = None
        country = self.Parent
        for sector in country.SectorList:
            if sector.ID == self.ID:
                continue
            if 'SUP_' + self.Code in sector.Equations:
                if ret_value is None:
                    ret_value = sector
                else:
                    raise LogicError('More than one supplier, must set SupplyAllocation: ' + self.Code)
        if ret_value is None:
            raise LogicError('No supplier: ' + self.Code)
        return ret_value

    def GenerateEquations(self):
        if len(self.SupplyAllocation) == 0:
            supplier = self.SearchSupplier()
            self.SupplyAllocation = [[], supplier]
        if len(self.SupplyAllocation) > 0:
            self.NumSupply = len(self.SupplyAllocation[0])
            self.GenerateTermsLowLevel('DEM', 'Demand')
            self.GenerateMultiSupply()
        else: # pragma: no cover
            # Keep this legacy code here for now, in case I need to revert.
            raise LogicError('Should never reach this code!')
            self.NumSupply = 0
            self.GenerateTermsLowLevel('SUP', 'Supply')
            if self.NumSupply == 0:
                raise ValueError('No supply for market: ' + self.FullCode)
            self.GenerateTermsLowLevel('DEM', 'Demand')
            if self.NumSupply > 1:
                raise LogicError('More than one supply at market, must set SupplyAllocation: ' + self.Code)
            else:
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
        # Set aggregate supply equal to demand
        self.Equations[sup_name] = dem_name
        for s in country.SectorList:
            if s.ID == self.ID:
                continue
            if sup_name in s.Equations:
                s.Equations[sup_name] = self.Equations[dem_name]
                return

    def GenerateMultiSupply(self):
        country = self.Parent
        sup_name = 'SUP_' + self.Code
        dem_name = 'DEM_' + self.Code
        # Set aggregate supply equal to demand
        self.Equations[sup_name] = dem_name
        # Generate individual supply equations
        # terms: need to create a list of non-residual supply terms so that
        # we can set the residual supply
        terms = [sup_name,]
        # Unpack the SupplyAllocation member. [Create a class?]
        sector_list, residual_sector = self.SupplyAllocation
        for sector, eqn in sector_list:
            local_name = 'SUP_' + sector.FullCode
            terms.append(local_name)
            self.AddVariable(local_name, 'Supply from {0}'.format(sector.LongName), eqn)
            # Push this local variable into the supplying sector
            # If we are in the same country, use 'SUP_{CODE}'
            # If we are in different countries, use 'SUP_{FULLCODE}'
            if self.ShareParent(sector):
                supply_name = 'SUP_' + self.Code
            else:
                supply_name = 'SUP_' + self.FullCode
            sector.Equations[supply_name] = self.GetVariableName(local_name)
            sector.AddCashFlow('+' + supply_name)
        # Residual sector supplies rest
        sector = residual_sector
        local_name = 'SUP_' + residual_sector.FullCode
        # Equation = [Total supply] - \Sum Individual suppliers
        eqn = '-'.join(terms)
        self.AddVariable(local_name,  'Supply from {0}'.format(residual_sector.LongName), eqn)
        if self.ShareParent(residual_sector):
            supply_name = 'SUP_' + self.Code
        else:
            supply_name = 'SUP_' + self.FullCode
        residual_sector.Equations[supply_name] = self.GetVariableName(local_name)
        residual_sector.AddCashFlow('+' + supply_name)



class FinancialAssetMarket(Market):
    """
    Handles the interactions for a market in a financial asset.
    Must be a single issuer.
    """
    def __init__(self, country, long_name, code, issuer_short_code):
        Market.__init__(self, country, long_name, code)
        self.IssuerShortCode = issuer_short_code



