# -----------------------------------------Input Parameters------------------------------------------------------------------
from math import hypot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from copy import deepcopy
from heapq import heappush, heappop, heapify
import matplotlib.ticker as ticker
from time import time

'Remove and return the lowest priority task. Raise KeyError if empty.'
REMOVED = '<removed-task>'  # placeholder for a removed task

fontsize = 20
fontsize2 = 5
Euro = "eur"
MEuro = "M%s" % Euro


def draw_cables(WT_List, central_platform_locations, Cable_List):
    print "cable"
    Crossing_penalty = 0.0
    NT = len(WT_List)
    Area = []
    Transmission = [[[498000.0, 5731000.0], [498000.0, 5731000.0]]]# [463000.0, 5918000.0]]]
    name = 'sebastian'
    # ---------------------------------------Main--------------------------

    def set_cable_topology(WT_List, central_platform_locations, Cable_List):
        Wind_turbines = []
        for WT in WT_List:
            Wind_turbines.append([WT[0] + 1, WT[1], WT[2]])
        # initialize the parameters
        Wind_turbinesi, Costi, Cost0i, Costij, Savingsi, Savingsi_finder, Savingsi2, Savingsi2_finder, distancefromsubstationi, substationi, Routingi, Routing_redi, Routing_greeni, Routesi, Capacityi, Cable_Costi, Crossings_finder = dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict()
        i = 1
        for substation in central_platform_locations:
            Wind_turbinesi[i], Costi[i], distancefromsubstationi[i] = initial_values(NT, Wind_turbines, substation)
            substationi[i] = substation
            i = i + 1
        # splits the Wind_turbines list in the closest substation

        def second(x):
            return x[2]

        for j in xrange(NT):
            empty = []
            for key, value in distancefromsubstationi.iteritems():
                empty.append(value[j])
            index = empty.index(min(empty, key=second)) + 1
            Wind_turbinesi[index].append([value[j][1], Wind_turbines[j][1], Wind_turbines[j][2]])
        #        Wind_turbinesi[1]=[x for x in Wind_turbines if x[0]<=118]
        #        Wind_turbinesi[2]=[x for x in Wind_turbines if x[0]>118]
        for j in xrange(len(Cable_List)):
            Capacityi[j + 1] = Cable_List[j][0]
            Cable_Costi[j + 1] = Cable_List[j][1]
        # initialize routes and Saving matrix
        for key, value in Wind_turbinesi.iteritems():
            Routesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = initial_routes(value)
            Cost0i[key], Costij[key] = costi(value, substationi[key])
            Savingsi[key], Savingsi_finder[key], Crossings_finder[key] = savingsi(Cost0i[key], Costij[key], value,
                                                                                  Cable_Costi[1], substationi[key], Area,
                                                                                  Crossing_penalty)
        fig = plt.figure()
        for area in Area:
            plt.plot([area[0][0], area[1][0]], [area[0][1], area[1][1]], color='k', ls='--', linewidth='2')
        for trans in Transmission:
            plt.plot([trans[0][0], trans[1][0]], [trans[0][1], trans[1][1]], color='yellow', linewidth='4')
        cable_length = 0
        total_cost = 0
        crossings = 0
        for key, value in Wind_turbinesi.iteritems():
            Routesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = Hybrid(Savingsi[key],
                                                                                         Savingsi_finder[key],
                                                                                         Wind_turbinesi[key], Routesi[key],
                                                                                         Routingi[key], substationi[key],
                                                                                         Capacityi, Routing_redi[key],
                                                                                         Routing_greeni[key], Costi[key],
                                                                                         Cable_Costi)
            Savingsi2[key], Savingsi2_finder[key], Crossings_finder[key] = savingsi(Cost0i[key], Costij[key], value,
                                                                                    Cable_Costi[1], substationi[key], Area,
                                                                                    Crossing_penalty)
            Routesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = Esau_Williams_Cable_Choice(Savingsi2[key],
                                                                                                             Savingsi2_finder[
                                                                                                                 key],
                                                                                                             Crossings_finder[
                                                                                                                 key],
                                                                                                             Wind_turbinesi[
                                                                                                                 key],
                                                                                                             Routesi[key],
                                                                                                             Routingi[key],
                                                                                                             substationi[
                                                                                                                 key],
                                                                                                             Capacityi,
                                                                                                             Routing_redi[
                                                                                                                 key],
                                                                                                             Routing_greeni[
                                                                                                                 key],
                                                                                                             Costi[key],
                                                                                                             Cable_Costi)
            Routesi[key], Routingi[key] = RouteOpt_Hybrid(Routingi[key], Routing_redi[key], Routing_greeni[key],
                                                          substationi[key], Costi[key], Capacityi, Routesi[key],
                                                          Wind_turbinesi[key])
            length, cost, ax = plotting(fig, substationi[key], Wind_turbinesi[key], Routingi[key], Routing_redi[key],
                                        Routing_greeni[key], Capacityi, Cable_Costi)
            cable_length += length
            total_cost += cost
            for route in Routingi[key]:
                if edge_crossings_area([route[0], route[1]], Wind_turbinesi[key], substationi[key], Area)[0] is True:
                    crossings += edge_crossings_area([route[0], route[1]], Wind_turbinesi[key], substationi[key], Area)[1]
        print cable_length
        # print Routesi[1]
        # print Routesi
        # print('Cable length = {0} km'.format(round(cable_length / 1000, 3)))
        # print 'Cable cost = {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro)
        # if Area is not []:
        #     print 'Crossings = {0}'.format(crossings)
        # print 'Elapsed time = {0:.3f} s'.format(time() - start)

            ######Legend######

        # if len(Cable_Costi) == 1:
        #     label1 = mpatches.Patch(color='blue', label='Capacity: {0}'.format(Capacityi[1], round(cable_length / 1000, 3),
        #                                                                        int(total_cost), name))
        #     legend = plt.legend([label1], ["Capacity: {0}".format(Capacityi[1])], loc='upper right', numpoints=1,
        #                         fontsize=fontsize2, fancybox=True, shadow=True, ncol=2,
        #                         title='Cable Cost: {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro))
        # elif len(Cable_Costi) == 2:
        #     label1 = mpatches.Patch(color='blue', label='Capacity: {0}'.format(Capacityi[1], round(cable_length / 1000, 3),
        #                                                                        int(total_cost), name))
        #     label2 = mpatches.Patch(color='red', label='Capacity: {1}'.format(Capacityi[2], round(cable_length / 1000, 3),
        #                                                                       int(total_cost), name))
        #     legend = plt.legend([label1, (label2)],
        #                         ["Capacity: {0}".format(Capacityi[1]), "Capacity: {0}".format(Capacityi[2])],
        #                         loc='upper right', numpoints=1, fontsize=fontsize2, fancybox=True, shadow=True, ncol=2,
        #                         title='Cable Cost: {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro))
        # elif len(Cable_Costi) == 3:
        #     label1 = mpatches.Patch(color='blue', label='Capacity: {0}'.format(Capacityi[1], round(cable_length / 1000, 3),
        #                                                                        int(total_cost), name))
        #     label2 = mpatches.Patch(color='red', label='Capacity: {1}'.format(Capacityi[2], round(cable_length / 1000, 3),
        #                                                                       int(total_cost), name))
        #     label3 = mpatches.Patch(color='green', label='Capacity: {2}'.format(Capacityi[3], round(cable_length / 1000, 3),
        #                                                                         int(total_cost), name))
        #     legend = plt.legend([label1, label2, label3],
        #                         ["Capacity: {0}".format(Capacityi[1]), "Capacity: {0}".format(Capacityi[2]),
        #                          "Capacity: {0}".format(Capacityi[3])], loc='upper right', numpoints=1, fontsize=fontsize2,
        #                         fancybox=True, shadow=True, ncol=3,
        #                         title='Cable Cost: {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro))
        # plt.setp(legend.get_title(), fontsize=fontsize2)
        plt.tight_layout()
        plt.subplots_adjust(left=0.06, right=0.94, bottom=0.08)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.title(' {0} OWF - Hybrid '.format(name), fontsize=fontsize2)
        plt.grid()
        scale = 1000
        def plotaxis(x, pos):
            return '{0:g}'.format(x / scale)
        ticks1 = ticker.FuncFormatter(plotaxis)
        ax.xaxis.set_major_formatter(ticks1)
        ticks2 = ticker.FuncFormatter(plotaxis)
        ax.yaxis.set_major_formatter(ticks2)
        plt.xticks(fontsize=fontsize2)
        plt.yticks(fontsize=fontsize2)
        plt.axis([min(min([coord[1] for coord in WT_List]), central_platform_locations[0][0]) - 500.0, max(max([coord[1] for coord in WT_List]), central_platform_locations[0][0]) + 500.0, min(min([coord[2] for coord in WT_List]), central_platform_locations[0][1]) - 500.0, max(max([coord[2] for coord in WT_List]), central_platform_locations[0][1]) + 500.0])
        # ax.autoscale(False, tight=False)
        for j, txt in enumerate(range(1, NT + 1)):
            ax.annotate(txt, ([item[1]+10 for item in WT_List][j], [item[2]+10 for item in WT_List][j]))
        plt.savefig("topology.eps", format="eps", dpi=1000)

    def mainroutine(arc, lines, Routes, Routing):
        if [arc[0], 0] in Routing:
            index1 = Routing.index([arc[0], 0])
        else:
            for line in lines:
                if arc[0] in line:
                    index1 = Routing.index([line[0], 0])
        Routing.pop(index1)
        Routing.append([arc[0], arc[1]])
        # turbines to be reversed
        for line in lines:
            if arc[0] in line:
                indexline = lines.index(line)
                indexarc = line.index(arc[0])
        indeces = []
        for i in xrange(0, indexarc):
            turbine = lines[indexline][i]
            for route in Routing:
                if route[1] == turbine and route != [arc[0], arc[1]]:
                    indexroute = Routing.index(route)
                    indeces.append(indexroute)
        for index in indeces:
            Routing[index].reverse()
        Routes = []
        for route in Routing:
            if route[1] == 0:
                Routes.append([[route[1], route[0]]])
        helpRouting = [i for i in Routing if i[1] != 0]
        helpRouting.reverse()
        for path in Routes:
            for pair in path:
                for route in helpRouting:
                    if pair[1] == route[1]:
                        index2 = path.index(pair)
                        index3 = Routes.index(path)
                        Routes[index3].insert(index2 + 1, [route[1], route[0]])
        indeces = []
        for zeygos in helpRouting:
            for path in Routes:
                if [zeygos[1], zeygos[0]] in path:
                    indexzeygos = helpRouting.index(zeygos)
                    indeces.append(indexzeygos)
        for index in indeces:
            helpRouting[index] = []
        temp = [x for x in helpRouting if x != []]
        temp2 = []
        for pair1 in temp:
            counter1 = 1
            counter2 = 1
            for pair2 in temp:
                if pair1[0] in pair2 and pair2 != pair1:
                    counter1 = counter1 + 1
            if [pair1[0], counter1] not in temp2:
                temp2.append([pair1[0], counter1])
            for pair2 in temp:
                if pair1[1] in pair2 and pair2 != pair1:
                    counter2 = counter2 + 1
            if [pair1[1], counter2] not in temp2:
                temp2.append([pair1[1], counter2])
        temp3 = []
        for pair1 in temp2:
            for pair2 in temp:
                if pair1[1] == 1 and pair1[0] == pair2[0]:
                    temp3.append(pair2)
                    temp.remove(pair2)

        for pair1 in temp3:
            for pair2 in temp:
                if pair1[1] == pair2[0]:
                    indexpair1 = temp3.index(pair1)
                    temp3.insert(indexpair1 + 1, pair2)
                    temp.remove(pair2)
        temp3 = [x for x in temp if x not in temp3] + temp3
        indeces = []
        if temp3 != []:
            for pair in temp3:
                for route in Routes:
                    for path in route:
                        if pair[0] == path[1]:
                            indexpath = route.index(path)
                            indexroute = Routes.index(route)
                            Routes[indexroute].insert(indexpath + 1, pair)
                            indextemp = temp3.index(pair)
                            indeces.append(indextemp)
            for index in indeces:
                temp3[index] = []
            while temp3 != []:
                indeces = []
                temp3 = [x for x in temp3 if x != []]
                temp3.reverse()
                for pair in temp3:
                    for route in Routes:
                        for path in route:
                            if pair[1] == path[1]:
                                indexpath = route.index(path)
                                indexroute = Routes.index(route)
                                Routes[indexroute].insert(indexpath + 1, [pair[1], pair[0]])
                                indextemp = temp3.index(pair)
                                indeces.append(indextemp)
                for index in indeces:
                    temp3[index] = []
                if temp3 != []:
                    temp3 = [x for x in temp3 if x != []]
                    indeces = []
                    temp3.reverse()
                    for pair in temp3:
                        for route in Routes:
                            for path in route:
                                if pair[0] == path[1]:
                                    indexpath = route.index(path)
                                    indexroute = Routes.index(route)
                                    Routes[indexroute].insert(indexpath + 1, pair)
                                    indextemp = temp3.index(pair)
                                    indeces.append(indextemp)
                    for index in indeces:
                        temp3[index] = []
                    temp3 = [x for x in temp3 if x != []]
        return Routing, Routes


    def Hybrid(Savingsi, Savingsi_finder, Wind_turbinesi, Routes, Routing, central_platform_location, Capacityi,
               Routing_red, Routing_green, Costi, Cable_Costi):
        Paths = []
        for WT in Wind_turbinesi:
            Paths.append([0, WT[0]])
        while True:
            if Savingsi != []:
                Savingsi, Savingsi_finder, saving = pop_task(Savingsi, Savingsi_finder)
            else:
                break
            if saving is None or saving[0] > 0:
                break
            arc = [saving[1], saving[2]]
            if check_same_path(arc, Paths) == False and any(
                    [True for e in [[arc[0], 0]] if e in Routing]) == True and one_neighbor(arc[1], Paths) == False:
                condition4 = dict()
                for key, value in Capacityi.iteritems():
                    condition4[key] = check_capacity(arc, Paths, Capacityi[key])
                if condition4[1] is False and edge_crossings(arc, Wind_turbinesi, central_platform_location,
                                                             Routing) is False and \
                                edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                                    0] is False:
                    Routing = []
                    for index1, path in enumerate(Paths):
                        if arc[0] == path[1]:
                            Paths[index1].remove(0)
                            break
                    for index2, path in enumerate(Paths):
                        if arc[1] == path[-1]:
                            break
                    Paths[index2] = Paths[index2] + Paths[index1]
                    Paths[index1] = []
                    Paths = [path for path in Paths if path != []]
                    for i in Paths:
                        for j in xrange(len(i) - 1):
                            Routing.append([i[j + 1], i[j]])
        Routes = []
        for index, path in enumerate(Paths):
            route = []
            for j in xrange(len(path) - 1):
                route.append([path[j], path[j + 1]])
            Routes.append(route)
        return Routes, Routing, Routing_red, Routing_green


    def Esau_Williams_Cable_Choice(Savingsi, Savingsi_finder, Crossingsi_finder, Wind_turbinesi, Routes, Routing,
                                   central_platform_location, Capacityi, Routing_red, Routing_green, Costi, Cable_Costi):
        total_update_red = []
        total_update_green = []
        while True:
            if Savingsi != []:
                Savingsi, Savingsi_finder, saving = pop_task(Savingsi, Savingsi_finder)
            else:
                break
            if saving is None or saving[0] > 0:
                break
            arc = [saving[1], saving[2]]
            lines = turbinesinroute(Routes)
            if check_same_path(arc, lines) == False:
                condcap = dict()
                for key, value in Capacityi.iteritems():
                    condcap[key] = check_capacityEW(arc, lines, Capacityi[key])
                if condcap[1] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] is False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) is False:
                        Routing, Routes = mainroutine(arc, lines, Routes, Routing)
                        lines = turbinesinroute(Routes)
                        for indexl, line in enumerate(lines):
                            if arc[0] in line:
                                break
                        for turbine in lines[indexl]:
                            for n in Wind_turbinesi:
                                value = -(Costi[lines[indexl][0]][0] - Costi[turbine][n[0]]) * Cable_Costi[1]
                                arc1 = [lines[indexl][0], 0]
                                arc2 = [turbine, n[0]]
                                if turbine != n[0]:
                                    value = value + Crossing_penalty * (
                                    Crossingsi_finder[(arc2[0], arc2[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                                Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (turbine, n[0]), value)
                        heapify(Savingsi)
                if len(condcap) > 1 and condcap[1] == True and condcap[2] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False:
                        Routes_temp = deepcopy(Routes)
                        Routing_temp = deepcopy(Routing)
                        total_update_red_temp = []
                        Routing_red_temp = []
                        Routing_temp, Routes_temp = mainroutine(arc, lines, Routes_temp, Routing_temp)
                        lines = turbinesinroute(Routes_temp)
                        for indexl, line in enumerate(lines):
                            if arc[0] in line:
                                break
                        update = []
                        for route in Routes_temp:
                            for i in xrange(0, len(route)):
                                if arc[1] in route[i]:
                                    index = Routes_temp.index(route)
                        elements = len(Routes_temp[index])
                        if elements == 1:
                            index1 = len(Routes_temp[index][0]) - 1 - Capacityi[1]
                            for j in xrange(0, index1):
                                update.append([Routes_temp[index][0][j + 1], Routes_temp[index][0][j]])
                        connected_turbines = []
                        if elements > 1:
                            for i in xrange(0, elements):
                                for j in xrange(len(Routes_temp[index][elements - 1 - i]) - 1, 0, -1):
                                    connected_turbines.append([Routes_temp[index][elements - 1 - i][j - 1],
                                                               Routes_temp[index][elements - 1 - i][j], 1])
                        for pair1 in connected_turbines:
                            for pair2 in connected_turbines:
                                if pair1[0] == pair2[1]:
                                    index = connected_turbines.index(pair2)
                                    connected_turbines[index][2] = connected_turbines[index][2] + pair1[2]
                        for pair in connected_turbines:
                            if pair[2] > Capacityi[1]:
                                update.append([pair[1], pair[0]])
                        total_update_red_temp = renew_update(total_update_red, total_update_red_temp, Routes_temp) + update
                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in xrange(0, len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        new = -(cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green,
                                           Cable_Costi) - cable_cost(central_platform_location, Wind_turbinesi,
                                                                     Routing_temp, Routing_red_temp, Routing_green,
                                                                     Cable_Costi))
                        arc1 = [lines[indexl][0], 0]
                        new = new + Crossing_penalty * (
                        Crossingsi_finder[(arc[0], arc[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Routes = Routes_temp
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            total_update_red = total_update_red_temp
                            lines = turbinesinroute(Routes)
                            for line in lines:
                                if arc[0] in line:
                                    indexl = lines.index(line)
                            for turbine in lines[indexl]:
                                for n in Wind_turbinesi:
                                    value = -(Costi[lines[indexl][0]][0] - Costi[turbine][n[0]]) * Cable_Costi[1]
                                    arc1 = [lines[indexl][0], 0]
                                    arc2 = [turbine, n[0]]
                                    if turbine != n[0]:
                                        value = value + Crossing_penalty * (
                                        Crossingsi_finder[(arc2[0], arc2[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                                    Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (turbine, n[0]), value)
                            heapify(Savingsi)
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (max_saving[1], max_saving[2]),
                                                                 max_saving[0])

                if len(condcap) > 2 and condcap[1] == True and condcap[2] == True and condcap[3] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False:
                        Routes_temp = deepcopy(Routes)
                        Routing_temp = deepcopy(Routing)
                        total_update_red_temp = deepcopy(total_update_red)
                        total_update_green_temp = deepcopy(total_update_green)
                        Routing_temp, Routes_temp = mainroutine(arc, lines, Routes_temp, Routing_temp)
                        lines = turbinesinroute(Routes_temp)
                        for indexl, line in enumerate(lines):
                            if arc[0] in line:
                                break
                        update_red = []
                        update_green = []
                        for route in Routes_temp:
                            for i in xrange(0, len(route)):
                                if arc[1] in route[i]:
                                    index = Routes_temp.index(route)
                        elements = len(Routes_temp[index])
                        if elements == 1:
                            index1 = len(Routes_temp[index][0]) - 1 - Capacityi[1]
                            index2 = len(Routes_temp[index][0]) - 1 - Capacityi[2]
                            for j in xrange(index2, index1):
                                update_red.append([Routes_temp[index][0][j + 1], Routes_temp[index][0][j]])
                            for j in xrange(0, index2):
                                update_green.append([Routes_temp[index][0][j + 1], Routes_temp[index][0][j]])
                        connected_turbines = []
                        if elements > 1:
                            for i in xrange(0, elements):
                                for j in xrange(len(Routes_temp[index][elements - 1 - i]) - 1, 0, -1):
                                    connected_turbines.append([Routes_temp[index][elements - 1 - i][j - 1],
                                                               Routes_temp[index][elements - 1 - i][j], 1])
                        for pair1 in connected_turbines:
                            for pair2 in connected_turbines:
                                if pair1[0] == pair2[1]:
                                    index = connected_turbines.index(pair2)
                                    connected_turbines[index][2] = connected_turbines[index][2] + pair1[2]
                        for pair in connected_turbines:
                            if pair[2] > Capacityi[2]:
                                update_green.append([pair[1], pair[0]])
                            elif pair[2] > Capacityi[1] and pair[2] <= Capacityi[2]:
                                update_red.append([pair[1], pair[0]])

                        for pair in update_red:
                            if pair not in total_update_red_temp:
                                total_update_red_temp.append(pair)
                        total_update_red_temp = [x for x in total_update_red_temp if x in Routing_temp]

                        for pair in update_green:
                            if pair not in total_update_green_temp:
                                total_update_green_temp.append(pair)
                        total_update_green_temp = [x for x in total_update_green_temp if x in Routing_temp]

                        total_update_red_temp = [x for x in total_update_red_temp if x not in total_update_green_temp]

                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in xrange(0, len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        Routing_green_temp = []
                        for route in total_update_green_temp:
                            for z in xrange(0, len(route) - 1):
                                Routing_green_temp.append([route[z], route[z + 1]])
                        arc1 = [lines[indexl][0], 0]
                        new = Crossing_penalty * (
                        Crossingsi_finder[arc[0], arc[1]] - Crossingsi_finder[arc1[0], arc1[1]])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Routes = Routes_temp
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            Routing_green = Routing_green_temp
                            total_update_red = total_update_red_temp
                            total_update_green = total_update_green_temp
                            lines = turbinesinroute(Routes)
                            for line in lines:
                                if arc[0] in line:
                                    indexl = lines.index(line)
                            for turbine in lines[indexl]:
                                for n in Wind_turbinesi:
                                    if turbine != n[0]:
                                        value = -(Costi[lines[indexl][0]][0] - Costi[turbine][n[0]]) * Cable_Costi[1]
                                        arc1 = [lines[indexl][0], 0]
                                        arc2 = [turbine, n[0]]
                                        value = value + Crossing_penalty * (
                                        Crossingsi_finder[arc2[0], arc2[1]] - Crossingsi_finder[arc1[0], arc1[1]])
                                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (turbine, n[0]),
                                                                             value)
                            heapify(Savingsi)
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (max_saving[1], max_saving[2]),
                                                                 max_saving[0])
        return Routes, Routing, Routing_red, Routing_green


    def RouteOpt_Hybrid(Routing, Routing_red, Routing_green, central_platform_location, Costi, Capacityi, Routes,
                        Wind_turbinesi):
        Paths = []
        temp = []
        for route in Routes:
            cond = False
            for i in range(len(route) - 1, -1, -1):
                for pair in route:
                    if route[i][0] == pair[0] and route[i] != pair and cond == False:
                        cond = True
                        for pair5 in route:
                            if pair[0] == pair5[0]:
                                path = []
                                path.append(pair5[0])
                                path.append(pair5[1])
                                for pair6 in route:
                                    if pair6[0] == path[-1]:
                                        path.append(pair6[1])
                                Paths.append(path)
                        temp.append(route)
            if cond == False and len(route) <= Capacityi[1]:
                path = []
                path.append(route[0][0])
                for pair in route:
                    path.append(pair[1])
                Paths.append(path)
            elif cond == False and len(route) > Capacityi[1]:
                index = len(route) - Capacityi[1]
                path = []
                path.append(route[index][0])
                for i in range(index, len(route)):
                    path.append(route[i][1])
                Paths.append(path)
        before = []
        after = []
        for path in Paths:
            list = []
            index = Paths.index(path)
            path.reverse()
            cond = True
            i = 0
            while cond == True:
                for l in range(1, len(path)):
                    list.append([Costi[path[l - 1]][path[l]] - Costi[path[l]][path[0]], path[0], path[l]])
                s = max(list, key=lambda x: x[0])
                if s[0] > 0 and edge_crossings([s[1], s[2]], Wind_turbinesi, central_platform_location,
                                               Routing) == False and \
                                edge_crossings_area([s[1], s[2]], Wind_turbinesi, central_platform_location, Transmission)[
                                    0] == False:
                    for k in list:
                        if k == s:
                            lamd = list.index(k)
                            xmm = lamd + 1
                            path1 = path[:xmm]
                            path2 = path[xmm:]
                            path1.reverse()
                            if i == 0:
                                before.append(Paths[index])
                            i = 1
                            path = path1 + path2
                            Paths[index] = path
                            list = []
                            cond = True
                else:
                    list = []
                    cond = False
                    if i == 1:
                        after.append(Paths[index])

        for path in before:
            for i in range(0, len(path) - 1):
                if [path[i], path[i + 1]] in Routing:
                    Routing.remove([path[i], path[i + 1]])
                elif [path[i + 1], path[i]] in Routing:
                    Routing.remove([path[i + 1], path[i]])
        for path in after:
            for i in range(0, len(path) - 1):
                Routing.append([path[i], path[i + 1]])
        return Routes, Routing


    def renew_update(total_update, total_update_temp, Paths_temp):
        indeces = []
        for indexerase, route in enumerate(total_update):
            for turbine in route:
                if turbine != 0:
                    for pair in total_update_temp:
                        if (pair[0] != 0 and pair[1] == 0) or (pair[0] == 0 and pair[1] != 0):
                            same1 = [turbine, pair[0]]
                        if pair[0] != 0 and pair[1] != 0:
                            same1 = [turbine, pair[0]]
                            same2 = [turbine, pair[1]]
                            if check_same_path(same1, Paths_temp) == True or check_same_path(same2, Paths_temp) == True:
                                if indexerase not in indeces:
                                    indeces.append(indexerase)
        if indeces != []:
            for i in indeces:
                total_update[i] = []
        for pair in total_update[:]:
            if pair == []:
                total_update.remove(pair)
        return total_update


    def initial_values(NT, Wind_turbines, central_platform_location):
        Costi = [[0 for i in xrange(NT + 1)] for j in xrange(NT + 1)]
        set_cost_matrix(Costi, Wind_turbines, central_platform_location)
        distancefromsubstationi = []
        for i in xrange(len(Costi[0]) - 1):
            distancefromsubstationi.append([0, i + 1, Costi[0][i + 1]])
        Wind_turbinesi = []
        return Wind_turbinesi, Costi, distancefromsubstationi


    def initial_routes(Wind_turbinesi):
        Routing_greeni = []
        Routing_redi = []
        Routingi = []
        Routesi = []
        for WT in Wind_turbinesi:
            Routingi.append([WT[0], 0])
            Routesi.append([[0, WT[0]]])
        return Routesi, Routingi, Routing_redi, Routing_greeni


    def check_same_path(arc, Paths):
        same_path = False
        for path in Paths:
            if arc[0] in path and arc[1] in path:
                same_path = True
                break
        return same_path


    # Subroutine 5, check if turbine u has only one neighbor in Routing
    def one_neighbor(turbine, Paths):
        more_than_one = False
        for path in Paths:
            if turbine in path and turbine != path[-1]:
                more_than_one = True
                break
        return more_than_one


    def costi(Wind_turbinesi, central_platform_location):
        Cost0i = []
        Costij = []
        for i in Wind_turbinesi:
            Cost0i.append([0, i[0], hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])])
            for j in Wind_turbinesi:
                if i != j:
                    Costij.append([i[0], j[0], hypot(i[1] - j[1], i[2] - j[2])])
        return Cost0i, Costij


    def savingsi(Cost0i, Costij, Wind_turbinesi, Cable_Cost1, central_platform_location, Area, Crossing_penalty):
        Savingsi = []
        Savingsi_finder = {}
        Crossingsi_finder = {}
        counter = 0
        for i in zip(*Wind_turbinesi)[0]:
            k = Cost0i[counter]
            step = (len(Wind_turbinesi) - 1) * counter
            for j in xrange(step, step + len(Wind_turbinesi) - 1):
                saving = -(k[2] - Costij[j][2]) * Cable_Cost1
                arc1 = [i, 0]
                arc2 = [i, Costij[j][1]]
                crossings_arc1 = edge_crossings_area(arc1, Wind_turbinesi, central_platform_location, Area)[1]
                crossings_arc2 = edge_crossings_area(arc2, Wind_turbinesi, central_platform_location, Area)[1]
                Crossingsi_finder[(arc1[0], arc1[1])] = crossings_arc1
                Crossingsi_finder[(arc2[0], arc2[1])] = crossings_arc2
                saving = saving + Crossing_penalty * (crossings_arc2 - crossings_arc1)
                if saving < 0:
                    add_task(Savingsi, Savingsi_finder, (i, Costij[j][1]), saving)
            counter += 1
        return Savingsi, Savingsi_finder, Crossingsi_finder


    def add_task(Savings, entry_finder, task, priority):
        'Add a new task or update the priority of an existing task'
        if task in entry_finder:
            entry_finder = remove_task(entry_finder, task)
        entry = [priority, task[0], task[1]]
        entry_finder[(task[0], task[1])] = entry
        heappush(Savings, entry)
        return Savings, entry_finder


    def remove_task(entry_finder, task):
        entry = entry_finder.pop(task)
        entry[0] = REMOVED
        return entry_finder


    def pop_task(Savings, entry_finder):
        while Savings:
            saving = heappop(Savings)
            if saving[0] is not REMOVED:
                del entry_finder[(saving[1], saving[2])]
                return Savings, entry_finder, saving


    def set_cost_matrix(Cost, Wind_turbines, central_platform_location):
        Cost[0][0] = float('inf')
        for i in Wind_turbines:
            Cost[0][i[0]] = hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])
            Cost[i[0]][0] = hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])
            for j in Wind_turbines:
                if i == j:
                    Cost[i[0]][j[0]] = float('inf')
                else:
                    Cost[i[0]][j[0]] = hypot(i[1] - j[1], i[2] - j[2])


    def turbinesinroute(Routes):
        lines = [[] for i in xrange(len(Routes))]
        for route in Routes:
            index = Routes.index(route)
            for pair in route:
                lines[index].append(pair[1])
        return lines


    def check_capacityEW(arc, Paths, Capacity):
        cap_exceeded = False
        turbines_in_branch = 0
        for path in Paths:
            if arc[0] in path or arc[1] in path:
                turbines_in_branch = turbines_in_branch + (len(path))
                if turbines_in_branch > Capacity:
                    cap_exceeded = True
                    break
        return cap_exceeded


    def check_capacity(arc, Paths, Capacity):
        cap_exceeded = False
        turbines_in_branch = 0
        for path in Paths:
            if arc[0] in path or arc[1] in path:
                turbines_in_branch = turbines_in_branch + (len(path) - 1)
                if turbines_in_branch > Capacity:
                    cap_exceeded = True
                    break
        return cap_exceeded


    def edge_crossings(arc, Wind_turbines, central_platform_location, Routing):
        x1, y1 = give_coordinates(arc[0], Wind_turbines, central_platform_location)
        x2, y2 = give_coordinates(arc[1], Wind_turbines, central_platform_location)
        intersection = False
        # Left - 0
        # Right - 1
        # Colinear - 2
        for route in Routing:
            if arc[0] not in route:
                x3, y3 = give_coordinates(route[0], Wind_turbines, central_platform_location)
                x4, y4 = give_coordinates(route[1], Wind_turbines, central_platform_location)
                counter = 0
                Area = [0, 0, 0, 0]
                Position = [0, 0, 0, 0]
                Area[0] = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
                Area[1] = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)
                Area[2] = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
                Area[3] = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
                for i in xrange(4):
                    if Area[i] > 0:
                        Position[i] = 0
                    elif Area[i] < 0:
                        Position[i] = 1
                    else:
                        Position[i] = 2
                        counter = counter + 1
                if Position[0] != Position[1] and Position[2] != Position[3] and counter <= 1:
                    intersection = True
                    break
        return intersection

    def edge_crossings_area(arc, Wind_turbines, central_platform_location, Area_cross):
        x1, y1 = give_coordinates(arc[0], Wind_turbines, central_platform_location)
        x2, y2 = give_coordinates(arc[1], Wind_turbines, central_platform_location)
        intersection = False
        crossings = 0
        for area in Area_cross:
            counter = 0
            x3, y3 = area[0][0], area[0][1]
            x4, y4 = area[1][0], area[1][1]
            Area = [0, 0, 0, 0]
            Position = [0, 0, 0, 0]
            Area[0] = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
            Area[1] = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)
            Area[2] = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
            Area[3] = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
            for i in xrange(4):
                if Area[i] > 0:
                    Position[i] = 0
                elif Area[i] < 0:
                    Position[i] = 1
                else:
                    Position[i] = 2
                    counter += 1
            if Position[0] != Position[1] and Position[2] != Position[3] and counter <= 1:
                intersection = True
                crossings += 1
        return intersection, crossings


    # Plotting+Cable_length
    def plotting(fig, central_platform_location1, Wind_turbines1, Routing, Routing_red, Routing_green, Capacityi,
                 Cable_Costi):
        central_platform_location1_1 = [[0, central_platform_location1[0], central_platform_location1[1]]]
        Full_List = central_platform_location1_1 + Wind_turbines1
        Routing_blue = [i for i in Routing if i not in Routing_red]
        Routing_blue = [i for i in Routing_blue if i not in Routing_green]
        cable_length1blue = 0
        index, x, y = zip(*Full_List)
        ax = fig.add_subplot(111)
        ax.set_xlabel('x [km]', fontsize=fontsize2)
        ax.set_ylabel('y [km]', fontsize=fontsize2)
        arcs1 = []
        arcs2 = []
        for i in Routing_blue:
            for j in Full_List:
                if j[0] == i[0]:
                    arcs1.append([j[1], j[2]])
                if j[0] == i[1]:
                    arcs2.append([j[1], j[2]])
        for i in xrange(len(arcs1)):
            arcs1.insert(2 * i + 1, arcs2[i])
        for j in xrange(len(arcs1) - len(Routing_blue)):
            plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='b')
            cable_length1blue = cable_length1blue + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                          arcs1[2 * j][1] - arcs1[2 * j + 1][1])
        cable_cost = Cable_Costi[1] * cable_length1blue
        cable_length = cable_length1blue

        if len(Cable_Costi) == 2:
            cable_length1red = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_red:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in xrange(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in xrange(len(arcs1) - len(Routing_red)):
                plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='r')
                cable_length1red = cable_length1red + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                            arcs1[2 * j][1] - arcs1[2 * j + 1][1])
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red)
            cable_length = cable_length1blue + cable_length1red

        if len(Cable_Costi) == 3:

            cable_length1red = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_red:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in xrange(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in xrange(len(arcs1) - len(Routing_red)):
                plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='r')
                cable_length1red = cable_length1red + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0], arcs1[2 * j][1] - arcs1[2 * j + 1][1])

            cable_length1green = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_green:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in xrange(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in xrange(len(arcs1) - len(Routing_green)):
                plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='g')
                cable_length1green += hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0], arcs1[2 * j][1] - arcs1[2 * j + 1][1])
            cable_length = cable_length1blue + cable_length1red + cable_length1green
            cable_cost = Cable_Costi[1] * cable_length1blue + Cable_Costi[2] * cable_length1red + Cable_Costi[3] * cable_length1green
        plt.plot([p[1] for p in central_platform_location1_1], [p[2] for p in central_platform_location1_1], marker='o',
                 ms=10, color='0.35')
        plt.plot([p[1] for p in Wind_turbines1], [p[2] for p in Wind_turbines1], 'o', ms=6, color='0.3')
        return cable_length, cable_cost, ax


    def cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green, Cable_Costi):
        Routing_blue = [i for i in Routing if i not in Routing_red]
        Routing_blue = [i for i in Routing_blue if i not in Routing_green]
        cable_length1blue = 0
        for route in Routing_blue:
            x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
            x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
            cable_length1blue = cable_length1blue + hypot(x2 - x1, y2 - y1)
        cable_cost = Cable_Costi[1] * (cable_length1blue)

        if len(Cable_Costi) == 2:
            cable_length1red = 0
            for route in Routing_red:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1red = cable_length1red + hypot(x2 - x1, y2 - y1)
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red)

        if len(Cable_Costi) == 3:
            cable_length1red = 0
            for route in Routing_red:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1red = cable_length1red + hypot(x2 - x1, y2 - y1)
            cable_length1green = 0
            for route in Routing_green:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1green = cable_length1green + hypot(x2 - x1, y2 - y1)
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red) + Cable_Costi[3] * (
            cable_length1green)
        return cable_cost


    # Submethods return x and y coordinates of a turbine if it's ID is known. The OHVS must also be included
    def give_coordinates(turbineID, Wind_turbines, central_platform_location):
        if turbineID == 0:
            x = central_platform_location[0]
            y = central_platform_location[1]
        else:
            # print turbineID, turbineID - 1
            turbine = WT_List[turbineID - 1]
            x = turbine[1]
            y = turbine[2]
        return x, y

    return set_cable_topology(WT_List, central_platform_locations, Cable_List)

# ------------------------------------Run------------------------------------------------------------------

if __name__ == '__main__':
    # ---------------------------------
    central_platform = [[3000.0, 3000.0], [0.0, 0.0], [3000.0, 0.0], [0.0, 3000.0]]
    import numpy as np
    from time import time, clock
    number_turbines_per_cable = [2, 4, 7]# [2, 4, 7]
    from math import sqrt

    voltage = 66000.0
    rated_power = 10000000.0
    rated_current = rated_power / sqrt(3) / voltage
    def read_cablelist():
        cables_info = []
        with open("cable_list.dat",
                  "r") as cables:
            next(cables)
            for line in cables:
                cols = line.split()
                cables_info.append([float(cols[0]), float(cols[1]), float(cols[2])])
        return cables_info



    cables_info = read_cablelist()
    Cable_List = []
    for number in number_turbines_per_cable:
        for cable in cables_info:
            if rated_current * number <= cable[1]:
                # print number, cable[2], rated_current
                Cable_List.append([number, cable[2] + 365.0])
                break
    layout = []
    with open("../../../../../guideline/baseline/square/substation_layout_74.dat", "r") as inp:
        for i, line in enumerate(inp):
            cols = line.split()
            # print cols
            layout.append([i, float(cols[0]), float(cols[1])])

    WT_List = layout

    draw_cables(WT_List, central_platform, Cable_List)
