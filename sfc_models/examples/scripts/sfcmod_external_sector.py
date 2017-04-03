# coding=utf-8
from sfc_models.objects import *


def get_description():
    return 'External sector model'

def build_country(model, paramz):
    """
    Builds a country object.
    :param model: Model
    :param paramz: dict
    :return: None
    """
    country_name = paramz['Country Name']
    country = Country(model, code=paramz['Country'], long_name=country_name)
    gov = GoldStandardGovernment(country, 'GOV', initial_gold_stock=40.)
    #cb = CentralBank(country, 'CB', 'Central Bank', tre)
    mm = MoneyMarket(country, issuer_short_code='GOV')
    #dep = DepositMarket(country, issuer_short_code='TRE')
    tax = TaxFlow(country, 'TF', 'TaxFlow', taxrate=.2, taxes_paid_to='GOV')
    hh = Household(country, code='HH', long_name='Household ' + country_name)
    goods = Market(country, 'GOOD', 'Goods market ' + country_name)
    bus = FixedMarginBusinessMultiOutput(country, 'BUS', 'Business Sector', market_list=[goods, ], profit_margin=0.0)
    goods.AddSupplier(bus)
    goods.AddVariable('MU', 'Propensity to import', paramz['mu'])
    labour = Market(country, 'LAB', 'Labour market: ' + country_name)
    gov.AddInitialCondition('F', -100.)
    mm.AddInitialCondition('DEM_MON', 100.)
    hh.AddInitialCondition('F', 100.)
    gov.AddVariable('GOLDCOVER', 'Gold Coverage of Money Stock', 'GOLD/SUP_MON')
    gov.AddVariable('LAG_COVER', 'Previous period''s GOLDCOVER', 'GOLDCOVER(k-1)')

    gov.AddInitialCondition('DEM_GOOD', 25.)

    gov.AddVariable('LAG_G', 'Previous period''s Government Consumption', 'DEM_GOOD(k-1)')
    gov.AddInitialCondition('LAG_G', 25.)
    if True:
        gov.AddVariable('ADJUST', 'Adjustmemt to spending', 'min(.2*(LAG_COVER-.4), .05*(LAG_COVER-.4))')
        gov.SetEquationRightHandSide('DEM_GOOD', 'LAG_G * (1 + ADJUST)')
    else:
        gov.SetEquationRightHandSide('DEM_GOOD', 'LAG_G')
    # Create the goods demand function

    # I normally would not commit a file in a half-finished state, but I want to make sure
    # that I upload a lot of key changes to GitHub. The work in this class should have been
    # done in a different branch; oops.

    # Create the demand for deposits.  ('MON' is the residual asset.)
    # hh.AddVariable('L0', 'lambda_0: share of bills in wealth', paramz['L0'])
    # hh.AddVariable('L1', 'lambda_1: parameter related to interest rate', paramz['L1'])
    # hh.AddVariable('L2', 'lambda_2: parameter related to disposable income', paramz['L2'])
    # # Generate the equation. Need to get the name of the interest rate variable
    # r =dep.GetVariableName('r')
    # # The format() call will replace '{0}' with the contents of the 'r' variable.
    # eqn = 'L0 + L1 * {0} - L2 * (AfterTax/F)'.format(r)
    # hh.GenerateAssetWeighting([('DEP', eqn)], 'MON')


def other_country(country):
    if country == 'N':
        return 'S'
    return 'N'


def generate_supply_allocation(mod, country):
    Y = mod[country]['HH'].GetVariableName('INC')
    other = other_country(country)
    market = mod[country]['GOOD']
    market.AddSupplier(mod[other]['BUS'], 'MU*{0}'.format(Y))
    mod[other]['BUS'].AddMarket(market)


def build_model():
    """

    :return: Model
    """
    model = Model()
    ExternalSector(model)

    paramz = {
        'Country': 'N',
        'Country Name': 'North',
        'alpha_income': .6,
        'alpha_fin': .4,
        'mu': '0.18761',
        'L0': '0.635',
        'L1': '5.',
        'L2': '.01',
    }
    build_country(model, paramz)
    paramz = {
        'Country': 'S',
        'Country Name': 'South',
        'alpha_income': .7,
        'alpha_fin': .3,
        'mu': '0.18761',
        'L0': '0.67',
        'L1': '6.',
        'L2': '.07',
    }
    build_country(model, paramz)
    generate_supply_allocation(model, 'N')
    generate_supply_allocation(model, 'S')
    # model.AddExogenous('N_GOV', 'DEM_GOOD', '[25.]*105')
    # model.AddExogenous('S_GOV', 'DEM_GOOD', '[25.]*105')
    model.AddExogenous('S_GOOD', 'MU', '[0.18761]*5 + [0.21] * 105')
    model.AddGlobalEquation('N_trade_balance', 'North trade balance',
                            'S_GOOD__SUP_N_BUS - N_GOOD__SUP_S_BUS')
    model.EquationSolver.MaxTime = 40
    model.EquationSolver.TraceStep = 5
    # model.EquationSolver.ParameterSolveInitialSteadyState = True
    # model.EquationSolver.ParameterErrorTolerance = 1e-4
    return model


if __name__ == '__main__':
    register_standard_logs('output', __file__)
    mod = build_model()
    mod.main()
