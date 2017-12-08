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
        indep2.add_output("areas", val=areas)
        indep2.add_output("radius", val=rotor_radius)
        indep2.add_output("downwind_spacing", val=1900.0)#1330.0)
        indep2.add_output("crosswind_spacing", val=1900.0)#.0)
        indep2.add_output("odd_row_shift_spacing", val=0.0)
        indep2.add_output("layout_angle", val=80.0)

        self.add_subsystem("regular_layout", RegularLayout())
        self.add_subsystem("analysis", Dev())

        self.connect("indep2.areas", "regular_layout.area")
        self.connect("indep2.downwind_spacing", "regular_layout.downwind_spacing")
        self.connect("indep2.crosswind_spacing", "regular_layout.crosswind_spacing")
        self.connect("indep2.odd_row_shift_spacing", "regular_layout.odd_row_shift_spacing")
        self.connect("indep2.layout_angle", "regular_layout.layout_angle")
        self.connect("regular_layout.regular_layout", "analysis.layout")

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
# [1212.3432058726044, 1857.2419373594398, 1196.7844285385258, areas, 131.4387661905908] result of Annealing = [ 6.65410628] LCOE

   # [ 963.76288446] [ 2418.24137673] [ 1033.51506808] [ 75.98448581] [ 6.59863725] LCOE REGULAR BEST

# 1391.22013673,  1852.79334031,   353.77828467, areas,   164.39541089
   # 969.34641881] [ 2428.05402564] [ 1033.85393252] [ 46.63310252
    prob['indep2.downwind_spacing'] =  1391.22013673#969.34641881#, 1212.3432058726044
    prob['indep2.crosswind_spacing'] = 1852.79334031#2428.05402564#1857.2419373594398
    prob['indep2.odd_row_shift_spacing'] = 353.77828467#1033.85393252#600.0#1196.7844285385258
    prob['indep2.layout_angle'] = 164.39541089#346.63310252#131.4387661905908

    prob.run_model()
    print(prob["analysis.layout"].tolist())
    print(prob["analysis.lcoe"])
