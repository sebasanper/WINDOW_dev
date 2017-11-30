from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder, ExplicitComponent
import numpy as np
from time import time, clock
from constraints_openmdao import MinDistance, WithinBoundaries
# from regular_parameterised import RegularLayout
from call_workflow_once import call_workflow_layout as analysis_cheap
from farm_description import areas

class LCOE(Group):
    # def __init__(self):
    #     super(LCOE, self).__init__()

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output("layout", val=np.array([[0.0, 0.0], [800.0, 0.0], [1600.0, 0.0],
                                                      [0.0, 800.0], [800.0, 800.0], [1600.0, 800.0],
                                                      [0.0, 1600.0], [800.0, 1600.0], [1600.0, 1600.0]]))
        indep2.add_output("areas", val=areas)
        indep2.add_output("radius", val=63.0)
        self.add_subsystem('constraint_distance', MinDistance())
        self.add_subsystem('constraint_boundary', WithinBoundaries())
        self.add_subsystem("analysis", Dev())

        self.connect("indep2.layout", ["constraint_boundary.layout", "analysis.layout", "constraint_distance.orig_layout"])
        self.connect("indep2.radius", "constraint_distance.turbine_radius")
        self.connect("indep2.areas", "constraint_boundary.areas")

class Dev(ExplicitComponent):
    def setup(self):
        self.add_input("layout", shape=(9,2))
        self.add_output("lcoe", val=0.0)

        self.declare_partials(of="lcoe", wrt="layout", method="fd")

    def compute(self, inputs, outputs):
        layout = inputs["layout"]
        lcoe = analysis_cheap(layout, nbins=4, artif_angle=30.0, a=1, c=4, d=1, e=0, f=3, j=1)
        outputs['lcoe'] = lcoe

if __name__ == '__main__':
#     def print_nice(string, value):
#         header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
#         header += str(value) + "\n"
#         header += "=" * (22 + len(string))
#         print header
#     # print clock(), "Before defining problem"
    prob = Problem()
#     # print clock(), "Before defining model"
    prob.model = LCOE()
#     # print clock(), "Before setup"
#     prob.model.approx_totals(of=['lcoe.LCOE'], wrt=['indep2.layout'], method='fd', step=1e-7, form='central', step_calc='rel')
    prob.setup()

#     # print clock(), "After setup"
    # view_model(prob) # Uncomment to view N2 chart.
#     start = time()


#     prob.setup()
    prob.run_model()
    print(prob["analysis.lcoe"])
    # prob.check_totals(of=['lcoe.LCOE'], wrt=['indep2.layout'])

    # of = ['lcoe.LCOE']
    # wrt = ['indep2.layout']
    # derivs = prob.compute_totals(of=of, wrt=wrt)

    # print(derivs['lcoe.LCOE', 'indep2.layout'])
    # # print clock(), "Before 1st run"
    # prob.run_model()
    # print clock(), "After 1st run"
    # print time() - start, "seconds", clock()


    # print prob['AeroAEP.wakemodel.p']
    # print prob['AeroAEP.wakemodel.combine.ct']
    # print prob['lcoe.LCOE']
    # with open('all_outputs.dat', 'w') as out:
    #     out.write("{}".format(prob.model.list_outputs(out_stream=None)))
    # print prob['AeroAEP.AEP']
    # print prob['Costs.investment_costs']
    # print prob['Costs.decommissioning_costs']
    # print prob['lcoe.LCOE']
    # print prob['OandM.availability']
    # print prob['OandM.annual_cost_O&M']

    # print prob['find_max_TI.max_TI']
    # print prob['support.cost_support']

    # print prob['electrical.topology']
    # print prob['electrical.cost_p_cable_type']
    # print prob['electrical.length_p_cable_type']

    # print prob['AEP.windrose.cases']
    # print prob['AEP.farmpower.ind_powers']
    # print prob['AEP.wakemodel.U']
    # print prob['AEP.wakemodel.linear_solve.deficits0.dU']
    # print prob['AEP.wakemodel.linear_solve.deficits1.dU']
    # print prob['AEP.wakemodel.linear_solve.deficits2.dU']
    # print prob['AEP.wakemodel.linear_solve.deficits3.dU']
    # print prob['AEP.wakemodel.linear_solve.deficits4.dU']
    # print prob['AEP.wakemodel.linear_solve.ct0.ct']
    # print prob['AEP.wakemodel.linear_solve.ct1.ct']
    # print prob['AEP.wakemodel.linear_solve.ct2.ct']
    # print prob['AEP.wakemodel.linear_solve.ct3.ct']
    # print prob['AEP.wakemodel.linear_solve.ct4.ct']
    # print prob['AEP.wakemodel.linear_solve.deficits1.distance.dist_down']
    # print prob['AEP.wakemodel.linear_solve.deficits1.distance.dist_cross']
    # ordered = prob['AEP.wakemodel.linear_solve.order_layout.ordered']
    # print ordered
    # print prob['indep2.layout']
    # # print [[prob['AEP.wakemodel.combine.U'][i] for i in [x[0] for x in ordered]] for item  in prob['AEP.wakemodel.combine.U']]

    # print "second run"
    # start = time()
    # print clock(), "Before 2nd run"
    # prob['indep2.wind_directions'] = 0.0
    # prob.run_model()
    # print clock(), "After 2nd run"
    # print time() - start, "seconds", clock()
    # print prob['lcoe.LCOE']


    # print "third run"
    # start = time()
    # print clock(), "Before 3rd run"
    # prob['indep2.wind_directions'] = 270.0
    # prob.run_model()
    # print clock(), "After 3rd run"
    # print time() - start, "seconds", clock()
    # print prob['lcoe.LCOE']


    # with open("angle_power.dat", "w") as out:
    #     for n in range(n_cases):
    #         out.write("{} {} {} {} {}\n".format(prob['AEP.open_cases.wind_directions'][n], prob['AEP.open_cases.freestream_wind_speeds'][n], prob['AEP.windrose.probabilities'][n], prob['AEP.farmpower.farm_power'][n], prob['AEP.energies'][n]))
    # print prob['AEP.AEP']
    # print sum(prob['AEP.windrose.probabilities'])