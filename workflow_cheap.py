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
    prob = Problem()
    prob.model = LCOE()
    prob.setup()

        # indep2.add_output("layout", val=np.array([[485389.30470373359, 5731725.2110892925], [486541.11849076685, 5731060.2110892925], [487396.11849076685, 5732541.1145297633], [487692.93227780017, 5730395.2110892925], [488547.93227780017, 5731876.1145297633], [489402.93227780017, 5733357.0179702351], [488844.74606483348, 5729730.2110892925], [489699.74606483348, 5731211.1145297633], [490554.74606483348, 5732692.0179702351], [491409.74606483348, 5734172.9214107059], [489996.5598518668, 5729065.2110892925], [490851.5598518668, 5730546.1145297633], [491706.5598518668, 5732027.0179702351], [492561.5598518668, 5733507.9214107059], [493416.5598518668, 5734988.8248511776], [490293.37363890011, 5726919.3076488208], [491148.37363890011, 5728400.2110892925], [492003.37363890011, 5729881.1145297633], [492858.37363890011, 5731362.0179702351], [493713.37363890011, 5732842.9214107059], [494568.37363890011, 5734323.8248511776], [495423.37363890011, 5735804.7282916494], [491445.18742593337, 5726254.3076488208], [492300.18742593337, 5727735.2110892925], [493155.18742593337, 5729216.1145297633], [494010.18742593337, 5730697.0179702351], [494865.18742593337, 5732177.9214107059], [495720.18742593337, 5733658.8248511776], [497430.18742593337, 5736620.6317321202], [492597.00121296669, 5725589.3076488208], [493452.00121296669, 5727070.2110892925], [494307.00121296669, 5728551.1145297633], [495162.00121296669, 5730032.0179702351], [496017.00121296669, 5731512.9214107059], [496872.00121296669, 5732993.8248511776], [497727.00121296669, 5734474.7282916494], [498582.00121296669, 5735955.6317321202], [493748.815, 5724924.3076488208], [494603.815, 5726405.2110892925], [495458.815, 5727886.1145297633], [496313.815, 5729367.0179702351], [497168.815, 5730847.9214107059], [494900.62878703332, 5724259.3076488208], [495755.62878703332, 5725740.2110892925], [496610.62878703332, 5727221.1145297633], [497465.62878703332, 5728702.0179702351], [498320.62878703332, 5730182.9214107059], [495197.44257406663, 5722113.4042083491], [496052.44257406663, 5723594.3076488208], [496907.44257406663, 5725075.2110892925], [497762.44257406663, 5726556.1145297633], [498617.44257406663, 5728037.0179702351], [499472.44257406663, 5729517.9214107059], [496349.25636109989, 5721448.4042083491], [497204.25636109989, 5722929.3076488208], [498059.25636109989, 5724410.2110892925], [498914.25636109989, 5725891.1145297633], [499769.25636109989, 5727372.0179702351], [500624.25636109989, 5728852.9214107059], [497501.07014813321, 5720783.4042083491], [498356.07014813321, 5722264.3076488208], [499211.07014813321, 5723745.2110892925], [500066.07014813321, 5725226.1145297633], [500921.07014813321, 5726707.0179702351], [501776.07014813321, 5728187.9214107059], [498652.88393516652, 5720118.4042083491], [499507.88393516652, 5721599.3076488208], [500362.88393516652, 5723080.2110892925], [501217.88393516652, 5724561.1145297633], [502072.88393516652, 5726042.0179702351], [499804.69772219984, 5719453.4042083491], [500659.69772219984, 5720934.3076488208], [501514.69772219984, 5722415.2110892925], [500956.51150923315, 5718788.4042083491]]))  # Baseline

    def read_layout(layout_file):
        layout_file = open(layout_file, 'r')
        layout = []
        i = 0
        for line in layout_file:
            columns = line.split()
            layout.append([float(columns[0]), float(columns[1])])
            i += 1

        return np.array(layout)

    prob.run_model()
    print(prob["analysis.layout"].tolist())
    print(prob["analysis.lcoe"])
    print(prob['constraint_distance.n_constraint_violations'])
    print(prob['constraint_boundary.n_constraint_violations'])
    print(prob['constraint_boundary.magnitude_violations'])
