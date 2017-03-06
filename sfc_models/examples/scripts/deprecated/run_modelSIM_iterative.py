from matplotlib import pyplot as plt


import sfc_models.gl_book.model_SIM_iterative as model

obj = model.ModelSIMiterative()

obj.main()

print(obj.H)
plt.plot(obj.time_axis, obj.H)
plt.show()


