from scipy.optimize import differential_evolution
from openmdao.api import Problem, Group, IndepVarComp
from workflow_cheap import LCOE
from constraints_openmdao import MinDistance, WithinBoundaries
from farm_description import n_quadrilaterals, areas, separation_equation_y, NT
from turbine_description import rotor_radius
from random import uniform
from transform_quadrilateral import AreaMapping
import numpy as np

squares = []
for n in range(n_quadrilaterals):
    square = [[1.0 / n_quadrilaterals * n, 0.0], [n * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 0.0]]
    squares.append(square)
borssele_mapping1 = AreaMapping(areas[0], squares[0])
borssele_mapping2 = AreaMapping(areas[1], squares[1])

def create_random():
    xt, yt = 2.0, 2.0
    while (xt < 0.0 or xt > 1.0) or (yt < 0.0 or yt > 1.0):
        xb, yb = uniform(min(min([item[0] for item in areas[0]]), min([item[0] for item in areas[1]])), max(max([item[0] for item in areas[0]]), max([item[0] for item in areas[1]]))), uniform(min(min([item[1] for item in areas[0]]), min([item[1] for item in areas[1]])), max(max([item[1] for item in areas[0]]), max([item[1] for item in areas[1]])))
        if yb > separation_equation_y(xb):
            xt, yt = borssele_mapping1.transform_to_rectangle(xb, yb)
        else:
            xt, yt = borssele_mapping2.transform_to_rectangle(xb, yb)
    return [xb, yb]

prob = Problem()
prob.model = LCOE()
prob.setup()


def obj(x):
    prob['indep2.layout'] = [[x[i], x[i+1]] for i in range(0, NT * 2, 2)]
    prob.run_model()
    ans = prob['analysis.lcoe'][0]
    ans += prob['constraint_boundary.n_constraint_violations'] * 5.0 + prob['constraint_distance.n_constraint_violations'] * 5.0

    return ans

bounds = [(484000.0, 504000.0), (5.715e6, 5.74e6)] * 74

result = differential_evolution(obj, bounds)

print result.x, result.fun
