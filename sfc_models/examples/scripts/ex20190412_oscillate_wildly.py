"""
ex20190412_oscillate_wildly.py

This is an example of how solutions can be wildly unstable from one period to the next.

This is based on model SIM (again...), with a rapidly changing tax rate.

"""

# This next line imports all of the objects used.
# The syntax "from <module> import *" is frowned upon, but I want to reduce the number of lines of
# code in these simpler examples.
from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot


def main():
    # The next line of code sets the name of the output files based on the code file's name.
    # This means that if you paste this code into a new file, get a new log name.
    register_standard_logs('output', __file__)
    # Create model, which holds all entities
    mod = Model()
    mod.EquationSolver.TraceStep = 10
    # Create first country - Canada. (This model only has one country.)
    can = Country(mod, 'CA', 'Canada')
    # Create sectors
    gov = ConsolidatedGovernment(can, 'GOV', 'Government')
    hh = Household(can, 'HH', 'Household')
    # A literally non-profit business sector
    bus = FixedMarginBusiness(can, 'BUS', 'Business Sector')
    # Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
    tax = TaxFlow(can, 'TF', 'TaxFlow', .2)
    labour = Market(can, 'LAB', 'Labour market')
    goods = Market(can, 'GOOD', 'Goods market')
    # Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
    mod.AddExogenous('GOV', 'DEM_GOOD', '[20.,] * 105')
    mod.AddExogenous('TF', 'TaxRate', '[.15, .4, .05, .1, .02, .08, .4, .1, .02] + [.2]*100' )
    mod.EquationSolver.ParameterSolveInitialSteadyState = True
    # Build the model
    mod.main()
    CUT = 10
    k = mod.GetTimeSeries('k', cutoff=CUT)
    goods_produced = mod.GetTimeSeries('BUS__SUP_GOOD', cutoff=CUT)
    fisc_bal = mod.GetTimeSeries('GOV__FISC_BAL', cutoff=CUT)
    Quick2DPlot(k, goods_produced, 'National Output With Erratic Taxes', filename='oscillate_wildly.png')
    Quick2DPlot(k, fisc_bal, 'Government Fiscal Balance Erratic Taxes', filename='oscillate_wildly_2.png')




if __name__ == '__main__':
    main()
