from __future__ import print_function
import math
import random
from anneal import Annealer
from scipy.optimize import rosen, differential_evolution
from numpy.random import random
from numpy import sqrt, array
from copy import deepcopy
# from joblib import Parallel, delayed
from openmdao.api import Problem
from workflow_cheap import LCOE
import time
from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder, ExplicitComponent
import numpy as np
from time import time, clock
from constraints_openmdao import MinDistance, WithinBoundaries
# from regular_parameterised import RegularLayout
from call_workflow_once import call_workflow_layout as analysis_cheap
from farm_description import n_quadrilaterals, areas, separation_equation_y, NT
from turbine_description import rotor_radius
from random import uniform
from transform_quadrilateral import AreaMapping
from regular_parameterised import RegularLayout

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

class TravellingSalesmanProblem(Annealer):

    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor

    def move(self):
        """Swaps two cities in the route."""
        self.state = [uniform(570.0, 2500.0), uniform(570.0, 2500.0), uniform(0.0, 1250.0), uniform(0.0, 180.0)]

    def energy(self):
        """Calculates the length of the route."""
        e = objfunc(self.state)
        return e



if __name__ == '__main__':

    # latitude and longitude for the twenty largest U.S. cities
    
    # initial state, a randomly-ordered itinerary
    init_state = [uniform(570.0, 2500.0), uniform(570.0, 2500.0), uniform(0.0, 1250.0), uniform(0.0, 180.0)]
    # random.shuffle(init_state)

    # create a distance matrix
    tsp = TravellingSalesmanProblem(init_state)
    tsp.steps = 500
    # since our state is just a list, slice is the fastest way to copy
    tsp.copy_strategy = "slice"
    state, e = tsp.anneal()

    print()
    print("%i result:" % e)
    print(state)
