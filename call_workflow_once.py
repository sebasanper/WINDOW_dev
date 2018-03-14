from workflow import Workflow
from workflow_for_optimisation import Workflow as Workflow_for_opt
from aep_workflow import Workflow as aep_workflow
from joblib import Parallel, delayed

from site_conditions.wind_conditions.windrose import MeanWind, WeibullWindBins
from costs.investment_costs.BOS_cost.cable_cost.cable_cost_models import cable_optimiser, radial_cable, random_cable
from costs.investment_costs.BOS_cost.cable_cost.cable_efficiency import infield_efficiency
from costs.OM_costs.om_models import oandm
from costs.investment_costs.BOS_cost.support_cost.farm_support_cost import farm_support_cost
from finance.finance_models import LPC
from farm_energy.AEP.aep import aep_average
from costs.other_costs import other_costs
from costs.total_costs import total_costs
# from farm_energy.wake_model_mean_new.aero_power_ct_models.thrust_coefficient import ct_v80
from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, danish_recommendation, frandsen, \
    larsen_turbulence, Quarton
from site_conditions.terrain.terrain_models import Flat, Plane, Rough, Gaussian
from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen, LarsenEffects as Larsen, Ainslie1DEffects as Ainslie1D, Ainslie2DEffects as Ainslie2D, constantwake
from farm_energy.wake_model_mean_new.wake_overlap import root_sum_square, maximum, multiplied, summed
from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient, power2, thrust_coefficient2

from random import randint, choice
import numpy as np
from statistics import mode, stdev
from Hybrid import draw_cables

# a - 1
wakemodels = [constantwake, Jensen, Larsen, Ainslie1D, Ainslie2D]
# b - 2
windrosemodels = ["C:/Users/Sebastian/PycharmProjects/WINDOW_dev/site_conditions/wind_conditions/weibull_windrose_12identical.dat",
    "site_conditions/wind_conditions/weibull_windrose_12unique.dat"]#,
    # "site_conditions/wind_conditions/weibull_windrose_12sameWeibull.dat",
    # ]
# c - 3
turbmodels = ["ConstantTurbulence", frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton]
# d - 4
cablemodels = ["ConstantCable", cable_optimiser, radial_cable, random_cable, draw_cables]
# e - 5
mergingmodels = [root_sum_square, maximum, multiplied, summed]
# f - 6
thrustmodels = ["farm_energy/wake_model_mean_new/aero_power_ct_models/ConstantThrust.dat", "farm_energy/wake_model_mean_new/aero_power_ct_models/windsim_ct.dat", "farm_energy/wake_model_mean_new/aero_power_ct_models/NREL_5MW_C_T_new.txt", "farm_energy/wake_model_mean_new/aero_power_ct_models/FASTstatistics_ct.dat", "C:/Users/Sebastian/PycharmProjects/WINDOW_dev/ct_dtu10.dat"]
# g - 7
powermodels = ["farm_energy/wake_model_mean_new/aero_power_ct_models/ConstantPower.dat", "farm_energy/wake_model_mean_new/aero_power_ct_models/windsim_power.dat", "farm_energy/wake_model_mean_new/aero_power_ct_models/nrel_cp.dat", "farm_energy/wake_model_mean_new/aero_power_ct_models/FASTstatistics_power.dat", "C:/Users/Sebastian/PycharmProjects/WINDOW_dev/power_dtu10.dat"]#, "farm_energy/wake_model_mean_new/aero_power_ct_models/powercurve.dat"]
# h - 8
depthmodels = [Flat, Gaussian, Plane, Rough]
# i - 9
weibullmodels = [MeanWind, WeibullWindBins]
# j - 10
farm_support_cost_models = ["ConstantSupport", farm_support_cost]

def call_aep(power_curve_file, ct_curve_file, windrose_file, layout, nbins, artif_angle, a, c, d, e, f, j):
    # print("called")
    real_angle = 30.0
    h = 3  # Fixed
    i = 1  # Fixed
    new_layout = []
    for item in layout:
        # print item
        if item[0] != -115110.0:
            new_layout.append(item)
    # print new_layout
    workflow1 = aep_workflow(weibullmodels[i], windrose_file, turbmodels[c], thrust_coefficient, ct_curve_file, wakemodels[a], mergingmodels[e], power, power_curve_file)

    workflow1.windrose.nbins = nbins
    workflow1.windrose.artificial_angle = artif_angle
    workflow1.windrose.real_angle = real_angle
    workflow1.print_output = False
    workflow1.draw_infield = False
    answer = workflow1.run(new_layout)
    power2.reset()
    thrust_coefficient2.reset()
    # print layout
    # print workflow1.turbulence, "turbulences"
    return answer


def call_workflow_layout(layout, nbins, artif_angle, a, c, d, e, f, j):
    # print("called")
    real_angle = 30.0
    b = 0  # Fixed
    g = f  # Turbine model
    h = 3  # Fixed
    i = 1  # Fixed
    new_layout = []
    for item in layout:
        # print item
        if item[0] != 0.0:
            new_layout.append(item)
    # print new_layout
    workflow1 = Workflow_for_opt(weibullmodels[i], windrosemodels[b], turbmodels[c], None, depthmodels[h], farm_support_cost_models[j], None, oandm, cablemodels[d], infield_efficiency, thrust_coefficient, thrustmodels[f], wakemodels[a], mergingmodels[e], power, powermodels[g], aep_average, other_costs, total_costs, LPC)

    workflow1.windrose.nbins = nbins
    workflow1.windrose.artificial_angle = artif_angle
    workflow1.windrose.real_angle = real_angle
    workflow1.print_output = True
    workflow1.draw_infield = False
    answer = workflow1.run(new_layout)
    power2.reset()
    thrust_coefficient2.reset()
    # print layout
    print workflow1.finance, "LCOE"
    return answer


def call_workflow_once(nbins, artif_angle, a, c, d, e, f, j):
    # print("called")
    real_angle = 30.0
    b = 0  # Fixed
    g = f  # Turbine model
    h = 3  # Fixed
    i = 1  # Fixed

    workflow1 = Workflow(weibullmodels[i], windrosemodels[b], turbmodels[c], None, depthmodels[h], farm_support_cost_models[j], None, oandm, cablemodels[d], infield_efficiency, thrust_coefficient, thrustmodels[f], wakemodels[a], mergingmodels[e], power, powermodels[g], aep_average, other_costs, total_costs, LPC)
    layout_input_file = "coords3x3.dat"
    # layout_input_file = "horns_rev_5MW_layout.dat"
    # nbins = randint(2, 25)
    # real_angle = choice([30.0, 60.0, 90.0, 120.0, 180.0])
    # artif_angle = 400.0

    workflow1.windrose.nbins = nbins
    workflow1.windrose.artificial_angle = artif_angle
    workflow1.windrose.real_angle = real_angle
    # workflow1.print_output = True
    workflow1.run(layout_input_file)
    power2.reset()
    thrust_coefficient2.reset()
    return workflow1.finance, workflow1.runtime, workflow1.power_calls, workflow1.thrust_calls


def reject_outliers(data, m=5.189):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.0
    try:
        good = data[s<m]
    except IndexError:
        good = data
    return good


def results_median_workflow(nbins, artif_angle, a, c, d, e, f, j):
    print("called")
    aeps = []
    finances = []
    runtimes = []
    n_power_calls = []
    n_thrust_calls = []

    for _ in range(5):
        results = call_workflow_once(nbins, artif_angle, a, c, d, e, f, j)
        time = results[1]
        power_calls = results[2]
        if f == 3:  # Time for FAST
            time += power_calls * 120.0
        elif f == 1:  # Time for WindSim
            time += power_calls * 0.032
        elif f == 2:  # Time for WT_Perf
            time += power_calls * 1.712
        else:  # Time for powercurve or constant.
            pass
        finances.append(results[0])
        runtimes.append(time)
        # print (time, power_calls)
        n_power_calls.append(power_calls)
        n_thrust_calls.append(results[3])
    stddev_finance = stdev(finances)
    runtimes = reject_outliers(np.array(runtimes))
    stddev_time = stdev(runtimes)

    # lcoe = []
    # sens = 1.0
    # layout = [[0.0, 0.0], [882.0, 0.0], [1764.0, 0.0], [0.0, 882.0], [882.0, 882.0], [1764.0, 882.0], [0.0, 1764.0], [882.0, 1764.0], [1764.0, 1764.0]]
    # lcoe.append(call_workflow_layout(layout, nbins, artif_angle, a, c, d, e, f, j))
    # for i in range(1, 11):
    #     layout = [[0.0, 0.0], [882.0, 0.0], [1764.0, 0.0], [0.0, 882.0], [882.0, 882.0], [1764.0, 882.0], [0.0, 1764.0], [882.0, 1764.0], [1764.0, 1764.0]]
    #     layout[4][0] += 1.0 / float(i)
    #     layout[4][1] += 1.0 / float(i)        
    #     lcoe.append(call_workflow_layout(layout, nbins, artif_angle, a, c, d, e, f, j))
    # for i in range(1, len(lcoe)):
    #     if abs(lcoe[i] - lcoe[0]) <= 0.0001:
    #         sens = 1.0 / float(i)
    #         break
    # with open("mopsoc_sampling.dat", "a") as out:
    #     out.write("{} {} {} {} {} {} {} {} {} {} {}\n".format(nbins, artif_angle, a, c, d, e, f, j, np.mean(finances), stddev_finance, np.mean(runtimes)))

    return np.mean(finances), stddev_finance, np.mean(runtimes), stddev_time, mode(n_power_calls), mode(n_thrust_calls)#, sens

def main():
    Parallel(n_jobs=-2)(delayed(results_median_workflow)(choice(list(range(11))) + 2, [1.0, 5.0, 15.0, 30.0][choice(list(range(4)))], choice(list(range(4))), choice(list(range(6))), choice(list(range(4))),
                       choice(list(range(4))), choice(list(range(4))), choice(list(range(2)))) for _ in range(5))

if __name__ == '__main__':

    from time import time
    from joblib import Parallel, delayed
    # start = time()
    layout = [[0.0, 0.0], [882.0, 0.0], [1764.0, 0.0], [0.0, 882.0], [882.0, 882.0], [1764.0, 882.0], [0.0, 1764.0], [882.0, 1764.0], [1764.0, 1764.0]]
    a=1
    c=2
    d=0
    e=0
    f=4
    j=0
    print layout
    print(call_aep(layout, 15, 30.0, a, c, d, e, f, j), "AEP")
    # print(results_median_workflow(15, 30.0, a, c, d, e, f, j))
    # print(time() - start, "seconds")
    # print(call_workflow_once(4, 30.0, 1, 4 ,1, 0, 3 ,1))

    # [list(range(23)), list(range(6)), list(range(4)), list(range(6)), list(range(4)),
    #                        list(range(4)), list(range(4)), list(range(2))]
    # main()
