# coding=utf-8
"""
intro_6_06_gold_standard_G.py

Model similar to model OPENG from Godley and Lavoie's "Monetary Economics."

In this model, governments cut spending if they are in danger of breaching their desired
gold cover ratio.
"""

from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot

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
    model.AddExogenous('S_GOOD', 'MU', '[0.18761]*5 + [0.21] * 405')
    model.AddGlobalEquation('N_trade_balance', 'North trade balance',
                            'S_GOOD__SUP_N_BUS - N_GOOD__SUP_S_BUS')
    model.EquationSolver.MaxTime = 80
    model.EquationSolver.TraceStep = 5
    model.EquationSolver.ParameterSolveInitialSteadyState = True
    # model.EquationSolver.ParameterErrorTolerance = 1e-4
    return model


def main():
    register_standard_logs('output', __file__)
    mod = build_model()
    mod.main()
    k = mod.GetTimeSeries('k')
    gc = mod.GetTimeSeries('S_GOV__GOLDCOVER')
    g = mod.GetTimeSeries('S_GOV__DEM_GOOD')
    Yd = mod.GetTimeSeries('S_HH__AfterTax')
    N_Yd = mod.GetTimeSeries('N_HH__AfterTax')
    Quick2DPlot(k,gc,'Southern Government Gold Cover', filename='intro_gold_cover.png')
    Quick2DPlot(k, g, 'Southern Government Consumption (G)', filename='intro_gold_gov_spend.png')
    Quick2DPlot(k, Yd, 'Southern Household Disposable Income', filename='intro_gold_Yd.png')
    Quick2DPlot(k, N_Yd, 'Northern Household Disposable Income', filename='intro_gold_N_Yd.png')

if __name__ == '__main__':
    main()


