# coding=utf-8
from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot


def build_model(government_consumption):
    mod = Model()
    country = Country(mod, 'CO')
    Household(country, 'HH')
    ConsolidatedGovernment(country, 'GOV')
    FixedMarginBusiness(country, 'BUS')
    Market(country, 'GOOD')
    Market(country, 'LAB')
    TaxFlow(country, 'TAX', taxrate=.2)
    mod.AddExogenous('GOV', 'DEM_GOOD', [15.,]*5 + [government_consumption,]* 50)
    mod.AddGlobalEquation('DEBT_GDP', 'DEBT-TO-GDP RATIO', '-100.*GOV__F/BUS__SUP_GOOD')
    mod.AddGlobalEquation('DEFICIT', 'DEFICIT-TO-GDP RATIO', '-100.*GOV__INC/BUS__SUP_GOOD')
    mod.EquationSolver.MaxTime = 40
    mod.EquationSolver.ParameterSolveInitialSteadyState = True
    return mod

mod20 = build_model(government_consumption=20.0)
mod20.main()
mod25 = build_model(government_consumption=25.0)
mod25.main()
k = mod20.GetTimeSeries('k')
Y20 = mod20.GetTimeSeries('BUS__SUP_GOOD')
Rat20 = mod20.GetTimeSeries('DEBT_GDP')
Def20 = mod20.GetTimeSeries('GOV__INC')
Y30 = mod25.GetTimeSeries('BUS__SUP_GOOD')
Rat30 = mod25.GetTimeSeries('DEBT_GDP')
Def30 = mod25.GetTimeSeries('GOV__INC')

p = Quick2DPlot([k,k], [Y20, Y30], title='Output in Simulations', filename='intro_X_XX_sim_fiscal.png',
                run_now=False)
p.Legend = ['Scenario #1', 'Scenario #2']
p.DoPlot()
p = Quick2DPlot([k,k], [Def20, Def30], title='Fiscal Balance', filename='intro_X_XX_sim_deficit.png',
            run_now=False)
p.Legend = ['Scenario #1', 'Scenario #2']
p.DoPlot()
p = Quick2DPlot([k, k], [Rat20, Rat30], title='Debt-to-GDP Ratio', filename='intro_X_XX_sim_debt_gdp.png',
            run_now=False)
p.Legend = ['Scenario #1', 'Scenario #2']
p.DoPlot()