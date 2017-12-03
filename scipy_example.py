from scipy.optimize import rosen, differential_evolution
from numpy.random import random
from numpy import sqrt, array
from copy import deepcopy
# from joblib import Parallel, delayed
from openmdao.api import Problem
from workflow_cheap import LCOE
import time

prob = Problem()
# print clock(), "Before defining model"
prob.model = LCOE()
# print clock(), "Before setup"
prob.setup()

def objfunc(x):
    prob['indep2.downwind_spacing'] = x[0]
    prob['indep2.crosswind_spacing'] = x[1]
    prob['indep2.odd_row_shift_spacing'] = x[2]
    prob['indep2.layout_angle'] = x[3]
    # layout = [[x[i], x[74 + i]] for i in range(74)]
    # prob['indep2.layout'] = layout
    prob.run_model()
    f = prob['analysis.lcoe'][0]
    # g = [0.0] * 2
    # g[0] = prob['constraint_boundary.magnitude_violations'][0]
    # g[1] = prob['constraint_distance.magnitude_violations'][0]

    return f

bounds = [(570.0, 2500.0), (570.0, 2500.0), (0.0, 1250.0), (0.0, 180.0)]
# bounds = [(484000.0, 504000.0) for _ in range(74)] + [(5.715e6, 5.74e6) for _ in range(74)]
result = differential_evolution(objfunc, bounds, popsize=1)
# initial_guess = [1000.0, 1400.0, 0.0, 30.0]
# minimizer_kwargs = {"method":"Nelder-Mead"}
# result = basinhopping(objfunc, initial_guess, minimizer_kwargs=minimizer_kwargs)
print result.x, result.fun
# (array([1., 1., 1., 1., 1.]), 1.9216496320061384e-19)