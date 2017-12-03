from openmdao.api import Problem
from workflow_cheap import LCOE

prob = Problem()
model = prob.model = LCOE()

# model.add_design_var('indep2.layout', lower=np.array([[484000.0, 5.715e6] for _ in range(NT)]), upper=np.array([[504000.0, 5.74e6] for _ in range(NT)]))#, scaler=1.0/1600.0)

prob.set_solver_print(level=5)

prob.setup()
# print(prob['indep2.layout'])

with open("regular_borssele_test.dat", "r") as inp:
	with open("results_74s.dat", "w") as out:
		for line in inp:
			x = line.split()
			prob['indep2.downwind_spacing'] = x[0]
			prob['indep2.crosswind_spacing'] = x[1]
			prob['indep2.odd_row_shift_spacing'] = x[2]
			prob['indep2.layout_angle'] = x[3]

			prob.run_model()
			print(line, prob['analysis.lcoe'])
			out.write("{} {} {} {} {}\n".format(x[0], x[1], x[2], x[3], prob['analysis.lcoe'][0]))
