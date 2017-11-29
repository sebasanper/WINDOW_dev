import numpy as np
from matplotlib import pyplot as plt, style
from mpl_toolkits.mplot3d import Axes3D
from random import randint, random
from copy import deepcopy
from statistics import mode, mean, StatisticsError
from functools import reduce
from joblib import Parallel, delayed
# from pareto_epsilon import eps_sort
from math import sqrt, sin
from dynamic_weights2 import dynamic_weights
import call_workflow_once as wf
fitness = wf.results_median_workflow
style.use('ggplot')


# def memoize(fn):
#     """returns a memoized version of any function that can be called
#     with the same list of arguments.
#     Usage: foo = memoize(foo)"""
#
#     def handle_item(x):
#         if isinstance(x, dict):
#             return make_tuple(sorted(x.items()))
#         elif hasattr(x, '__iter__'):
#             return make_tuple(x)
#         else:
#             return x
#
#     def make_tuple(L):
#         return tuple(handle_item(x) for x in L)
#
#     def foo(*args, **kwargs):
#         items_cache = make_tuple(sorted(kwargs.items()))
#         args_cache = make_tuple(args)
#         if (args_cache, items_cache) not in foo.past_calls:
#             foo.past_calls[(args_cache, items_cache)] = fn(*args, **kwargs)
#         return foo.past_calls[(args_cache, items_cache)]
#
#     foo.past_calls = {}
#     foo.__name__ = 'memoized_' + fn.__name__
#     return foo


def criteria(x):
    n_bins = x[0] + 3
    angles = [1.0, 5.0, 15.0, 30.0][x[1]]
    lcoe, stddev_finance, time, stddev_time, n_power_calls, n_thrust_calls = fitness(n_bins, angles, x[2], x[3], x[4], x[5], x[6], x[7])

    error = abs(lcoe - 7.89829164727)

    return [error, time, stddev_finance]
# function1 = memoize(function1)


def mode_custom(x):
    i = 0
    while True:
        try:
            x_mode = mode(x)
            break
        except StatisticsError:
            x = np.append(x, i)
            i += 1
    return x_mode


def generate_weights(num_weights):
    random_nums = np.random.random(num_weights - 1)
    random_nums[::-1].sort()
    weights = [1.0 - random_nums[0]]
    for i in range(1, num_weights - 1):
        weights.append(random_nums[i - 1] - random_nums[i])
    weights.append(random_nums[-1])
    return weights


def normalise(vector):
    summation = sum(vector)
    if summation == 0.0:
        vector = generate_weights(len(vector))
    else:
        vector = [n / summation for n in vector]
    return vector


def dominates(candidate, particle):
    return sum([candidate[0][x] <= particle[0][x] for x in range(len(candidate[0]))]) == len(candidate[0])


def dominate_one_in_swarm(candidate, swarm):
    for particle in swarm:
        if dominates(candidate, particle):
            flag = True
            break
    else:
        flag = False
    return flag


def dominates_any(candidate, archive):
    for particle in archive:
        if dominates(candidate, particle):
            out = particle
            break
    else:
        out = None
    return out


def dominated(archive):
    for particle1 in archive:
        for particle2 in archive:
            if dominates(particle1, particle2):
                out = particle2
                break
        break
    else:
        out = None
    return out


def not_dominated(candidate, archive):
    for particle in archive:
        if dominates(particle, candidate):
            flag = True
            break
    else:
        flag = False
    return flag


def distance_multidimension(x, y):
    sum_ = 0
    for i in range(len(x)):
        sum_ += (x[i] - y[i]) ** 2.0
    return sqrt(sum_)


def similarity(candidate, archive, tolerance):
    for particle in archive:
        if distance_multidimension(candidate[0], particle[0]) < tolerance:
            flag = True
            break
    else:
        flag = False
    return flag


def replace(list_, old, new):
    for i, v in enumerate(list_):
        if v == old:
            list_.pop(i)
            list_.insert(i, new)


def eliminate(list_, to_be_deleted):
    for i, v in enumerate(list_):
        if v == to_be_deleted:
            list_.pop(i)


def fitness_function(sample, fitness_functions):
    return [fitness(sample) for fitness in fitness_functions]


class PSOCategorical:
    def __init__(self, n_particles, scaling_factor):
        self.n_functions = 3
        self.weight_local = 1.49618
        self.weight_global = 1.49618
        self.inertia_weight = 0.729
        self.n_particles = n_particles
        self.scaling_factor = scaling_factor
        self.categories = [list(range(11)), list(range(4)), list(range(4)), list(range(6)), list(range(4)),
                           list(range(4)), list(range(4)), list(range(2))]
        self.positions_categorical = [[[0 for _ in var] for var in self.categories] for _ in range(self.n_particles)]
        self.velocities_categorical = [[[0 for _ in var] for var in self.categories] for _ in range(self.n_particles)]
        self.local_best_fitness = [999999.9 for _ in range(self.n_particles)]
        self.global_best_fitness = 999999.9
        self.local_best = []
        self.global_best = []
        self.samples = [[] for _ in range(self.n_particles)]
        self.fitness = [[999999.9 for _ in range(self.n_functions)] for _ in range(self.n_particles)]
        self.obj_function = [0.0 for _ in range(self.n_particles)]
        self.archive = []
        self.archive_size = 20
        self.old_swarm = []
        self.fitness_and_samples = list(zip(self.fitness, self.samples))

    def update_archive(self, swarm):
        for particle in swarm:
            if dominate_one_in_swarm(particle, self.old_swarm) and not_dominated(particle, self.archive) is False and similarity(particle, self.archive, 1e-5) is False:
                to_be_changed = dominates_any(particle, self.archive)
                to_be_substituted = dominated(self.archive)
                if len(self.archive) < self.archive_size:
                    self.archive.append(particle)
                elif to_be_changed:
                    replace(self.archive, to_be_changed, particle)
                elif to_be_substituted:
                    replace(self.archive, to_be_substituted, particle)

        for solution1 in self.archive:
            for solution2 in self.archive:
                if solution1 != solution2:
                    if dominates(solution1, solution2):
                        eliminate(self.archive, solution2)

    def representative_sample(self, distribution):
        samples = []
        for _ in range(self.n_samples):
            samples.append(self.sample_distribution(distribution))
        samples = np.array(samples)
        representative_sample = [mode_custom(samples[:, i]) for i in range(len(self.categories))]
        return representative_sample

    def initialise_categorical_positions(self):
        for particle in range(self.n_particles):
            for variable in range(len(self.categories)):
                weights = generate_weights(len(self.categories[variable]))
                self.positions_categorical[particle][variable] = weights
        self.local_best = deepcopy(self.positions_categorical)
        self.global_best = deepcopy(self.local_best[0])

    def initialise_categorical_velocities(self):
        for particle in range(self.n_particles):
            for variable in range(len(self.categories)):
                velocities = [random() for _ in self.categories[variable]]
                self.velocities_categorical[particle][variable] = velocities

    def update_position(self):
        for particle in range(self.n_particles):
            for var in range(len(self.categories)):
                for prob in range(len(self.categories[var])):
                    self.positions_categorical[particle][var][prob] += self.velocities_categorical[particle][var][prob]
                    if self.positions_categorical[particle][var][prob] > 1:
                        self.positions_categorical[particle][var][prob] = 1.0
                    elif self.positions_categorical[particle][var][prob] < 0:
                        self.positions_categorical[particle][var][prob] = 0.0

        for part in range(self.n_particles):
            for var in range(len(self.categories)):
                # print(self.positions_categorical[part][var])
                self.positions_categorical[part][var] = normalise(self.positions_categorical[part][var])

    def update_global_best(self, position, sample):
        for var in range(len(self.categories)):
            for prob in range(len(self.categories[var])):
                if prob != sample[var]:
                    self.global_best[var][prob] = self.scaling_factor * position[var][prob]
                else:
                    summation = sum([(1.0 - self.scaling_factor) * pr if position[var].index(pr) != prob else 0 for pr
                                     in position[var]])
                    self.global_best[var][prob] = position[var][prob] + summation

    def update_local_best(self, particle, position, sample):
        for var in range(len(self.categories)):
            for prob in range(len(self.categories[var])):
                if prob != sample[var]:
                    self.local_best[particle][var][prob] = self.scaling_factor * position[var][prob]
                else:
                    summation = sum([(1.0 - self.scaling_factor) * pr if position[var].index(pr) != prob else 0 for pr
                                     in position[var]])
                    self.local_best[particle][var][prob] = position[var][prob] + summation

    def sample_distribution(self, distribution):
        sample = [np.random.choice(self.categories[var], p=distribution[var]) for var in range(len(distribution))]
        return sample

    def calculate_new_velocities(self):
        for particle in range(self.n_particles):
            for var in range(len(self.categories)):
                for prob in range(len(self.categories[var])):
                    if random() < 0.2:
                        turbulence = random()
                    else:
                        turbulence = 0.0
                    self.velocities_categorical[particle][var][prob] = self.inertia_weight * \
                                                                       self.velocities_categorical[particle][var][prob] \
                                                                       + self.weight_global * random() * \
                                                                       (self.global_best[var][prob] -
                                                                       self.positions_categorical[particle][var][prob])\
                                                                       + self.weight_local * random() * \
                                                                       (self.local_best[particle][var][prob] -
                                                                        self.positions_categorical[particle][var][prob])\
                                                                       + turbulence

    def run(self):
        # plt.ion()
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # fig, ax = plt.subplots()
        from time import time
        from math import sin, pi, copysign
        start = time()
        self.initialise_categorical_positions()
        self.initialise_categorical_velocities()
        self.n_iterations = 48
        self.n_samples = 3
        self.archive_size = 20
        weights_all = dynamic_weights(self.n_iterations, 4)
        for iteration in range(self.n_iterations):
            print("iteration:", iteration)
            # print(len(self.archive))
            # if iteration % 500 == 0 and iteration > 1:
            #     if sum([sqrt((item1[0][0] - item2[0][0]) ** 2.0 + (item1[0][1] - item2[0][1]) ** 2.0) for item1, item2 in zip(self.archive, history)]) <= 0.001:
            #         print("early exit", iteration)
            #         break
            # if iteration % 500 == 0:
            #     history = deepcopy(self.archive)
            weights = [weights_all[i][iteration] for i in range(self.n_functions)]
            # weights = [1.0, 0.0, 0.0]
            self.calculate_new_velocities()
            self.update_position()
            # weight1 = copysign(1.0, sin(10.0 * 2.0 * pi * iteration / self.n_iterations))
            # if weight1 < 1:
            #     weight1 = 0.0
            # weight1 = abs(sin(5.0 * 2.0 * pi * iteration / self.n_iterations))
            # weight2 = 1.0 - weight1
            # weights = [weight1, weight2, 0.0]
            # if iteration % 25 == 0:
            #     weights = generate_weights(self.n_functions)
            self.samples = [self.representative_sample(position) for position in self.positions_categorical]
            self.fitness = Parallel(n_jobs=-2)(delayed(criteria)(sample) for sample in self.samples)
            # self.fitness = [criteria(sample) for sample in self.samples]
            self.fitness_and_samples = list(zip(self.fitness, self.samples))
            self.old_swarm = deepcopy(self.fitness_and_samples)

            for particle in range(self.n_particles):
                self.obj_function[particle] = sum([weights[i] * self.fitness[particle][i] for i in range(self.n_functions)])

            self.update_archive(self.fitness_and_samples)
            for particle in range(self.n_particles):
                if self.obj_function[particle] < self.local_best_fitness[particle]:
                    self.update_local_best(particle, self.positions_categorical[particle], self.samples[particle])
                    self.local_best_fitness[particle] = self.obj_function[particle]
                if self.obj_function[particle] < self.global_best_fitness:
                    self.update_global_best(self.positions_categorical[particle], self.samples[particle])

            # plt.cla()
            # ax.scatter([item[0][0] for item in self.archive], [item[0][1] for item in self.archive], [item[0][2] for item in self.archive])
            # plt.pause(0.01)

            with open("MOPSOC_28nov.dat", "a", 1) as out:
                for item in self.archive:
                    out.write("{} {} {} {}\n".format(item[0][0], item[0][1], item[0][2], item[1]))
                out.write("\n\n")
            print(time() - start, "seconds")
            # while True:
            #     plt.pause(0.05)

if __name__ == '__main__':
    opt = PSOCategorical(20, 0.1)
    opt.run()
