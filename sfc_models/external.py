from sfc_models.models import Country
from sfc_models.sector import Sector
import sfc_models.utils as utils


class ExternalSector(Country):
    """
    All international concepts live within an "ExternalSector"

    It is a Country, with code = EXT (default)

    The "currency" of ExternalSector is 'NUMERAIRE' (by default).

    All currency values are expressed relative to this numéraire (that is,
    the value of NUMERAIRE=1 by definition). In practice,
    at least one real currency will always have a value of 1.0 as well.

    It would probably be a bad idea to define another Country`s currency as NUMERAIRE;
    the assumption within the code is that the ExternalSector lives within its own
    CurrencyZone.

    Since it is assumed that the supply of each real currency is netted out to
    zero, we should never get 'NUMERAIRE' financial assets created. If this happens,
    the equation set up is incorrect. The framework allows such an incoherent state;
    it is up to the user to tune their equations to keep the net NUMERAIRE financial
    assets at zero. (A sanity check may later be imposed.)

    A Model can only have one ExternalSector; the object registers itself as the
    Model.ExternalSector when created.
    """
    def __init__(self, model, code='EXT', currency='NUMERAIRE'):
        Country.__init__(self, model, long_name='External Sector', code=code,
                         currency=currency)
        model.ExternalSector = self
        ExchangeRates(self)
        ForexTransations(self)
        InternationalGold(self)
        for czone in model.CurrencyZoneList:
            self.RegisterCurrency(czone.Currency)

    def RegisterCurrency(self, currency):
        desc = 'Exchange Rate: x NUMERAIRE to buy 1 unit of {0}'.format(currency)
        # By default, fixed at 1.
        self['XR'].AddVariable(currency, desc, '1.0')
        desc = 'Net transactions in currency {0}'.format(currency)
        fx = self['FX']
        fx.AddVariable('NET_' + currency, desc, '')
        fx.AddVariable('F_' + currency, 'Net Financial assets in ' + currency,
                       'LAG_F_xx + NET_xx'.replace('xx', currency))
        fx.AddVariable('LAG_F_' + currency, 'Previous period financial assets',
                       'F_{0}(k-1)'.format(currency))

    def GetCrossRate(self, local, foreign):
        """
        Convenience function; just calls the XR Sector.
        (May also pass CurrencyZone objects.)

        Convention:
        Number of foreign units to buy 1 local. So an increase in the cross rate variable
        implies a stronger local currency versus the foreign.

        :param local: str
        :param foreign: str
        :return: str
        """
        return self['XR'].GetCrossRate(local, foreign)

    def _ReceiveMoney(self, target_sector, source_sector, variable_name):
        """
        Convenience function; calls ForexTransactions._ReceiveMoney
        :param target_sector: Sector
        :param source_sector: Sector
        :param variable_name: str
        :return: str
        """
        return self['FX']._ReceiveMoney(target_sector, source_sector, variable_name)

    def _SendMoney(self, source_sector, variable_name):
        """
        Convenience function, calls ForexTransactions._SendMoney
        :param source_sector: Sector
        :param variable_name: str
        :return:
        """
        self['FX']._SendMoney(source_sector, variable_name)

class ExchangeRates(Sector):
    """
    Object that handles all exchange rate information. Automatically created by
    ExternalSector; users should never need to create one independently.
    """
    def __init__(self, external_sector):
        Sector.__init__(self, country=external_sector, long_name='Exchange Rate Info',
                        code='XR', has_F=False)

    def GetCrossRate(self, local, foreign):
        """
        Get the variable name for a cross rate.
        (May also pass CurrencyZone objects.)

        Convention:
        Number of foreign units to buy 1 local. So an increase in the cross rate variable
        implies a stronger local currency versus the foreign.

        In standard Forex terms, this would be quoted as LOCAL/FOREIGN (local currency is base
        currency), or an "indirect quote".

        Reference: http://www.investopedia.com/university/forexmarket/forex2.asp

        The variable is created the first time the GetCrossRate method is called. That is,
        if it is never referenced, it will never appear in the equation block. (This would
        probably only show up if we have > 2 countries, and trade is all with a central hub
        country.)

        :param local: str
        :param foreign: str
        :return:
        """
        if type(local) is not str:
            local = local.Currency
        if type(foreign) is not str:
            foreign = foreign.Currency
        code = '{0}_{1}'.format(local, foreign)
        if code not in self.EquationBlock:
            desc = 'Cross rate: {0} to buy 1 {1} (Standard quote convention: "{2}/{3}.")'.format(
                foreign, local, local, foreign)
            self.AddVariable(code, desc,  '{0}/{1}'.format(local, foreign))
        return self.GetVariableName(code)

class ForexTransations(Sector):
    """
    Class that holds the equations detailing foreign exchange transactions.

    Object is automatically created by the ExternalSector; default code is "FX"

    Since the convention is that all balance sheet items in a Sector object are in the
    local currency, we need to be able to find a way to intermediate transactions
    between sectors in different CurrencyZone objects.

    We could create multinational bank objects that are two linked Sector objects.
    The ForexTransaction object is a simpler alternative: both sides of a transaction face
    off against a "Foreign Exchange Market" that is "out there somewhere".

    The convention is that each sector exchanges for units of "NUMERAIRE"; we just have to
    ensure that the net transactions for each currency versus "NUMERAIRE" are nil.
    """
    def __init__(self, external_sector, code='FX'):
        Sector.__init__(self, country=external_sector,
                        long_name='Foreign Exchange Transactions', code=code, has_F=False)

    def _SendMoney(self, source_sector, variable_name):
        """
        Half of an international transaction.

        This is used internally by the framework; users should normally call
        Model.RegisterCashFlow() or let the Market object handle international
        cash flows. This will only need to be called if extended or modifying the
        framework.

        The convention is that the amount is always based on the local currency
        of the sending Country.

        It is assumed that variable_name exists.

        This should not be called directly by users; however, we need to be able to
        handle interactions with Market objects.

        Does not call AddCashFlow() on the sending Sector. The cash flow implications
        have to be handled elsewhere. The reason being is that Market objects are
        the major SendCash() user, and they do not have cash flows themselves. The demand
        sectors are the source of the cash that is being sent overseas, so the
        domestic cash flows will balance.

        :param source_sector: Sector
        :param variable_name: str
        :return:
        """
        if utils.is_local_variable(variable_name):
            variable_name = source_sector.GetVariableName(variable_name)
        currency = source_sector.CurrencyZone.Currency
        currency_variable_name = self.Parent['XR'].GetVariableName(currency)
        self.EquationBlock['NET_' + currency].AddTerm('+' + variable_name)
        self.EquationBlock['NET_NUMERAIRE'].AddTerm(
            '-' + variable_name + '*' + currency_variable_name)

    def _ReceiveMoney(self, target_sector, source_sector, variable_name):
        """
               Half of an international transaction.

        This is used internally by the framework; users should normally call
        Model.RegisterCashFlow() or let the Market object handle international
        cash flows. This will only need to be called if extended or modifying the
        framework.

        The convention is that the amount is always based on the local currency
        of the sending Country.

        It is assumed that variable_name exists.

        This should not be called directly by users; however, we need to be able to
        handle interactions with Market objects.

        Does not call AddCashFlow() on the receiving Sector. The cash flow implications
        have to be handled elsewhere. Although this would likely be safe, the code is
        symmetric with respect to _SendMoney

        Returns the full cash flow term for the target sector (in target currency).

        :param target_sector: Sector
        :param source_sector: Sector
        :param variable_name: str
        :return: str
        """
        if utils.is_local_variable(variable_name):
            variable_name = source_sector.GetVariableName(variable_name)
        source_currency = source_sector.CurrencyZone.Currency
        target_currency = target_sector.CurrencyZone.Currency
        cross_rate = self.Parent.GetCrossRate(source_currency, target_currency)
        target_sector_term = '{0}*{1}'.format(variable_name, cross_rate)
        self.EquationBlock['NET_' + target_currency].AddTerm('-' + target_sector_term)
        # The target currency cancels out...
        term = '+{0}*{1}'.format(variable_name,
                                 self.Parent['XR'].GetVariableName(source_currency))
        self.EquationBlock['NET_NUMERAIRE'].AddTerm(term)
        return target_sector_term


class InternationalGold(Sector):
    def __init__(self, external_sector, code='GOLD'):
        """
        Object to handle international Gold transactions.

        It pushes variables onto transacting sectors; the only variables embedded in
        this object is PRICE (the price of 1 oz of gold in NUMERAIRE), and NET_OZ,
        which are the net transactions in OZ (should be zero normally).

        These variables are only created if SetGoldPurchases is called; so as to not
        clog the equation space of models that do not contain gold transactions.

        If users want to use this object without calling SetGoldSales, they can call
        SetUpVariables()
        :param external_sector:
        :param code:
        """
        Sector.__init__(self, country=external_sector, long_name='International Gold Market',
                        code=code, has_F=False)
        self.Owner = 'Gnomes of Zurich'

    def GetVariableName(self, varname):
        if varname in ('PRICE', 'NETOZ'):
            if varname not in self.EquationBlock.GetEquationList():
                self.SetUpVariables()
        return Sector.GetVariableName(self, varname)

    def SetUpVariables(self):
        if 'PRICE' not in self.EquationBlock:
            self.AddVariable('PRICE', 'Price of 1 oz gold in NUMERAIRE', '1.0')
        if 'NETOZ' not in self.EquationBlock:
            self.AddVariable('NETOZ', 'Net EXT transaction in gold (oz)', '')

    def SetGoldPurchases(self, sector, flow_variable_name, initial_stock):
        """
        Does all the set up for Gold purchases, including setting the initial stock.

        Creates the gold PRICE variable if does not already exist.
        :param sector: Sector
        :param flow_variable_name: str
        :param initial_stock: float
        :return:
        """
        loc_currency = sector.CurrencyZone.Currency
        desc = 'Value of Gold Holdings ({0})'.format(loc_currency)
        var_gold_price = self.GetVariableName('PRICE')
        var_currency = self.Parent['XR'].GetVariableName(loc_currency)
        sector.AddVariable('GOLDPRICE', 'Gold Price in {0}'.format(loc_currency),
                           '{0} / {1}'.format(var_gold_price, var_currency))
        eqn = '(LAG_GOLD_OZ * GOLDPRICE) + {0}'.format(flow_variable_name)
        sector.AddVariable('GOLD', desc, eqn)
        sector.AddVariable('LAG_GOLD_OZ', 'Previous period''s gold holdings (oz)', 'GOLD_OZ(k-1)')
        sector.AddVariable('GOLD_OZ', 'Number of oz Held', 'GOLD / GOLDPRICE')
        sector.AddInitialCondition('GOLD_OZ', initial_stock)
        self.Parent['FX']._SendMoney(sector, flow_variable_name)
        sector.AddCashFlow('-' + flow_variable_name, is_income=False)
        full_flow_variable_name = sector.GetVariableName(flow_variable_name)
        self.AddTermToEquation('NETOZ', '{0}*{1}'.format(var_currency, full_flow_variable_name))









