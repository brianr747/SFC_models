# coding=utf-8
from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot


register_standard_logs('output', __file__)
mod = Model()
country = Country(mod, 'CO')
Household(country, 'HH')
ConsolidatedGovernment(country, 'GOV')
FixedMarginBusiness(country, 'BUS', profit_margin=.025)
Market(country, 'GOOD')
Market(country, 'LAB')
TaxFlow(country, 'TAX', taxrate=.2)
# At time period 25, cut spending to 17 (from 20)
mod.AddExogenous('GOV', 'DEM_GOOD', [20.,]* 25 + [17.,]*20)
mod.AddGlobalEquation('DEBT_GDP', 'DEBT-TO-GDP RATIO', '-100.*GOV__F/BUS__SUP_GOOD')
mod.AddGlobalEquation('DEFICIT', 'DEFICIT', '-1.*GOV__INC')
mod.EquationSolver.MaxTime = 40
mod.main()
k = mod.GetTimeSeries('k')

Rat = mod.GetTimeSeries('DEBT_GDP')
Def = mod.GetTimeSeries('GOV__INC')
spend = mod.GetTimeSeries('GOV__DEM_GOOD')

p = Quick2DPlot([k, k], [spend, Def], title='Spending and Deficit', filename='intro_X_XX_multiplier_deficit.png',
                run_now=False)
p.Legend = ['Goverment Consumption', 'Deficit']
p.DoPlot()
Quick2DPlot(k, Rat, title='Debt-to-GDP Ratio', filename='intro_X_XX_multiplier_debt_gdp.png')
