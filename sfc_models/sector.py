from sfc_models.equation import EquationBlock, Equation, Term
from sfc_models.models import EconomicObject, Model, Country
from sfc_models.utils import Logger, replace_token_from_lookup, LogicError, create_equation_from_terms


class Sector(EconomicObject):
    """
    All sectors derive from this class.
    """

    def __init__(self, country, code, long_name='', has_F=True):
        if long_name == '':
            long_name = 'Sector Object {0} in Country {1}'.format(code, country.Code)
        self.Code = code
        EconomicObject.__init__(self, country, code=code)
        self.CurrencyZone = country.CurrencyZone
        country._AddSector(self)
        # This is calculated by the Model
        self.FullCode = ''
        self.LongName = long_name
        # self.Equations = {}
        self.HasF = has_F
        self.IsTaxable = False
        self.EquationBlock = EquationBlock()
        if has_F:
            # self.AddVariable('F', 'Financial assets', '<TO BE GENERATED>')
            F = Equation('F', 'Financial assets')
            F.AddTerm('LAG_F')
            self.AddVariableFromEquation(F)
            # self.AddVariable('LAG_F', 'Previous period''s financial assets.', 'F(k-1)')
            INC = Equation('INC', 'Income (PreTax)', rhs=[])
            self.AddVariableFromEquation(INC)
            self.AddVariable('LAG_F', 'Previous period''s financial assets.', 'F(k-1)')

    def AddVariable(self, varname, desc='', eqn=''):
        """
        Add a variable to the sector.
        The variable name (varname) is the local name; it will be decorated to create a
        full name. Equations within a sector can use the local name; other sectors need to
        use GetVariableName to get the full name.
        :param varname: str
        :param desc: str
        :param eqn: str
        :return: None
        """
        if '__' in varname:
            raise ValueError('Cannot use "__" inside local variable names: ' + varname)
        if desc is None:
            desc = ''
        if type(eqn) == Equation:
            equation = eqn
        else:
            equation = Equation(varname, desc, [Term(eqn, is_blob=True),])
        if varname in self.GetVariables():
            Logger('[ID={0}] Variable Overwritten: {1}', priority=3,
                   data_to_format=(self.ID, varname))
        self.EquationBlock.AddEquation(equation)
        # self.Equations[varname] = eqn
        Logger('[ID={0}] Variable Added: {1} = {2} # {3}', priority=2,
               data_to_format=(self.ID, varname, eqn, desc))

    def AddVariableFromEquation(self, eqn):
        """
        Method to be used until the Equation member is replaced...
        :param eqn: Equation
        :return:
        """
        if type(eqn) == str:
            eqn = Equation(eqn)
        self.AddVariable(eqn.LeftHandSide, eqn.Description, eqn)

    def SetEquationRightHandSide(self, varname, rhs):
        """
        Set the right hand side of the equation for an existing variable.
        :param varname: str
        :param rhs: str
        :return: None
        """
        try:
            self.EquationBlock[varname].TermList = [Term(rhs, is_blob=True),]
        except KeyError:
            raise KeyError('Variable {0} does not exist'.format(varname))
        # Could try: Equation.ParseString(rhs), but is too slow in unit tests...
        # if varname not in self.Equations:
        #     raise KeyError('Variable {0} does not exist'.format(varname))
        Logger('[ID={0}] Equation set: {1} = {2} ', priority=2,
               data_to_format=(self.ID, varname, rhs))
        # self.Equations[varname] = rhs

    def AddTermToEquation(self, varname, term):
        """
        Add a new term to an existing equation.

        The term variable may be either a string or (non-Blob) Term object.

        :param varname: str
        :param term: Term
        :return: None
        """
        term = Term(term)
        Logger('Adding term {0} to Equation {1} in Sector {2} [ID={3}]', priority=2,
               data_to_format=(term, varname, self.Code, self.ID))
        try:
            self.EquationBlock[varname].AddTerm(term)
        except KeyError:
            raise KeyError('Variable {0} not in Sector {1}'.format(varname, self.Code))


    def SetExogenous(self, varname, val):
        """
        Set an exogenous variable for a sector. The variable must already be defined (by AddVariable()).
        :param varname: str
        :param val: str
        :return: None
        """
        self.GetModel().AddExogenous(self, varname, val)

    def GetVariables(self):
        """
        Return a sorted list of variables.

        (Need to sort to make testing easier; dict's store in "random" hash order.

        This is a convenience function; it just passes along self.EquationBlock.GetEquationList()
        :return: list
        """
        return self.EquationBlock.GetEquationList()

    def GetVariableName(self, varname):
        """
        Get the full variable name associated with a local variable.

        Standard convention:
        {sector_fullcode}__{local variable name}.
        NOTE: that is is double-underscore '_'. The use of double underscores in
        variable names (or sector codes) is now verboten!
        This means that the presence of double underscore means that this is a full variable name.

        NOTE: If the sector FullCode is not defined, a temporary alias is created and registered.
        The Model object will ensure that all registered aliases are cleaned up.]

        :param varname: str
        :return: str
        """
        if varname not in self.EquationBlock.GetEquationList():
            raise KeyError('Variable %s not in sector %s' % (varname, self.FullCode))
        if self.FullCode == '':
            alias = '_{0}__{1}'.format(self.ID, varname)
            Logger('Registering alias: {0}', priority=5, data_to_format=(alias,))
            self.GetModel()._RegisterAlias(alias, self, varname)
            return alias
        else:
            # Put in a sanity check here
            if '__' in self.FullCode:
                raise ValueError('The use of "__" in sector codes is invalid: ' + self.FullCode)
            if '__' in varname:
                raise ValueError('The use of "__" in variable local names is invalid: ' + varname)
            return self.FullCode + '__' + varname

    def IsSharedCurrencyZone(self, other):
        """
        Is a sector in the same CurrencyZone as the other?
        :param other: Sector
        :return: bool
        """
        return self.CurrencyZone.ID == other.CurrencyZone.ID

    def _ReplaceAliases(self, lookup):
        """
        Use the lookup dictionary to replace aliases.
        :param lookup: dict
        :return:
        """
        self.EquationBlock.ReplaceTokensFromLookup(lookup)

    def AddCashFlow(self, term, eqn=None, desc=None, is_income=True):
        """
        Add a cash flow to the sector. Will add to the financial asset equation (F), and
        the income equation (INC) if is_income is True.

        Except: There is a list of exclusions to which cash flows are not considered income.
        That setting will override the is_income parameter. This allows us to carve out exceptions
        to the standard behaviour, which generally is to assume that cash flows are associated with
        income.

        :param term: str
        :param eqn: str
        :param desc: str
        :param is_income: bool
        :return: None
        """
        term = term.strip()
        if len(term) == 0:
            return
        term_obj = Term(term)
        if not term_obj.IsSimple: # pragma: no cover  - Not implemented; cannot hit the line below.
            raise LogicError('Must supply a single variable as the term to AddCashFlow')
        # term = term.replace(' ', '')
        # if not (term[0] in ('+', '-')):
        #     term = '+' + term
        # if len(term) < 2:
        #     raise ValueError('Invalid cash flow term')
        self.EquationBlock['F'].AddTerm(term)
        if is_income:
            # Need to see whether it is excluded
            mod = self.GetModel()
            for obj, excluded in mod.IncomeExclusions:
                if obj.ID == self.ID:
                    if term_obj.Term == excluded:
                        is_income = False
                        break
        if is_income:
            self.EquationBlock['INC'].AddTerm(term)
        if eqn is None:
            return
        # Remove the +/- from the term
        term = term_obj.Term
        if term in self.GetVariables():
            rhs = self.EquationBlock[term].RHS()
            if rhs == '' or rhs == '0.0':
                self.SetEquationRightHandSide(term, eqn)
        else:
            self.AddVariable(term, desc, eqn)

    def AddInitialCondition(self, variable_name, value):
        """
        Add an initial condition for a variable associated with this sector.
        :param variable_name: str
        :param value: float
        :return:
        """
        self.GetModel().AddInitialCondition(self.ID, variable_name, value)

    def _GenerateEquationsFrontEnd(self): # pragma: no cover
        """
        Used by graphical front ends; generates a logging message. (In Model.Main(),
        the logging is done by the Model before it calls the Sector.)
        :return:
        """
        Logger('Running _GenerateEquations on {0} [{1}]', priority=3,
               data_to_format=(self.Code, self.ID))
        self._GenerateEquations()

    def _GenerateEquations(self):
        """
        Work is done in derived classes.
        :return: None
        """
        return

    def Dump(self):
        """
        Create a string with information about this object. This is for debugging
        purposes, and the format will change over time. In other words, do not rely on
        this output if you want specific information.

        :return: str
        """
        out = '[%s] %s. FullCode = "%s" \n' % (self.Code, self.LongName, self.FullCode)
        out += '-' * 60 + '\n'
        for var in self.EquationBlock.GetEquationList():
            out += str(self.EquationBlock[var]) + '\n'
        return out

    def _CreateFinalEquations(self):
        """
        Returns the final set of equations, with the full names of variables.
        :return: list
        """
        out = []
        lookup = {}
        for varname in self.EquationBlock.GetEquationList():
            lookup[varname] = self.GetVariableName(varname)
        for varname in self.EquationBlock.GetEquationList():
            eq = self.EquationBlock[varname]
            rhs = eq.GetRightHandSide()
            if len(rhs.strip()) == 0:   # pragma: no cover  [Does not happen any more; leave in just in case.]
                continue
            out.append((self.GetVariableName(varname),
                        replace_token_from_lookup(rhs, lookup),
                        '[%s] %s' % (varname, eq.Description)))
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
        :param residual_asset_code: str
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
            self.AddVariable('DEM_' + code, 'Demand for asset ' + code, 'F * {0}'.format(weight))
            residual_weight += ' - ' + weight
        self.AddVariable('WGT_' + residual_asset_code, 'Asset weight for ' + residual_asset_code, residual_weight)
        self.AddVariable('DEM_' + residual_asset_code, 'Demand for asset ' + residual_asset_code,
                         'F * {0}'.format('WGT_' + residual_asset_code))

class Market(Sector):
    """
    Market Not really a sector, but keep it in the same list.
    """

    def __init__(self, country, code, long_name=''):
        if long_name == '':
            long_name = 'Market {0} in Country {1}'.format(code, country.Code)
        Sector.__init__(self, country, code, long_name, has_F=False)
        self.AddVariable('SUP_' + code, 'Supply for market ' + code, '')
        self.AddVariable('DEM_' + code, 'Demand for market ' + code, '')
        self.ResidualSupply = None
        self.OtherSuppliers = []

    def _SearchSupplier(self):
        """
        Find the sector that is a single supplier in a country.
        Throws a LogicError if more than one, or none.

        Need to set SupplyAllocation if you want to do something not
        covered by this default behaviour.

        :return: Sector
        """
        Logger('Market {0} searching Country {1} for a supplier', priority=3,
               data_to_format=(self.Code, self.Parent.Code))
        ret_value = None
        for sector in self.Parent.GetSectors():
            if sector.ID == self.ID:
                continue
            if 'SUP_' + self.Code in sector.EquationBlock.Equations:
                if ret_value is None:
                    ret_value = sector
                else:
                    raise LogicError('More than one supplier, must set SupplyAllocation: ' + self.Code)
        if ret_value is None:
            raise LogicError('No supplier: ' + self.Code)
        self.ResidualSupply = ret_value
        return ret_value

    def _GenerateEquations(self):
        """
        Generate the equations associated with this market.
        :return:
        """
        if self.ResidualSupply is None:
            supplier = self._SearchSupplier()
        self._GenerateTermsLowLevel('DEM', 'Demand')
        self._GenerateMultiSupply()

    def _GenerateTermsLowLevel(self, prefix, long_desc):
        """
        Generate the terms associated with this market, for supply and demand.

        TODO: This is now only called for the demand function; simplify to just refer
        to demand.

        :param prefix: str
        :param long_desc: str
        :return: None
        """
        Logger('Searching for demand for market {0}', priority=3, data_to_format=(self.FullCode,))
        if prefix not in ('SUP', 'DEM'):
            raise LogicError('Input to function must be "SUP" or "DEM"')
        # country = self.Parent
        short_name = prefix + '_' + self.Code
        long_name = prefix + '_' + self.FullCode
        self.AddVariable(short_name, long_desc + ' for Market ' + self.Code, '')
        term_list = []
        for s in self.CurrencyZone.GetSectors():
            if s.ID == self.ID:
                continue
            if self.ShareParent(s):
                var_name = short_name
            else:
                var_name = long_name
            try:
                term = s.GetVariableName(var_name)
            except KeyError:
                Logger('Variable {0} does not exist in {1}', priority=10,
                       data_to_format=(var_name, s.FullCode))
                continue
            term_list.append('+ ' + term)
            if prefix == 'SUP': # pragma: no cover
                # Since we assume that there is a single supplier, we can set the supply equation to
                # point to the equation in the market.
                s.AddCashFlow(var_name, self.GetVariableName(var_name), long_desc)
            else:
                # Must fill in demand equation in sectors.
                s.AddCashFlow('-' + var_name, '', long_desc)
        eqn = create_equation_from_terms(term_list)
        self.SetEquationRightHandSide(short_name, eqn)

    def AddSupplier(self, supplier, supply_eqn=''):
        """
        Add a supply. If the supply_eqn is empty (or None), becomes the ResidualSupplier
        :param supplier: Sector
        :param supply_eqn: str
        :return:
        """
        if supply_eqn is None or supply_eqn=='':
            self.ResidualSupply = supplier
            return
        self.OtherSuppliers.append((supplier, supply_eqn))

    def _GenerateMultiSupply(self):
        """
        Generate the supply terms with multiple suppliers.

        :return:
        """
        sup_name = 'SUP_' + self.Code
        dem_name = 'DEM_' + self.Code
        # Set aggregate supply equal to demand
        self.SetEquationRightHandSide(sup_name, rhs=dem_name)
        # Generate individual supply equations
        # These are already supplied for everything other than the residual supply, so
        # we need to build it up.
        # Also, the name of the supply varies, depending on whether we are in te same
        # country/region.
        residual_sector = self.ResidualSupply

        residual_equation = Equation(self.GetSupplierTerm(residual_sector),
                                     'Residual supply', sup_name)
        sector_list = self.OtherSuppliers
        # residual supply = total supply less other supply terms
        for supplier, _ in sector_list:
            term = '-SUP_' + supplier.FullCode
            residual_equation.AddTerm(term)
        # Now that we have an equation for the residual sector, append it to the
        # list of suppliers, so we can process all suppliers in one block of code.
        sector_list.append((residual_sector, residual_equation.RHS()))

        for supplier, eqn in sector_list:
            local_name = 'SUP_' + supplier.FullCode
            self.AddVariable(local_name, 'Supply from {0}'.format(supplier.LongName), eqn)
            # Push this local variable into the supplying sector
            # If we are in the same country, use 'SUP_{CODE}'
            # If we are in different countries, use 'SUP_{FULLCODE}'
            supply_name = self.GetSupplierTerm(supplier)
            if supply_name not in supplier.EquationBlock:
                supplier.AddVariable(supply_name, 'Supply to {0}'.format(self.FullCode), '')
            if self.IsSharedCurrencyZone(supplier):
                supplier.AddTermToEquation(supply_name, self.GetVariableName(local_name))
                supplier.AddCashFlow('+' + supply_name)
            else:
                model = self.GetModel()
                if model.ExternalSector is None:
                    raise LogicError('Must create ExternalSector if we have cross-currency suppliers')
                full_local_name = self.GetVariableName(local_name)
                model.ExternalSector._SendMoney(self, full_local_name)
                term = model.ExternalSector._ReceiveMoney(supplier, self, full_local_name)
                supplier.AddTermToEquation(supply_name, term)
                supplier.AddCashFlow(term)
        return
        # # Residual sector supplies rest
        # # noinspection PyUnusedLocal
        # # This declaration of sector is not needed, but I left it in case code from
        # # above is pasted here, without replacing 'sector' with residual_sector.
        # if not self.IsSharedCurrencyZone(residual_sector):
        #     raise NotImplementedError('Currently does not support residual sectors in another currency')
        # sector = residual_sector
        # local_name = 'SUP_' + residual_sector.FullCode
        # # Equation = [Total supply] - \Sum Individual suppliers
        # eqn = '-'.join(terms)
        # self.AddVariable(local_name, 'Supply from {0}'.format(residual_sector.LongName), eqn)
        # if self.ShareParent(residual_sector):
        #     supply_name = 'SUP_' + self.Code
        # else:
        #     supply_name = 'SUP_' + self.FullCode
        # if supply_name not in residual_sector.EquationBlock:
        #     residual_sector.AddVariable(supply_name, 'Supply to {0}'.format(self.FullCode), '')
        # residual_sector.SetEquationRightHandSide(supply_name, self.GetVariableName(local_name))
        # residual_sector.AddCashFlow('+' + supply_name)

    def GetSupplierTerm(self, supplier):
        """
        What is the local variable name within a supplier for supply to this
        market?

        If same Country,
        out = "SUP_{code}"

        >>> mod = Model()
        >>> ca = Country(mod, 'CA')
        >>> mar = Market(ca, 'GOOD')
        >>> supplier = Sector(ca, 'BUS')
        >>> mar.GetSupplierTerm(supplier)
        'SUP_GOOD'

        Howevever, if we are in a different country, must use the full code.
        out = "SUP_{FullCode}"

        >>> mod = Model()
        >>> ca = Country(mod, 'CA')
        >>> us = Country(mod, 'US')
        >>> mar = Market(ca, 'GOOD')
        >>> supplier = Sector(us, 'BUS')
        >>> mar.GetSupplierTerm(supplier)
        'SUP_CA_GOOD'

        :param supplier: Sector
        :return: str
        """
        if self.ShareParent(supplier):
            return 'SUP_' + self.Code
        else:
            return 'SUP_' + self.GetModel().GetSectorCodeWithCountry(self)


class FinancialAssetMarket(Market):
    """
    Handles the interactions for a market in a financial asset.
    Must be a single issuer.
    """

    def __init__(self, country, code, long_name='', issuer_short_code='GOV'):
        Market.__init__(self, country, code, long_name)
        self.IssuerShortCode = issuer_short_code
        self.SearchListSource = self.CurrencyZone


