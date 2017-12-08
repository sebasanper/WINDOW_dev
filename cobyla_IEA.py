from scipy.optimize import minimize
from openmdao.api import Problem, Group, IndepVarComp
from workflow_cheap import LCOE
from workflow_cheap_regular import LCOE as LCOE_reg
from constraints_openmdao import MinDistance, WithinBoundaries
from farm_description import n_quadrilaterals, areas, separation_equation_y, NT
from turbine_description import rotor_radius
from random import uniform
from transform_quadrilateral import AreaMapping
import numpy as np

def regular():

    prob = Problem()
    prob.model = LCOE_reg()
    prob.setup()

    def obj(x):
        print x
        prob['indep2.downwind_spacing'] = x[0]
        prob['indep2.crosswind_spacing'] = x[1]
        prob['indep2.odd_row_shift_spacing'] = x[2]
        prob['indep2.layout_angle'] = x[3]
        prob.run_model()
        ans = prob['analysis.lcoe'][0]
        return ans

    x1 = [uniform(800.0, 2500.0), uniform(800.0, 2500.0), uniform(0.0, 2500.0), uniform(0.0, 180.0)]

    opts = {'disp':False, 'maxiter':10000, 'rhobeg':50.0}

    a = minimize(obj, x0=x1, method='COBYLA', options=opts)

    print a

def irregular():

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
        print x
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
    # for _ in range(NT):
    #     x1 += create_random()

    last = create_random()

    x1 = [501342.4427192838, 5718446.0718312785, 501184.78531476273, 5716566.405270582, 502835.21883139096, 5727647.646920523, 501996.0846677459, 5725958.310929074, 501838.42726322485, 5724078.644368377, 500999.29309957975, 5722389.308376927, 500841.63569505874, 5720509.6418162305, 500002.50153141364, 5718820.305824781, 501495.27764352085, 5728021.880914025, 500656.14347987575, 5726332.544922575, 500498.4860753547, 5724452.878361878, 499659.35191170964, 5722763.542370428, 499501.6945071886, 5720883.875809732, 498662.56034354353, 5719194.539818282, 500312.99386017176, 5730275.781468224, 500155.3364556507, 5728396.114907526, 499316.20229200565, 5726706.778916077, 499158.5448874846, 5724827.11235538, 498319.4107238395, 5723137.776363931, 498161.75331931846, 5721258.109803233, 498973.0526723016, 5730650.015461725, 498815.3952677805, 5728770.348901028, 497976.2611041355, 5727081.012909578, 497818.6036996144, 5725201.346348882, 496979.4695359694, 5723512.010357432, 496821.8121314483, 5721632.343796735, 499469.03721624264, 5736282.587998822, 498629.9030525976, 5734593.252007374, 497633.1114844315, 5731024.249455227, 497475.4540799104, 5729144.582894529, 496636.3199162654, 5727455.2469030805, 496478.6625117443, 5725575.580342383, 495639.5283480992, 5723886.2443509335, 495481.8709435782, 5722006.577790237, 498129.0960283725, 5736656.821992325, 497289.96186472743, 5734967.486000875, 497132.3044602064, 5733087.819440178, 496293.1702965613, 5731398.483448728, 496135.51289204025, 5729518.816888032, 495296.3787283952, 5727829.480896582, 495138.72132387414, 5725949.8143358845, 494299.5871602291, 5724260.478344436, 495950.0206768573, 5735341.719994376, 495792.36327233625, 5733462.053433679, 494953.2291086912, 5731772.71744223, 494795.57170417014, 5729893.050881533, 493956.4375405251, 5728203.714890083, 493798.78013600403, 5726324.048329387, 492959.64597235894, 5724634.712337937, 494610.07948898716, 5735715.953987878, 494452.42208446615, 5733836.287427181, 493613.28792082105, 5732146.951435732, 493455.6305163, 5730267.284875034, 492616.49635265494, 5728577.948883586, 492458.83894813387, 5726698.282322888, 493112.480896596, 5734210.521420683, 492273.34673295094, 5732521.185429233, 492115.6893284299, 5730641.518868537, 491276.55516478483, 5728952.182877087, 491118.89776026376, 5727072.51631639, 491772.5397087259, 5734584.755414184, 490933.4055450808, 5732895.419422735, 490775.74814055976, 5731015.752862038, 489936.61397691467, 5729326.416870588, 489778.9565723936, 5727446.750309892, 489593.4643572107, 5733269.653416237, 489435.8069526896, 5731389.9868555395, 488596.67278904456, 5729700.65086409, 488253.5231693405, 5733643.887409738, 488095.86576481943, 5731764.220849042, 487256.7316011744, 5730074.884857592, 486755.9245769493, 5732138.454842543, 485415.9833890792, 5732512.688836045, last[0], last[1]]

    opts = {'disp':False, 'maxiter':10000, 'rhobeg':100.0}

    a = minimize(obj, x0=x1, method='COBYLA', options=opts, constraints=const)

    print a


if __name__ == '__main__':
    regular()
    # irregular()
