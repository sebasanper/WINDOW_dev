from random import random, sample
from transform_quadrilateral import AreaMapping
from farm_description import n_quadrilaterals, separation_equation_y, NT
import numpy as np
from numpy import sin, cos, deg2rad

def centroid(areas):
    return sum([place[0] for area in areas for place in area]) / len(areas.flatten()) * 2.0, sum([place[1] for area in areas for place in area]) / len(areas.flatten()) * 2.0

def rotate(turbine1, angle, origin):

    turbine = [turbine1[0] - origin[0], turbine1[1] - origin[1]]
    rotated = [turbine[0] * (cos(angle)) - turbine[1] * sin(angle), turbine[0] * (sin(angle)) + turbine[1] * cos(angle)]
    return [rotated[0] + origin[0], rotated[1] + origin[1]]

def regular_layout(dx, dy, dh, areas, angle, print_layout):
    layout_final = []
    centroid_small = centroid(areas)
    # print centroid_small
    angle = deg2rad(angle)
    with open("area.dat", "w") as areaout:
        for area in areas:
            for n in range(4) + [0]:
                areaout.write("{} {}\n".format(area[n][0], area[n][1]))

    n_rows = int((max([rotate(place, angle, centroid_small)[0] for area in areas for place in area]) - min([rotate(place, angle, centroid_small)[0] for area in areas for place in area])) / dx) + 10
    n_columns = int((max([rotate(place, angle, centroid_small)[1] for area in areas for place in area]) - min([rotate(place, angle, centroid_small)[1] for area in areas for place in area])) / dy) + 10
    layout = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout_translated = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout_rotated = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    x0, y0 = min([place[0] for area in areas for place in area]), min([place[1] for area in areas for place in area])
    layout[0][0] = [x0, y0]
    last_x = layout[0][0][0] + dx * n_rows
    last_y = layout[0][0][1] + dy * n_columns
    big_area = np.array([[layout[0][0], [last_x, layout[0][0][1]], [last_x, last_y], [layout[0][0][0], last_y]]])
    centroid_big = centroid(big_area)
    # print centroid_big
    for j in range(1, n_columns):
        if j % 2 == 0:
            layout[0][j] = [layout[0][j - 1][0] - dh, layout[0][j - 1][1] + dy]

        else:
            layout[0][j] = [layout[0][j - 1][0] + dh, layout[0][j - 1][1] + dy]

    for i in range(1, n_rows):
        layout[i][0] = [layout[i - 1][0][0] + dx, layout[i - 1][0][1]]

        for j in range(1, n_columns):
            if j % 2 == 0:
                layout[i][j] = [layout[i][j - 1][0] - dh, layout[i][j - 1][1] + dy]

            else:
                layout[i][j] = [layout[i][j - 1][0] + dh, layout[i][j - 1][1] + dy]

    for i in range(n_rows):
        for j in range(n_columns):
            layout_translated[i][j] = [layout[i][j][0] - (centroid_big[0] - centroid_small[0]), layout[i][j][1] - (centroid_big[1] - centroid_small[1])]
            layout_rotated[i][j] = rotate(layout_translated[i][j], angle, centroid_small)
    eps = 1e-8

    squares = []
    for n in range(n_quadrilaterals):
        square = [[1.0 / n_quadrilaterals * n, 0.0], [n * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 0.0]]
        squares.append(square)
    maps = [AreaMapping(areas[n], squares[n]) for n in range(n_quadrilaterals)]
    count = 0
    for i in range(n_rows):
        for j in range(n_columns):
            if separation_equation_y(layout_rotated[i][j][0]) < layout_rotated[i][j][1] or len(areas) == 1:
                mapped = maps[0].transform_to_rectangle(layout_rotated[i][j][0], layout_rotated[i][j][1])
            else:
                mapped = maps[1].transform_to_rectangle(layout_rotated[i][j][0], layout_rotated[i][j][1])

            if mapped[0] >= 0.0 - eps and mapped[0] <= 1.0 + eps and mapped[1] >= 0.0 - eps and mapped[1] <= 1.0 + eps:
                extra = 0
                layout_final.append([layout_rotated[i][j][0], layout_rotated[i][j][1]])
                count += 1
            else:
                extra = 1
    print count
    if count <= 74:
            to_add = 74 - count
            layout_final += [[0.0, 0.0] for _ in range(to_add)]
            reduced = layout_final
    elif count > 74:
        if count % 2 == 0:
            to_remove1 = to_remove2 = (count - 74) / 2
        else:
            to_remove1, to_remove2 = (count - 74) / 2, (count - 74) / 2 + 1
        reduced = layout_final[to_remove1:- to_remove2]
    if print_layout == True:
        with open("layout_draw.dat", "w") as out:
            for item in reduced:
                out.write("{} {}\n".format(item[0], item[1]))
    return reduced, count


if __name__ == '__main__':
    from farm_description import areas
    from random import uniform
    # [ 2394.72140817] [ 951.44319218] [ 508.77654122] [ 76.81854513]

    # [  854.77482677  2130.96378044   479.15059769   158.44208913] 6.77467530312
    # [1212.3432058726044, 1857.2419373594398, 1196.7844285385258, 131.4387661905908] [ 6.65410628] LCOE



   # [ 963.76288446] [ 2418.24137673] [ 1033.51506808] [ 75.98448581] 


   # 1589.47092779] [ 1597.54552192] [ 129.35847029] [ 99.53599745
   # [ 969.34641881] [ 2428.05402564] [ 1033.85393252] [ 46.63310252]
    print(regular_layout(969.34641881, 2428.05402564, 1033.85393252, areas, 46.63310252, True))
    # print(regular_layout(1391.22013673,  1852.79334031,   353.77828467, areas,   164.39541089, True))
    # print(regular_layout(1594.87471748,  1523.08957722,   650.57010833, areas,   284.27493592, True))
    # print(regular_layout(2181.63740977,  1080.48144669,   191.47025204, areas,   120.92938254, True)) # 6.7915460967304453
    # print(regular_layout(1273.70700573,  1834.37446286,    29.56929332,   areas,   225.0460898 , True))
    # with open("regular_borssele_test.dat", "a") as regular_file:
    #     for _ in range(10000):
    #         sample = [uniform(570.0,2500.0), uniform(570.0,2500.0), uniform(0.0, 1250.0), uniform(0.0, 180.0)]
    #         lay, cnt = regular_layout(sample[0], sample[1], sample[2], areas, sample[3])
    #         if 74 == cnt:
    #             regular_file.write("{} {} {} {} {}\n".format(sample[0], sample[1], sample[2], sample[3], cnt))
    #             print cnt, sample
 # 1.090844E+00   1.400479E+03   1.397751E+03  -2.127649E+01
