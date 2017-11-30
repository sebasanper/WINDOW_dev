import numpy as np

from openmdao.api import Problem, ScipyOptimizer
# fron openmdao.api imprt pyOptSparseDrivers
from workflow_cheap import LCOE

prob = Problem()
model = prob.model = LCOE()
# prob.driver = pyOptSparseDriver()
prob.driver = ScipyOptimizer()
prob.driver.options['optimizer'] = 'COBYLA'#"Powell"#COBYLA, Powell works, COBYLA works, Nelder-Mead works but violates constraints, own PSO works, 
prob.driver.options['maxiter'] = 50

model.add_design_var('indep2.layout', lower=np.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]), upper=np.array([[1600.0, 1600.0], [1600.0, 1600.0], [1600.0, 1600.0]]), scaler=1.0/1600.0)
model.add_objective('analysis.lcoe')
model.add_constraint('constraint_distance.magnitude_violations', upper=0.01)
model.add_constraint('constraint_boundary.magnitude_violations', upper=0.00001)

prob.set_solver_print(level=5)
				
prob.setup()
prob.run_driver()

print(prob['indep2.layout'])
with open("layout_opt.dat", "w") as out:
	for t in prob['indep2.layout']:
		out.write("{} {}\n".format(t[0], t[1]))
print(prob['analysis.lcoe'])

print(prob['constraint_distance.n_constraint_violations'])
print(prob['constraint_boundary.n_constraint_violations'])
print(prob['constraint_boundary.magnitude_violations'])
