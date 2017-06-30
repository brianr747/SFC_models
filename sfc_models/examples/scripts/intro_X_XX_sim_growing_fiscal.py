# coding=utf-8
from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot


register_standard_logs('output', __file__)
mod = Model()
country = Country(mod, 'CO')
Household(country, 'HH')
gov = ConsolidatedGovernment(country, 'GOV')
FixedMarginBusiness(country, 'BUS')
Market(country, 'GOOD')
Market(country, 'LAB')
TaxFlow(country, 'TAX', taxrate=.2)
# Set the demand for goods to be (1.02)^k
gov.SetEquationRightHandSide('DEM_GOOD', 'pow(1.02, k)')

mod.AddGlobalEquation('DEBT_GDP', 'DEBT-TO-GDP RATIO', '-100.*GOV__F/BUS__SUP_GOOD')
mod.AddGlobalEquation('DEFICIT', 'DEFICIT', '-100.*GOV__INC/BUS__SUP_GOOD')
mod.EquationSolver.MaxTime = 40
mod.EquationSolver.ParameterSolveInitialSteadyState = False
mod.main()
k = mod.GetTimeSeries('k')

Rat = mod.GetTimeSeries('DEBT_GDP')
Def = mod.GetTimeSeries('DEFICIT')
spend = mod.GetTimeSeries('GOV__DEM_GOOD')

Quick2DPlot(k, Def, 'Deficit Ratio (2% growth/year)', filename='intro_X_XX_sim_growing_deficit.png')
Quick2DPlot(k, Rat, title='Debt-to-GDP Ratio, (2% growth/year)', filename='intro_X_XX_sim_growing_fiscal.png')
