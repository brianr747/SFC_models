from sfc_models.models import *

def main():
    mod = Model()
    can = Country(mod, 'Canada', 'CA')
    gov = DoNothingGovernment(can, 'Government', 'GOV')
    hh = Household(can, 'Household', 'HH', .9, .2)
    tax = TaxFlow(can, 'TaxFlow', 'TF', .3)
    labour = Market(can, 'Labour market', 'LAB')
    goods = Market(can, 'Goods market', 'GOOD')
    mod.GenerateFullSectorCodes()
    mod.GenerateEquations()
    labour.DumpEquations()
    mod.GenerateIncomeEquations()
    mod.DumpEquations()


if __name__ == '__main__':
    main()