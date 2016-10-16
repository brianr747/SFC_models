from plot_for_examples import Quick2DPlot

import sfc_models.gl_book.SIM_machine_generated as generator

filename = 'SIM_model.py'
obj = generator.build_model()
obj.main(filename)

# Can only import now...
import SIM_model
obj = SIM_model.SFCModel()
obj.main()
print(obj.Y)
#Quick2DPlot(range(0, 20), obj.Y)


