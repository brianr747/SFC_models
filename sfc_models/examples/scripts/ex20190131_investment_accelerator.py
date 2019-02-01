"""
Investment Accelerator Model

Attempt at the simplest possible investment accelerator model. Has a number of
simplifications; no attempt to reflect more standard models.

Since we have a more advanced production function, need to add inventories. This was
not done in the existing framework, so extending the business sector class
locally.

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
        self.AddVariable('INV', 'Inventory', 'LAG_INV + PROD - SUP_GOOD')
        self.AddVariable('LAG_INV', 'Lagged Inventory', 'INV(k-1)')
        # Target inventory = 1*market demand
        # Production = (expected demand) + (desired change in inventory)
        # expected demand = investment + previous market demand
        # desired change in inventory = .5*(previous market demand - existing inventory).
        self.AddVariable('PROD', 'Production Level', 'max(0,INVEST + LAG_SUP_GOOD + (LAG_SUP_GOOD - LAG_INV))')
        self.AddVariable('CAPITAL', 'Stock of Capital', '0.95*LAG_CAP + INVEST')
        # Production function: Y = K(t-1)^.5 N^.5
        # N = Number of hours = P^2 / (K(t-1)
        self.AddVariable('NUMHOURS', 'Number of Hours Demanded', '(PROD*PROD)/LAG_CAP')
        self.AddVariable('LAG_CAP', 'Lagged Capital', 'CAPITAL(k-1)')
        self.AddVariable('LAG_PROD', 'Lagged Production', 'PROD(k-1)')
        self.AddVariable('LAG_SUP_GOOD', 'Lagged Supply to market', 'SUP_GOOD(k-1)')
        # Target capital = (target capital)*(previous production)
        self.AddVariable('CAPITAL_TARGET', 'Target ratio for capital', '1.')
        self.AddVariable('INVEST', 'Gross Investment', 'max(0., .05*LAG_CAP + CAPITAL_TARGET*(LAG_PROD-LAG_CAP))')
        # Ugly dividends payment: 10% of cash
        self.AddVariable('DIVPAID', 'Dividends Paid', '0.1*LAG_F')


    def _GenerateEquations(self):
        # self.AddVariable('SUP_GOOD', 'Supply of goods', '<TO BE DETERMINED>')
        wage_share = 1.0 - self.ProfitMargin
        Logger('Searching for Market Sector with Code {0} in parent country', priority=4,
               data_to_format=(self.OutputName,))
        self.AddVariable('DEM_LAB', 'Demand For Labour', '0.9*PROD')
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
    mod.EquationSolver.MaxTime = 40
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
    bus.AddInitialCondition('INV', 100.)
    bus.AddInitialCondition('LAG_INV', 100.)
    gov.AddInitialCondition('F', -150.)
    hh.AddInitialCondition('F', 100.)
    bus.AddInitialCondition('F', 50.)
    bus.AddInitialCondition('LAG_SUP_GOOD', 100.)
    bus.AddInitialCondition('SUP_GOOD', 100.)


    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('GOV', 'DEM_GOOD', '[25.,] * 105')
    # Build the model
    mod.main()
    CUT = 30
    k = mod.GetTimeSeries('k', cutoff=CUT)
    goods_produced = mod.GetTimeSeries('BUS__SUP_GOOD', cutoff=CUT)
    Quick2DPlot(k, goods_produced, 'Goods Produced (National Output)')




if __name__ == '__main__':
    main()
