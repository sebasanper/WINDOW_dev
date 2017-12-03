from numpy import exp, sqrt
import numpy as np
import pickle


def distance(x0, y0, x, y):
    return sqrt((x0 - x) ** 2.0 + (y0 - y) ** 2.0)


class Flat:
    def __init__(self, minx, maxx, miny, maxy):
        pass

    def depth(self, x, y):
        return 13.5


class Plane:
    def __init__(self, minx, maxx, miny, maxy):
        point1 = [maxx, maxy, 15]
        point2 = [minx, miny, 12.0]
        point3 = [minx, miny + 1.0, 12.0]
        self.point1 = [float(point1[i]) for i in range(3)]
        self.point2 = [float(point2[i]) for i in range(3)]
        self.point3 = [float(point3[i]) for i in range(3)]

    def depth(self, x, y):
        x1 = self.point1[0]
        x2 = self.point2[0]
        x3 = self.point3[0]
        y1 = self.point1[1]
        y2 = self.point2[1]
        y3 = self.point3[1]
        z1 = self.point1[2]
        z2 = self.point2[2]
        z3 = self.point3[2]

        return ((y - y1) * ((x2 - x1) * (z3 - z1) - (x3 - x1) * (z2 - z1)) - (x - x1) * ((y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1))) / ((x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)) + z1


class Gaussian:
    def __init__(self, minx, maxx, miny, maxy):
        self.centre = [minx + (maxx - minx) / 2.0, miny + (maxy - miny) / 2.0]
        self.sigma_x = distance(self.centre[0], self.centre[1], minx, miny) * 3.0 / 2.0  # Sigma is (max - desired value) times the distance from centre of rectangle to the sides, divided by two. Example: Rectangle is 4000x900. Centre at 2000x450. So 450 to one side, 450 * 3 = 1350 / 2 = 675.0. 3 is 15.0 m - 12.0 m (max - min water depth).
        self.sigma_y = self.sigma_x
        self.height = 15.0

    def depth(self, x, y):
        # print self.centre, self.sigma_x, self.sigma_y
        return self.height * exp(- ((x - self.centre[0]) ** 2.0 / 2.0 / self.sigma_x ** 2.0 + (y - self.centre[1]) ** 2.0 / 2.0 / self.sigma_y ** 2.0))


class Rough:

    def __init__(self, minx, maxx, miny, maxy):
        pick_file = open("site_conditions/terrain/bathymetry.pkl", "rb")
        self.bathymetry = pickle.load(pick_file)
        pick_file.close()


    def closest_node(self, node, nodes):
        nodes = np.asarray(nodes)
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)

        # self.coordinates_x = []
        # self.coordinates_y = []
        # self.depths = []
        # with open("bathymetry_table.dat", "r") as bathymetry_file:
        #     for line in bathymetry_file:
        #         cols = line.split()
        #         self.coordinates_x.append(float(cols[0]))
        #         self.coordinates_y.append(float(cols[1]))
        #         self.depths.append(float(cols[2]))
        # from scipy.interpolate import interp2d
        # degree = 'linear'  # 'cubic' 'quintic'
        # self.interpfunction = interp2d(self.coordinates_x[::50], self.coordinates_y[::50], self.depths[::50], kind=degree)

    def depth(self, x, y):
        # print time() - start
        return self.bathymetry[self.closest_node([x, y], self.bathymetry[:,[0, 1]])][2]


def depth(layout, model_type):
    terrain = model_type
    return [terrain.depth(layout[i][1], layout[i][2]) for i in range(len(layout))]


if __name__ == '__main__':
    # from time import time
    # import numpy as np
    # import pickle
    # # bathymetry = np.zeros((605 * 568, 3))
    # # i = 0
    # # with open("bathymetry_table.dat", "r") as inf:
    # #     for line in inf:
    # #         x = line.split()
    # #         bathymetry[i] = x
    # #         i += 1
    # # pickle_file = open("bathymetry.pkl", "wb")
    # # pickle.dump(bathymetry, pickle_file)
    # # pickle_file.close()
    # pick_file = open("bathymetry.pkl", "rb")
    # bathymetry = pickle.load(pick_file)

    # def closest_node(node, nodes):
    #     nodes = np.asarray(nodes)
    #     dist_2 = np.sum((nodes - node)**2, axis=1)
    #     return np.argmin(dist_2)

    # start = time()
    # print bathymetry[closest_node([496700.0, 5728000.0], bathymetry[:,[0, 1]])].tolist()
    # # print (depth([[0, 496700.0, 5728000.0]], Rough(3, 4, 4, 3)))
    # print time() - start
    # pick_file.close()
    pass