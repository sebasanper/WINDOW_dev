class Workflow:
    def __init__(self, inflow_model, windrose_file, wake_turbulence_model, aeroloads_model, depth_model, support_design_model,
                 hydroloads_model, OandM_model, cable_costs_model, cable_efficiency_model, thrust_coefficient_model, thrust_lookup_file, wake_mean_model, wake_merging_model, power_model, power_lookup_file, aep_model, more_costs, total_costs_model,
                 finance_model):

        self.print_output = False
        self.draw_infield = False

        self.inflow_model = inflow_model
        self.wake_turbulence_model = wake_turbulence_model
        self.aeroloads_model = aeroloads_model
        self.depth_model = depth_model
        self.support_design_model = support_design_model
        self.hydroloads_model = hydroloads_model
        self.OandM_model = OandM_model
        self.cable_topology_model = cable_costs_model
        self.cable_efficiency_model = cable_efficiency_model
        self.thrust_coefficient_model = thrust_coefficient_model
        self.wake_mean_model = wake_mean_model
        self.wake_merging_model = wake_merging_model
        self.power_model = power_model
        self.aep_model = aep_model
        self.total_costs_model = total_costs_model
        self.finance_model = finance_model
        self.more_costs = more_costs
        self.windrose = self.inflow_model(windrose_file)
        self.thrust_lookup_file = thrust_lookup_file
        self.power_lookup_file = power_lookup_file

    # @profile
    def connect(self, turbine_coordinates):
        self.number_turbines = len(turbine_coordinates)
        # print turbine_coordinates
        self.minx = min([turbine[1] for turbine in turbine_coordinates])
        self.maxx = max([turbine[1] for turbine in turbine_coordinates])
        self.miny = min([turbine[2] for turbine in turbine_coordinates])
        self.maxy = max([turbine[2] for turbine in turbine_coordinates])
        from site_conditions.terrain.terrain_models import depth
        from farm_energy.wake_model_mean_new.wake_1angle import energy_one_angle
        from farm_energy.wake_model_mean_new.wake_1angle_turbulence import max_turbulence_one_angle
        from costs.investment_costs.BOS_cost.cable_cost.Hybrid import draw_cables
        from farm_description import central_platform, read_cablelist, number_turbines_per_cable
        from turbine_description import rated_current
        from site_conditions.wind_conditions.windrose import WeibullWindBins, MeanWind
        from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen

        from turbine_description import cutin_wind_speed, cutout_wind_speed

        if self.print_output is True: print ("=== PREPARING WIND CONDITIONS ===")

        self.wind_directions, self.direction_probabilities = self.windrose.adapt_directions()

        if self.inflow_model == MeanWind:

            self.wind_speeds = self.windrose.expected_wind_speeds
            self.freestream_turbulence = [0.11]
            self.wind_speeds_probabilities = [[100.0] for _ in range(len(self.wind_directions))]

        elif self.inflow_model == WeibullWindBins:
            self.windrose.cutin = cutin_wind_speed
            self.windrose.cutout = cutout_wind_speed
            self.wind_speeds, self.wind_speeds_probabilities = self.windrose.speed_probabilities()
            self.freestream_turbulence = [0.11 for _ in range(len(self.wind_speeds[0]))]

        # if self.print_output is True: print self.wind_speeds, self.wind_speeds_probabilities

        self.energies_per_angle = []
        self.turbulences_per_angle = []
        self.cable_efficiencies_per_angle = []
        self.array_efficiencies = []
        # if self.print_output is True: print [sum(self.wind_speeds_probabilities[i]) for i in range(len(self.wind_speeds_probabilities))]

        self.max_turbulence_per_turbine = [0.0 for _ in range(len(turbine_coordinates))]

        if self.print_output is True: print( "=== CALCULATING ENERGY, TURBULENCE PER WIND DIRECTION ===")
        print self.wind_speeds
        for i in range(len(self.wind_directions)):
            # print " === Wind direction = " + str(self.wind_directions[i])
            # if self.print_output is True: print self.wind_speeds_probabilities[i]
            self.aero_energy_one_angle, self.powers_one_angle = energy_one_angle(turbine_coordinates, self.wind_speeds[i], self.wind_speeds_probabilities[i], self.wind_directions[i], self.freestream_turbulence, self.wake_mean_model, self.power_model, self.power_lookup_file, self.thrust_coefficient_model, self.thrust_lookup_file, self.wake_merging_model)
            # print( sum(self.powers_one_angle), self.wind_directions[i])
            # if self.print_output is True: print self.aero_energy_one_angle
            # if self.print_output is True: print self.powers_one_angle, max(self.powers_one_angle)
            # if self.print_output is True: print turbine_coordinates, self.wind_speeds[i], self.wind_directions[i], self.freestream_turbulence[0], Jensen, self.thrust_coefficient_model, self.wake_turbulence_model
            if self.wake_turbulence_model != "ConstantTurbulence":
                self.turbulences = max_turbulence_one_angle(turbine_coordinates, self.wind_speeds[i], self.wind_directions[i], self.freestream_turbulence, Jensen, self.thrust_coefficient_model, self.thrust_lookup_file, self.wake_turbulence_model)

            self.energy_one_angle_weighted = self.aero_energy_one_angle * self.direction_probabilities[i] / 100.0
            self.array_efficiency = (self.aero_energy_one_angle / (float(len(turbine_coordinates)) * max(self.powers_one_angle) * 8760.0))
            self.array_efficiencies_weighted = self.array_efficiency * self.direction_probabilities[i] / 100.0

            self.array_efficiencies.append(self.array_efficiencies_weighted)
            self.energies_per_angle.append(self.energy_one_angle_weighted)
            if self.wake_turbulence_model != "ConstantTurbulence":
                self.turbulences_per_angle.append(self.turbulences)
            if self.cable_topology_model != "ConstantCable":
                self.cable_efficiencies_per_angle.append(self.cable_topology_efficiency)

            if self.wake_turbulence_model != "ConstantTurbulence":
                for j in range(len(turbine_coordinates)):
                    if self.turbulences[j] > self.max_turbulence_per_turbine[j]:
                        self.max_turbulence_per_turbine[j] = self.turbulences[j]

        # if self.print_output is True: print self.array_efficiencies
        if self.print_output is True: print( " --- Array efficiency---")
        self.array_efficiency = sum(self.array_efficiencies)
        if self.print_output is True: print (str(self.array_efficiency * 100.0) + " %\n")
        print self.energies_per_angle
        if self.print_output is True: print (" --- Farm annual energy without losses---")
        self.farm_annual_energy = sum(self.energies_per_angle)
        if self.print_output is True: print( str(self.farm_annual_energy / 1000000.0) + " MWh\n")

        if self.print_output is True: print (" --- Maximum wind turbulence intensity ---")
        if self.wake_turbulence_model != "ConstantTurbulence":
            self.turbulence = self.max_turbulence_per_turbine
        elif self.wake_turbulence_model == "ConstantTurbulence":
            self.turbulence = [0.25 for _ in range(self.number_turbines)]
        if self.print_output is True: print (str([self.turbulence[l] * 100.0 for l in range(len(self.turbulence))]) + " %\n")

        print self.farm_annual_energy
        return self.farm_annual_energy, self.turbulence

    def run(self, layout_coordinates):

        from time import time
        from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power2, thrust_coefficient2, power, thrust_coefficient
        from farm_energy.wake_model_mean_new.ainslie1d import ainslie
        from farm_energy.wake_model_mean_new.ainslie2d import ainslie_full
        from farm_energy.wake_model_mean_new.jensen import determine_if_in_wake, wake_radius, wake_deficit
        from farm_energy.wake_model_mean_new.larsen import deff, wake_deficit_larsen, wake_radius, x0, rnb, r95, c1, determine_if_in_wake_larsen, wake_speed
        from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, Quarton, danish_recommendation, frandsen, larsen_turbulence
        self.coordinates = [[i, layout_coordinates[i][0], layout_coordinates[i][1]] for i in range(len(layout_coordinates))]
        start_time = time()
        answer = self.connect(self.coordinates)
        self.runtime = time() - start_time
        self.power_calls = power2.count()
        self.thrust_calls = thrust_coefficient2.count()
        power.reset()
        thrust_coefficient.reset()
        power2.reset()
        thrust_coefficient2.reset()
        # ainslie.reset()
        # ainslie_full.reset()
        determine_if_in_wake.reset()
        wake_radius.reset()
        wake_deficit.reset()
        frandsen2.reset()
        Quarton.reset()
        danish_recommendation.reset()
        larsen_turbulence.reset()
        frandsen.reset()
        return answer
