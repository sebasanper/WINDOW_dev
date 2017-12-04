__author__ = 'Sebastian Sanchez Perez-Moreno. Email: s.sanchezperezmoreno@tudelft.nl'

from math import ceil, floor, log
from random import randint, random, uniform
import time
from joblib import Parallel, delayed
from transform_quadrilateral import AreaMapping
from openmdao.api import Problem
from workflow_cheap import LCOE
from farm_description import NT, n_quadrilaterals, areas, separation_equation_y

result = open('gen7_best_layout_aep2.dat', 'w', 1)
result2 = open('gen7_fitness_aep2.dat', 'w', 1)
average = open('gen7_average_fitness_aep2.dat', 'w', 1)
start_time = time.time()

#  gen1 with     n_iter = 8000    n_ind = 100    mutation_rate = 0.01    selection_percentage = 0.3  random_selection = 0.05 100-13.24%=86.76% eff.
#  gen 2 same as gen1. Corrected min distance to 2D, instead of 1D. Changed to maximise efficiency instead. Using n_ind = 50 individuals for speed. 87.53% efficiency.
#  gen3     n_iter = 20    n_ind = 100. 2000 functions calls = 8 hrs.
#  gen 5 same as gen 3 more iter to 50
#  gen 6 windrose 360 degrees for speed. selection rate 0.2. each iteration took 10.69 minutes. 1069 minutes in total. too long.
#  gen7 as gen6 with     n_iter = 50    n_ind = 80

prob = Problem()
# print clock(), "Before defining model"
prob.model = LCOE()
prob.setup()

def objfunc(x):
    prob['indep2.layout'] = x
    prob.run_model()
    f = prob['analysis.lcoe'][0]
    f += prob['constraint_boundary.n_constraint_violations'] * 5.0 + prob['constraint_distance.n_constraint_violations'] * 5.0
    return - f

def gen_individual(n_turbines):
    return [gen_turbine() for k in range(n_turbines)]

def gen_population(n_ind, n_turbines):
    return [gen_individual(n_turbines) for x in range(n_ind)]

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

def gen_turbine():
    a = create_random()
    return a

def grade_gen(b, n):
    average = 0.0
    for item in b:
        average += item / n
    return average

def genetic():

    n_iter = 50
    n_ind = 100
    nt = 74
    mutation_rate = 0.01
    selection_percentage = 0.2
    random_selection = 0.05

    pops = gen_population(n_ind, nt)
    # pops.append([])
    # layout = open('horns_rev.dat', 'r')
    # for line in layout:
    #    columns = line.split()
    #    pops[-1].append([float(columns[0]) - 423974.0, float(columns[1]) - 6147540.0])
    # layout.close()
    n_ind = len(pops)
    for iteration in range(n_iter):  # Iteration through generations loop
        start_time2 = time.time()
        pop = pops
        # for x in range(nt):
        #     result.write('{0:d}\t{1:d}\n'.format(int(pop[0][x][0]), int(pop[0][x][1])))
        # result.write('\n')
        # pop = Parallel(n_jobs=-1)(delayed(find_distance)(nt, pop[x], diam, min_x, max_x, min_y, max_y) for x in range(n_ind))  # Parallel verification of minimum distance between turbines to 2D
        # for x in range(nt):
        #     result.write('{0:d}\t{1:d}\n'.format(int(pop[0][x][0]), int(pop[0][x][1])))
        # result.write('\n')
        # Calls the Wake Model
        fit = Parallel(n_jobs=-1)(delayed(objfunc)(pop[i]) for i in range(n_ind))  # Parallel evaluation of fitness of all individuals
        # fit = [objfunc(pop[i]) for i in range(n_ind)]
        aver = grade_gen(fit, float(n_ind))

        average.write('{}\n'.format(aver))

        for i in range(n_ind):
            fit[i] = [fit[i], i]
        for x in range(nt):
            result.write('{}\t{}\n'.format(int(pop[max(fit)[1]][x][0]), int(pop[max(fit)[1]][x][1])))  # This max implies maximisation.
        result.write('\n')

        for y in range(n_ind):
            result2.write('{}\n'.format(fit[y][0][0]))
        result2.write('\n')

        graded = [x[1] for x in sorted(fit, reverse=True)]

        retain_length = int(len(graded) * selection_percentage)
        parents_index = graded[:retain_length]

        # Add randomly other individuals for variety
        for item in graded[retain_length:]:
            if random_selection > random():
                parents_index.append(item)

        # Mutation of individuals
        for item in parents_index:
            if mutation_rate > random():
                place = randint(0, len(pop[item]) - 1)
                pop[item][place] = gen_turbine()

        pops = []
        for item in parents_index:
            pops.append(pop[item])

        # Crossover function. Create children from parents
        parents_length = len(parents_index)
        desired_length = n_ind - parents_length
        children = []
        while len(children) < desired_length:
            parent1 = randint(0, parents_length - 1)
            parent2 = randint(0, parents_length - 1)
            if parent1 != parent2:
                parent1 = pop[parents_index[parent1]]
                parent2 = pop[parents_index[parent2]]
                cross_place = randint(0, nt - 1)
                child = parent1[:cross_place] + parent2[cross_place:]
                children.append(child)
        pops.extend(children)

        print("%d iteration--- %s minutes ---" % (iteration, (time.time() - start_time2) / 60.0))
        print len(pops)
    print("--- %s minutes ---" % ((time.time() - start_time) / 60.0))
    result.close()
    result2.close()
    average.close()

if __name__ == '__main__':
    genetic()
