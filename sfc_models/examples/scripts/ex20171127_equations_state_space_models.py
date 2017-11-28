"""
ex20171127_equations_state_space_models.py

And now for something completely different...

This code just uses the equation parser and solver to generate the solutions for state space models.

One of the stranger applications of framework code...
"""


from sfc_models.equation_solver import EquationSolver
from sfc_models.examples.Quick2DPlot import Quick2DPlot
import matplotlib.pyplot as plt

def generate_model(eqns, use_control=False):
    if use_control:
        eqns += """
        u = (-.7 * x + .75 * r)/.05
        u(0) = 1.0
        exogenous
        r = [1.] * 10 + [2.]*21
            """
    else:
        eqns += """
    exogenous
    u = [1.] * 10 + [2.]*21
        """
    out = EquationSolver(eqns)
    out.Parser.MaxTime = 30
    out.SolveEquation()
    return out


def generate_base_model(a, use_control):
    eqns = """
    x = (1-a)*lag_x + a * lag_u
    y = x
    lag_x = x(k-1)
    lag_u = u(k-1)
    x(0) = 1.
    a = {0}
    """.format(a)
    # print(eqns)
    out = generate_model(eqns, use_control)
    return out

def generate_actual_model(use_control):
    eqns = """
    x = (1-a)*lag_x + a * lag_h
    y = x
    g = lag_u
    h = lag_g
    lag_x = x(k-1)
    lag_u = u(k-1)
    lag_g = g(k-1)
    lag_h = h(k-1)
    x(0) = 1.
    g(0) = 1.
    h(0) = 1.
    a = .05
    """
    return generate_model(eqns, use_control)



def main():
    mod_0 = generate_base_model(.05, use_control=False)
    k = mod_0.TimeSeries['k']
    x_0 = mod_0.TimeSeries['x']
    mod_1 = generate_base_model(.005, use_control=False)
    x_1 = mod_1.TimeSeries['x']
    mod_2 = generate_base_model(.09, use_control=False)
    x_2 = mod_2.TimeSeries['x']

    mod_act = generate_actual_model(use_control=False)
    x_act = mod_act.TimeSeries['x']
    plt.plot(k, x_0, 'bo', k, x_1, 'b+', k, x_2, 'b--')
    plt.title('Assumed Model Output, Plus Perturbed Systems')
    plt.grid()
    plt.show()


    plt.plot(k, x_act, '-ro', k, x_0, 'bo', k, x_1, 'b+', k, x_2, 'b--')
    plt.title('True Model, Plus Assumed Outputs')
    plt.grid()
    plt.show()

    mod_0 = generate_base_model(.05, use_control=True)
    k = mod_0.TimeSeries['k']
    x_0 = mod_0.TimeSeries['x']
    mod_1 = generate_base_model(.005, use_control=True)
    x_1 = mod_1.TimeSeries['x']
    mod_2 = generate_base_model(.09, use_control=True)
    x_2 = mod_2.TimeSeries['x']

    mod_act = generate_actual_model(use_control=True)
    x_act = mod_act.TimeSeries['x']
    plt.plot(k, x_0, 'bo', k, x_1, 'b+', k, x_2, 'b--')
    plt.title('Assumed Feedback Control Response')
    plt.grid()
    plt.show()


    plt.plot(k, x_act, '-ro', k, x_0, 'bo', k, x_1, 'b+', k, x_2, 'b--')
    plt.title('Actual Feedback Response')
    plt.grid()
    plt.show()


    # plt.plot(k, x_act, 'ro', k, x_1, 'b+', k, x_2, 'b--')
    # plt.grid()
    # plt.show()


    #Quick2DPlot(k, x_0, 'Base Output')


if __name__ == '__main__':
    main()
