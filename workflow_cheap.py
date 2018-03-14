from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder, ExplicitComponent
import numpy as np
from time import time, clock
from constraints_openmdao import MinDistance, WithinBoundaries
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


class LCOE(Group):

   def setup(self):
      indep2 = self.add_subsystem('indep2', IndepVarComp())
      indep2.add_output("layout", val=np.array([create_random() for _ in range(NT)]))
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

      self.declare_partials(of="lcoe", wrt="layout", method="fd", fd_step=100.0, step_size=100.0, step=100.0)

   def compute(self, inputs, outputs):
      layout = inputs["layout"]
      lcoe = analysis_cheap(layout, nbins=4, artif_angle=10.0, a=1, c=4, d=4, e=0, f=2, j=1)
      outputs['lcoe'] = lcoe

if __name__ == '__main__':
    from joblib import Parallel, delayed
#     def print_nice(string, value):
#         header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
#         header += str(value) + "\n"
#         header += "=" * (22 + len(string))
#         print header
#     # print clock(), "Before defining problem"
    prob = Problem()
    prob.model = LCOE()
    prob.setup()

    # indep2.add_output("layout", val=np.array([[485389.30470373359, 5731725.2110892925], [486541.11849076685, 5731060.2110892925], [487396.11849076685, 5732541.1145297633], [487692.93227780017, 5730395.2110892925], [488547.93227780017, 5731876.1145297633], [489402.93227780017, 5733357.0179702351], [488844.74606483348, 5729730.2110892925], [489699.74606483348, 5731211.1145297633], [490554.74606483348, 5732692.0179702351], [491409.74606483348, 5734172.9214107059], [489996.5598518668, 5729065.2110892925], [490851.5598518668, 5730546.1145297633], [491706.5598518668, 5732027.0179702351], [492561.5598518668, 5733507.9214107059], [493416.5598518668, 5734988.8248511776], [490293.37363890011, 5726919.3076488208], [491148.37363890011, 5728400.2110892925], [492003.37363890011, 5729881.1145297633], [492858.37363890011, 5731362.0179702351], [493713.37363890011, 5732842.9214107059], [494568.37363890011, 5734323.8248511776], [495423.37363890011, 5735804.7282916494], [491445.18742593337, 5726254.3076488208], [492300.18742593337, 5727735.2110892925], [493155.18742593337, 5729216.1145297633], [494010.18742593337, 5730697.0179702351], [494865.18742593337, 5732177.9214107059], [495720.18742593337, 5733658.8248511776], [497430.18742593337, 5736620.6317321202], [492597.00121296669, 5725589.3076488208], [493452.00121296669, 5727070.2110892925], [494307.00121296669, 5728551.1145297633], [495162.00121296669, 5730032.0179702351], [496017.00121296669, 5731512.9214107059], [496872.00121296669, 5732993.8248511776], [497727.00121296669, 5734474.7282916494], [498582.00121296669, 5735955.6317321202], [493748.815, 5724924.3076488208], [494603.815, 5726405.2110892925], [495458.815, 5727886.1145297633], [496313.815, 5729367.0179702351], [497168.815, 5730847.9214107059], [494900.62878703332, 5724259.3076488208], [495755.62878703332, 5725740.2110892925], [496610.62878703332, 5727221.1145297633], [497465.62878703332, 5728702.0179702351], [498320.62878703332, 5730182.9214107059], [495197.44257406663, 5722113.4042083491], [496052.44257406663, 5723594.3076488208], [496907.44257406663, 5725075.2110892925], [497762.44257406663, 5726556.1145297633], [498617.44257406663, 5728037.0179702351], [499472.44257406663, 5729517.9214107059], [496349.25636109989, 5721448.4042083491], [497204.25636109989, 5722929.3076488208], [498059.25636109989, 5724410.2110892925], [498914.25636109989, 5725891.1145297633], [499769.25636109989, 5727372.0179702351], [500624.25636109989, 5728852.9214107059], [497501.07014813321, 5720783.4042083491], [498356.07014813321, 5722264.3076488208], [499211.07014813321, 5723745.2110892925], [500066.07014813321, 5725226.1145297633], [500921.07014813321, 5726707.0179702351], [501776.07014813321, 5728187.9214107059], [498652.88393516652, 5720118.4042083491], [499507.88393516652, 5721599.3076488208], [500362.88393516652, 5723080.2110892925], [501217.88393516652, 5724561.1145297633], [502072.88393516652, 5726042.0179702351], [499804.69772219984, 5719453.4042083491], [500659.69772219984, 5720934.3076488208], [501514.69772219984, 5722415.2110892925], [500956.51150923315, 5718788.4042083491]]))  # Baseline

    # prob['indep2.layout'] = np.array([[501342.44271928, 5718446.07183128], [501184.78531476, 5716566.40527058], [502935.21883139, 5727747.64692052], [501996.08466775, 5726058.31092907], [501838.42726322, 5724078.64436838], [500999.29309958, 5722389.30837693], [500841.63569506, 5720609.64181623], [500002.50153141, 5718820.30582478], [501495.27764352, 5728021.88091403], [500656.14347988, 5726332.54492258], [500498.48607535, 5724552.87836188], [499659.35191171, 5722763.54237043], [499501.69450719, 5720883.87580973], [498662.56034354, 5719194.53981828], [500312.99386017, 5730375.78146822], [500155.33645565, 5728396.11490753], [499316.20229201, 5726706.77891608], [499158.54488748, 5724827.11235538], [498319.41072384, 5723137.77636393], [498161.75331932, 5721258.10980323], [498973.0526723, 5730650.01546173], [498815.39526778, 5728870.34890103], [497976.26110414, 5727081.01290958], [497818.60369961, 5725201.34634888], [496979.46953597, 5723512.01035743], [496821.81213145, 5721632.34379673], [499469.03721624, 5736282.58799882], [498629.9030526, 5734593.25200737], [497633.11148443, 5731124.24945523], [497475.45407991, 5729244.58289453], [496636.31991627, 5727455.24690308], [496478.66251174, 5725575.58034238], [495639.5283481, 5723986.24435093], [495481.87094358, 5722006.57779024], [498129.09602837, 5736756.82199232], [497289.96186473, 5734967.48600088], [497132.30446021, 5733087.81944018], [496293.17029656, 5731398.48344873], [496135.51289204, 5729518.81688803], [495296.3787284, 5727829.48089658], [495138.72132387, 5726049.81433588], [494299.58716023, 5724260.47834444], [495950.02067686, 5735341.71999438], [495792.36327234, 5733462.05343368], [494953.22910869, 5731772.71744223], [494795.57170417, 5729893.05088153], [493956.43754053, 5728203.71489008], [493798.780136, 5726324.04832939], [492959.64597236, 5724634.71233794], [494610.07948899, 5735815.95398788], [494552.42208447, 5733936.28742718], [493713.28792082, 5732146.95143573], [493455.6305163, 5730267.28487503], [492616.49635265, 5728577.94888359], [492458.83894813, 5726698.28232289], [493112.4808966, 5734310.52142068], [492273.34673295, 5732521.18542923], [492115.68932843, 5730641.51886854], [491276.55516478, 5728952.18287709], [491118.89776026, 5727072.51631639], [491772.53970873, 5734584.75541418], [490933.40554508, 5732895.41942274], [490775.74814056, 5731115.75286204], [490036.61397691, 5729326.41687059], [489778.95657239, 5727446.75030989], [489593.46435721, 5733269.65341624], [489435.80695269, 5731389.98685554], [488596.67278904, 5729700.65086409], [488253.52316934, 5733643.88740974], [488095.86576482, 5731764.22084904], [487256.73160117, 5730074.88485759], [486755.92457695, 5732138.45484254], [485415.98338908, 5732512.68883604], [488802.90901096, 5730656.80245216]])

# [1212.3432058726044, 1857.2419373594398, 1196.7844285385258, areas, 131.4387661905908] result of Annealing = [ 6.65410628] LCOE

   # [ 963.76288446] [ 2418.24137673] [ 1033.51506808] [ 75.98448581] [ 6.59863725] LCOE REGULAR BEST
    # prob['indep2.downwind_spacing'] =  963.76288446#1330.0#, 1212.3432058726044
    # prob['indep2.crosswind_spacing'] = 2418.24137673#1710.0#1857.2419373594398
    # prob['indep2.odd_row_shift_spacing'] = 1033.51506808#600.0#1196.7844285385258
    # prob['indep2.layout_angle'] = 75.98448581#80.0#131.4387661905908

    # def read_layout(layout_file):
    #     layout_file = open(layout_file, 'r')
    #     layout = []
    #     i = 0
    #     for line in layout_file:
    #         columns = line.split()
    #         layout.append([float(columns[0]), float(columns[1])])
    #         i += 1
    def read_layout(layout_file):
        layout_file = open(layout_file, 'r')
        layout = []
        i = 0
        for line in layout_file:
            columns = line.split()
            layout.append([float(columns[0]), float(columns[1])])
            i += 1

        return np.array(layout)
    prob['indep2.layout'] = read_layout("optim_diff.dat")
    prob.run_model()
    print(prob["analysis.layout"].tolist())
    print(prob["analysis.lcoe"])
    print(prob['constraint_distance.n_constraint_violations'])
    print(prob['constraint_boundary.n_constraint_violations'])
    print(prob['constraint_boundary.magnitude_violations'])

    #     return np.array(layout)
    # prob['indep2.layout'] = read_layout('layout_opt_3.dat')

    def randomly(n):
        if n % 100 == 0:
            print n, "iteration"
        with open("random_irregular.dat", "a", 1) as out:
            prob["indep2.layout"] = [create_random() for _ in range(NT)]
            prob.run_model()
            out.write("{} {} {}\n\n".format(prob["indep2.layout"], prob["analysis.lcoe"], prob['constraint_distance.n_constraint_violations']))
            print(prob["analysis.lcoe"])

    Parallel(n_jobs=-2)(delayed(randomly)(i) for i in range(10000))
    # print(prob["analysis.layout"].tolist())
    # print(prob["analysis.lcoe"])
    # print(prob['constraint_distance.n_constraint_violations'])
    # print(prob['constraint_boundary.n_constraint_violations'])
    # print(prob['constraint_boundary.magnitude_violations'])

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