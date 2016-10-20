from sfc_models.models import *
from sfc_models.iterative_machine_generator import IterativeMachineGenerator
from sfc_models.extras import Quick2DPlot


def main():
    mod = Model()
    can = Country(mod, 'Canada', 'CA')
    gov = DoNothingGovernment(can, 'Government', 'GOV')
    hh = Household(can, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
    bus = Sector(can, 'Business Sector', 'BUS')

    tax = TaxFlow(can, 'TaxFlow', 'TF', .2)
    labour = Market(can, 'Labour market', 'LAB')
    goods = Market(can, 'Goods market', 'GOOD')
    goods.AffectsNet = False
    mod.GenerateFullSectorCodes()
    # Patch in the business sector...
    bus.AddVariable('SUP_GOOD', 'Supply of goods', '<TO BE DETERMINED>')
    bus.AddVariable('DEM_LAB', 'Demand for labour', 'GOOD_SUP_GOOD')
    mod.GenerateEquations()
    mod.GenerateIncomeEquations()
    # Exogenous:
    mod.Exogenous = [('GOV', 'DEM_GOOD', '[20.,] * 5 + [25.,] * 100')]
    mod.ForceExogenous()
    #mod.DumpEquations()
    eqns = mod.CreateFinalEquations()
    eqns += '\n\nMaxTime = 100\nErr_Tolerance=0.001'
    print(eqns)
    generator = IterativeMachineGenerator(eqns)
    generator.main('SIM_Machine_Model.py')

    import SIM_Machine_Model
    obj = SIM_Machine_Model.SFCModel()
    obj.main()
    obj.WriteCSV('dump.csv')
    # Lop off t = 0 because it represents hard-coded initial conditions
    Quick2DPlot(obj.t[1:], obj.GOOD_SUP_GOOD[1:], 'Goods supplied (national production Y)')
    Quick2DPlot(obj.t[1:], obj.HH_F[1:], 'HH_F')
    # Quick2DPlot(obj.t[1:], obj.BUS_F[1:], 'BUS_F')
    # Quick2DPlot(obj.t[1:], obj.GOV_F[1:], 'GOV_F')
    # Quick2DPlot(obj.t[1:], obj.HH_INC[1:], 'HH_INC')
    # Quick2DPlot(obj.t[1:], obj.TF_T[1:], 'TF_T')


if __name__ == '__main__':
    main()