"""
Consumption Propensity Shock Model

A small riff on the previous Investment Accelerator Model. Only difference is that
investment propensity is fixed, and propensity to consume changes.

Uses a lot of lagged information to ensure solution stability.

Base it off Model SIM, but beef up the business sector. By implication, all prices
are fixed.
"""

from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot
from sfc_models.sector import Sector
from sfc_models.utils import Logger

# Create the new business sector class

class BusinessWithInvestment(FixedMarginBusiness):
    def __init__(self, country, code, long_name=''):
        if long_name == '':
            long_name = 'Business with Investment {0} in Country {1}'.format(code, country.Code)
        labour_input_name = 'LAB'
        output_name = 'GOOD'
        profit_margin=0.0
        FixedMarginBusiness.__init__(self, country, code, long_name, profit_margin,
                                     labour_input_name, output_name)
        self.AddVariable('INV', 'Inventory', 'LAG_INV + PROD - SUP_GOOD - INVEST')
        self.AddVariable('LAG_INV', 'Lagged Inventory', 'INV(k-1)')
        # Target inventory = 1*market demand
        # Production = (expected demand) + (desired change in inventory)
        # expected demand = investment + previous market demand
        # desired change in inventory = .5*(previous market demand - existing inventory).
        self.AddVariable('PROD', 'Production Level', 'max(0,INVEST + LAG_SUP_GOOD + .1*(LAG_SUP_GOOD - LAG_INV))')
        self.AddVariable('INVSALES', 'Inventory/Sales Ratio', 'INV/SUP_GOOD')
        self.AddVariable('CAPITAL', 'Stock of Capital', '0.95*LAG_CAP + INVEST')
        # Production function: Y = K(t-1)^.5 N^.5
        # N = Number of hours = P^2 / (K(t-1)
        self.AddVariable('NUMHOURS', 'Number of Hours Demanded', '(PROD*PROD)/LAG_CAP')
        self.AddVariable('WAGERATE', 'Wage rate', 'DEM_LAB/NUMHOURS')
        self.AddVariable('LAG_HOURS', 'Lagged Number of Hours', 'NUMHOURS(k-1)')
        self.AddVariable('LAG_CAP', 'Lagged Capital', 'CAPITAL(k-1)')
        self.AddVariable('LAG_PROD', 'Lagged Production', 'PROD(k-1)')
        self.AddVariable('LAG_SUP_GOOD', 'Lagged Supply to market', 'SUP_GOOD(k-1)')
        # Target capital = (alpha_capital)*(previous # of hours worked)
        self.AddVariable('ALPHA_CAPITAL', 'Multiplier for target capital', '1.')
        self.AddVariable('CAPITAL_TARGET', 'Target Level for capital', 'ALPHA_CAPITAL*LAG_HOURS')
        self.AddVariable('INVEST', 'Gross Investment', 'max(0., .05*LAG_CAP + .1*(CAPITAL_TARGET-LAG_CAP))')
        self.AddVariable('CAPITAL_RATIO', 'Ratio of Capital to target', 'CAPITAL/CAPITAL_TARGET')
        # Pro-Forma Profits: 20% of sales - depreciation.
        self.AddVariable('PROFORMA', 'Pro-Forma Profits (Lagged)', '0.20*LAG_SUP_GOOD - .05*LAG_CAP')
        self.AddVariable('DIVPAID', 'Dividends Paid', '.055* LAG_F + 0.8*PROFORMA')
        self.AddVariable('DEM_LAB', 'Demand For Labour', '0.8*PROD')


    def _GenerateEquations(self):
        # self.AddVariable('SUP_GOOD', 'Supply of goods', '<TO BE DETERMINED>')
        wage_share = 1.0 - self.ProfitMargin
        Logger('Searching for Market Sector with Code {0} in parent country', priority=4,
               data_to_format=(self.OutputName,))

        # Since we have inventories, profits are volume of sales * profit margin
        self.SetEquationRightHandSide('PROF', '.1 * SUP_GOOD')
        for s in self.Parent.SectorList:
            if s.Code == 'HH':
                Logger('Adding dividend flow', priority=5)
                self.AddCashFlow('-DIV', 'DIVPAID', 'Dividends paid', is_income=False)
                s.AddCashFlow('DIV', self.GetVariableName('DIVPAID'), 'Dividends received', is_income=True)
                break

def main():
    # The next line of code sets the name of the output files based on the code file's name.
    # This means that if you paste this code into a new file, get a new log name.
    register_standard_logs('output', __file__)
    # Create model, which holds all entities
    mod = Model()
    mod.EquationSolver.TraceStep = 10
    mod.EquationSolver.MaxTime = 100
    # Create first country - Canada. (This model only has one country.)
    can = Country(mod, 'CA', 'Canada')
    # Create sectors
    gov = ConsolidatedGovernment(can, 'GOV', 'Government')
    hh = Household(can, 'HH', 'Household')
    # A literally non-profit business sector
    bus = BusinessWithInvestment(can, 'BUS', 'Business Sector')
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    tax = TaxFlow(can, 'TF', 'TaxFlow', .2)
    labour = Market(can, 'LAB', 'Labour market')
    goods = Market(can, 'GOOD', 'Goods market')
    # Initial conditions
    bus.AddInitialCondition('CAPITAL', 100.)
    bus.AddInitialCondition('PROD', 100.)
    bus.AddInitialCondition('INV', 95.)
    # bus.AddInitialCondition('LAG_INV', 100.)

    # bus.AddInitialCondition('LAG_SUP_GOOD', 95.)
    bus.AddInitialCondition('SUP_GOOD', 95.)
    bus.AddInitialCondition('NUMHOURS', 100.)
    # Initialise money holdings
    bizcash = 69
    hhcash = 76.
    gov.AddInitialCondition('F', -(bizcash+hhcash))
    hh.AddInitialCondition('F', hhcash)
    bus.AddInitialCondition('F', bizcash)
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    #mod.AddExogenous('GOV', 'DEM_GOOD', '[19.,] * 20 + [25.]*100')
    mod.AddExogenous('GOV', 'DEM_GOOD', '[19.,] * 105')
    mod.AddExogenous('BUS', 'ALPHA_CAPITAL', '[1.,] * 105')
    mod.AddExogenous('HH', 'AlphaIncome', [.6,] * 5 + [.55] * 100)

    # Build the model
    mod.main()

    # First set of charts: short-term effects
    CUT = 9
    k = mod.GetTimeSeries('k', cutoff=CUT)
    goods_produced = mod.GetTimeSeries('BUS__PROD', cutoff=CUT)
    capital_ratio = mod.GetTimeSeries('BUS__CAPITAL_RATIO', cutoff=CUT)
    investment = mod.GetTimeSeries('BUS__INVEST', cutoff=CUT)
    dem_labour = mod.GetTimeSeries('BUS__DEM_LAB', cutoff=CUT)
    inventory = mod.GetTimeSeries('BUS__INV', cutoff=CUT)
    inventory_sales = mod.GetTimeSeries('BUS__INVSALES', cutoff=CUT)
    profit = mod.GetTimeSeries('BUS__PROFORMA', cutoff=CUT)
    consumption = mod.GetTimeSeries('HH__DEM_GOOD', cutoff=CUT)
    # Fix initial condition
    investment[0] = 5.
    capital_ratio[0] = 1.
    inventory_sales[0] = 1.
    profit[0] = 14.
    consumption[0] = 76.
    print(profit)
    if True:
        p = Quick2DPlot([k,k], [goods_produced, consumption], title='Effect Of Shock',
                    filename='consumption_propensity_01.png', run_now=False)
        p.Legend = ['Production', 'Household Consumption']
        p.DoPlot()
        Quick2DPlot(k, inventory, 'Inventory', filename='consumption_propensity_02.png')
        Quick2DPlot(k, investment, 'Gross Investment', filename='consumption_propensity_03.png')
        # Quick2DPlot(k, inventory, 'Inventory', filename='consumption_propensity_02.png')
        return
        Quick2DPlot(k, capital_ratio, 'Ratio of Capital to Target', filename='consumption_02.png')
        Quick2DPlot(k, dem_labour, 'Wage Income', filename='consumption_03.png')

        Quick2DPlot(k, inventory_sales, 'Inventory/Sales Ratio', filename='consumption_05.png')
        Quick2DPlot(k, goods_produced, 'Goods Produced (National Output)', filename='consumption_propensity_06.png')
    # Quick2DPlot(k, profit, 'Business Sector (Pro-Forma) Profit', filename='recession_investment_07.png')
    CUT = 100
    k = mod.GetTimeSeries('k', cutoff=CUT)
    goods_produced = mod.GetTimeSeries('BUS__PROD', cutoff=CUT)
    fisc_bal =  mod.GetTimeSeries('GOV__FISC_BAL', cutoff=CUT)
    profit = mod.GetTimeSeries('BUS__PROFORMA', cutoff=CUT)
    consumption = mod.GetTimeSeries('HH__DEM_GOOD', cutoff=CUT)

    # Fix initial conditions
    profit[0] = 14.

    Quick2DPlot(k, goods_produced, 'Goods Produced (National Output) - Long Run', filename='recession_investment_07.png')
    Quick2DPlot(k, fisc_bal, 'Government Fiscal Balance - Long Run',
                filename='recession_investment_08.png')
    Quick2DPlot(k, profit, 'Business Sector (Pro-Forma) Profits',
                filename='recession_investment_09.png')








if __name__ == '__main__':
    main()
