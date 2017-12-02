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


class LCOE(Group):
    # def __init__(self):
    #     super(LCOE, self).__init__()

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output("layout", val=np.array([create_random() for _ in range(NT)]))
        # indep2.add_output("layout", val=np.array([[496739.226740417, 5730260.328529582], [496781.030471919, 5732330.091594553], [497006.8408240323, 5734115.1657679025], [500724.6195478625, 5725268.087117375], [498841.4026507029, 5723443.262008221], [496419.4299239046, 5733943.127034864], [493705.0156600609, 5729155.268562897], [498086.7306085363, 5735968.188244396], [490299.6251440735, 5732622.873202982], [491420.6072281312, 5726007.163289186], [500751.05190541677, 5724017.500070824], [500264.14125801425, 5718395.754169116], [497722.4686105763, 5730745.452368334], [497070.1611452929, 5727854.8336736765], [494240.8869819385, 5725383.908357059], [500997.42366974393, 5721871.2866823785], [489624.9352851828, 5731194.779303233], [499598.55816895526, 5720007.50197409], [492528.78288271994, 5729144.08816494], [493495.6337353149, 5724206.39636153], [489602.07776812743, 5732303.746274246], [500503.53668874834, 5720724.272780397], [486655.43450782954, 5731195.412921167], [502462.80070719344, 5728611.040350197], [493933.0722023798, 5730847.775735418], [495006.9473406908, 5727045.5073945], [493687.28346507857, 5732716.56451267], [491413.6796402806, 5730097.184699417], [490042.32258668396, 5732612.72878034], [489811.9350147435, 5732641.59564729], [486509.0376080911, 5732413.1241315985], [497974.69574037264, 5733414.756816601], [499494.1701445045, 5736688.4672860475], [491020.5050659521, 5730598.9131112555], [497867.2572118561, 5726049.798308862], [496835.51723630144, 5724959.163337865], [497156.6139907382, 5733878.752354547], [494434.2783652708, 5722930.103913396], [498827.9564414761, 5728203.225454168], [490639.68892236974, 5727677.983926128], [490561.3281975846, 5729229.936698631], [497628.4204690419, 5731022.418948743], [498411.27196596714, 5729444.372303993], [488017.34446998197, 5733588.390120024], [501034.5964453242, 5724765.213431093], [494217.882840404, 5725406.358804362], [499199.4365906718, 5719803.677474473], [493104.2229279706, 5735184.604085922], [485409.38344876, 5731843.2187254], [497221.9885666539, 5726533.394142444], [500328.3955609819, 5720099.821750345], [498023.6340049696, 5727775.298477015], [495849.2096629012, 5735081.5077843685], [491568.6090685805, 5733449.321564672], [491541.08990264573, 5730320.107091928], [492751.5065370166, 5732030.943929495], [490054.91150151286, 5730795.133149844], [493155.43608780875, 5727599.429375098], [490199.74389021314, 5730622.297283431], [486141.47275076853, 5731707.53043803], [501262.6812433458, 5724848.230993106], [496357.834951884, 5735859.974020689], [494261.5140364207, 5735666.927319213], [492620.74629729916, 5732985.813224885], [487175.5094155953, 5732034.284927241], [491144.73476664344, 5726857.713734061], [489146.55843556474, 5733787.250581298], [490966.9325239034, 5732872.657342179], [498527.7630729638, 5723341.417645146], [487302.7643002945, 5731247.674632416], [497300.6306593455, 5731651.765042642], [500456.1271169122, 5723081.488072584], [496963.41509165306, 5726512.633276903], [499651.04719221266, 5718968.322028079]]))
        indep2.add_output("areas", val=areas)
        indep2.add_output("radius", val=rotor_radius)
        self.add_subsystem('constraint_distance', MinDistance())
        self.add_subsystem('constraint_boundary', WithinBoundaries())
        self.add_subsystem("analysis", Dev())

        self.connect("indep2.layout", ["constraint_boundary.layout", "analysis.layout", "constraint_distance.orig_layout"])
        self.connect("indep2.radius", "constraint_distance.turbine_radius")
        self.connect("indep2.areas", "constraint_boundary.areas")

class Dev(ExplicitComponent):
    def setup(self):
        self.add_input("layout", shape=(NT, 2))
        self.add_output("lcoe", val=0.0)

        self.declare_partials(of="lcoe", wrt="layout", method="fd")

    def compute(self, inputs, outputs):
        layout = inputs["layout"]
        lcoe = analysis_cheap(layout, nbins=4, artif_angle=30.0, a=1, c=4, d=4, e=0, f=2, j=1)
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
    print(prob["indep2.layout"].tolist())
    print(prob["analysis.lcoe"])
    print(prob['constraint_distance.n_constraint_violations'])
    print(prob['constraint_boundary.n_constraint_violations'])
    print(prob['constraint_boundary.magnitude_violations'])

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