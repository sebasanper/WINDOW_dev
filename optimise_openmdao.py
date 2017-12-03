import numpy as np

from openmdao.api import Problem, ScipyOptimizer
# from openmdao.api import pyOptSparseDriver
from workflow_cheap import LCOE
from farm_description import NT

prob = Problem()
model = prob.model = LCOE()
# prob.driver = pyOptSparseDriver()
prob.driver = ScipyOptimizer()
prob.driver.options['optimizer'] = 'COBYLA'#'SLSQP'#"Powell"#COBYLA, Powell works, COBYLA works, Nelder-Mead works but violates constraints, own PSO works, 
# prob.driver.options['maxiter'] = 300

# model.add_design_var('indep2.layout', lower=np.array([[484000.0, 5.715e6] for _ in range(NT)]), upper=np.array([[504000.0, 5.74e6] for _ in range(NT)]))#, scaler=1.0/1600.0)
model.add_design_var("indep2.downwind_spacing", lower=570.0, upper=2500.0)
model.add_design_var("indep2.crosswind_spacing", lower=570.0, upper=2500.0)
model.add_design_var("indep2.odd_row_shift_spacing", lower=285.0, upper=570.0)
model.add_design_var("indep2.layout_angle", lower=0.0, upper=180.0)
model.add_objective('analysis.lcoe')
model.add_constraint('constraint_distance.magnitude_violations', upper=0.01)
model.add_constraint('constraint_boundary.magnitude_violations', upper=0.00001)

prob.set_solver_print(level=5)

prob.setup()
print(prob['indep2.layout'])
prob.run_model()
print(prob['analysis.lcoe'])
prob.run_driver()

print(prob['indep2.layout'])
with open("layout_opt_alpso.dat", "w") as out:
	for t in prob['indep2.layout']:
		out.write("{} {}\n".format(t[0], t[1]))
print(prob['analysis.lcoe'])

print(prob['constraint_distance.n_constraint_violations'])
print(prob['constraint_boundary.n_constraint_violations'])
print(prob['constraint_boundary.magnitude_violations'])
