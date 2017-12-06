from scipy.optimize import minimize
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

class constraint1(Group):    
    def setup(self):
        indep3 = self.add_subsystem('indep3', IndepVarComp())
        indep3.add_output("layout", val=np.array([create_random() for _ in range(NT)]))
        indep3.add_output("radius", val=rotor_radius)
        self.add_subsystem("mindistance", MinDistance())
        self.connect("indep3.layout", "mindistance.orig_layout")
        self.connect("indep3.radius", "mindistance.turbine_radius")

class constraint2(Group):
    def setup(self):
        indep4 = self.add_subsystem('indep4', IndepVarComp())
        indep4.add_output("layout", val=np.array([create_random() for _ in range(NT)]))
        indep4.add_output("areas", val=areas)
        self.add_subsystem("inbounds", WithinBoundaries())
        self.connect("indep4.layout", "inbounds.layout")
        self.connect("indep4.areas", "inbounds.areas")

cons1 = Problem()
cons1.model = constraint1()
cons1.setup()

cons2 = Problem()
cons2.model = constraint2()
cons2.setup()


def obj(x):
    prob['indep2.layout'] = [[x[i], x[i+1]] for i in range(0, NT * 2, 2)]
    prob.run_model()
    ans = prob['analysis.lcoe'][0]
    return ans

def con1(x):
    cons1['indep3.layout'] = [[x[i], x[i+1]] for i in range(0, NT * 2, 2)]
    cons1.run_model()
    ans = cons1['mindistance.magnitude_violations'][0]

def con2(x):
    cons2['indep4.layout'] = [[x[i], x[i+1]] for i in range(0, NT * 2, 2)]
    cons2.run_model()
    ans = cons2['inbounds.magnitude_violations'][0]

con1d = {'type':'ineq', 'fun':con1}

con2d = {'type':'ineq', 'fun':con2}

const = (con1d, con2d)

x1 = []
for _ in range(NT):
    x1 += create_random()

opts = {'disp':True, 'maxiter':10000, 'iprint':1}

a = minimize(obj, x0=x1, method='COBYLA', constraints=const, options=opts)

print a
