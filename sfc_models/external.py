from sfc_models.models import Country
from sfc_models.sector import Sector


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
        for czone in model.CurrencyZoneList:
            self.RegisterCurrency(czone.Currency)

    def RegisterCurrency(self, currency):
        desc = 'Exchange Rate: x NUMERAIRE to buy 1 unit of {0}'.format(currency)
        # By default, fixed at 1.
        self['XR'].AddVariable(currency, desc, '1.0')
        desc = 'Net transactions in currency {0}'.format(currency)
        self['FX'].AddVariable('NET_' + currency, desc, '')

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

    def _SendMoney(self, source_sector, variable_name, is_income):
        """
        Half of an international transaction.

        The convention is that the amount is always based on the local currency
        of the sending Country.

        It is assumed that variable_name exists.

        This should not be called directly by users; however, we need to be able to
        handle interactions with Market objects.

        :param source_sector: Sector
        :param variable_name: str
        :param is_income: bool
        :return:
        """
        if '__' not in variable_name:
            variable_name = source_sector.GetVariableName(variable_name)
        term = '-' + variable_name
        source_sector.AddCashFlow('-' + variable_name, is_income=is_income)
        currency = source_sector.CurrencyZone.Currency
        currency_variable_name = self.Parent['XR'].GetVariableName(currency)
        self.EquationBlock['NET_' + currency].AddTerm(term)
        self.EquationBlock['NET_NUMERAIRE'].AddTerm(term + '/' + currency_variable_name)



