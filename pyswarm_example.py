from scipy.optimize import rosen, differential_evolution
from numpy.random import random
from numpy import sqrt, array
from copy import deepcopy
# from joblib import Parallel, delayed
from openmdao.api import Problem
from workflow_cheap import LCOE
import time
from farm_description import NT

prob = Problem()
# print clock(), "Before defining model"
prob.model = LCOE()
# print clock(), "Before setup"
prob.setup()

from pyswarm import pso

def objfunc(x):
    layout = [[x[i], x[74 + i]] for i in range(74)]
    prob['indep2.layout'] = layout
    prob.run_model()
    f = prob['analysis.lcoe'][0]
    f += prob['constraint_boundary.n_constraint_violations'][0] * 5.0
    print f
    # g = [0.0] * 2
    # g[0] = prob['constraint_boundary.magnitude_violations'][0]
    # g[1] = prob['constraint_distance.magnitude_violations'][0]

    return f

def objfunc2(x):
    prob['indep2.downwind_spacing'] = x[0]
    prob['indep2.crosswind_spacing'] = x[1]
    prob['indep2.odd_row_shift_spacing'] = x[2]
    prob['indep2.layout_angle'] = x[3]
    prob.run_model()
    f = prob['analysis.lcoe'][0]
    f += prob['constraint_boundary.n_constraint_violations'][0] * 5.0
    print f
    # g = [0.0] * 2
    # g[0] = prob['constraint_boundary.magnitude_violations'][0]
    # g[1] = prob['constraint_distance.magnitude_violations'][0]

    return f

def con1(x):	
    layout = [[x[i], x[74 + i]] for i in range(74)]
    prob['indep2.layout'] = layout
    prob.run_model()
    g1 = - prob['constraint_boundary.magnitude_violations'][0]
    g2 = - prob['constraint_distance.magnitude_violations'][0]
    # g[1] = prob['constraint_distance.magnitude_violations'][0]
    return [g1, g2]
# (570.0, 2500.0), (570.0, 2500.0), (0.0, 1250.0), (0.0, 180.0)]
lb = [570.0, 570.0, 0.0, 0.0]
ub = [2500.0, 2500.0, 1250.0, 180.0]

xopt, fopt = pso(objfunc2, lb, ub, f_ieqcons=None)
print xopt
print fopt
