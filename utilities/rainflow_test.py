# from rainflow_counting import rainflow
# from random import random
# from numpy import array


# a = array([random() - 0.5 for _ in range(100)])
# with open("signal.dat", "w") as signal:
#     for point in a:
#         signal.write("{0:f}\n".format(point))
# print rainflow(a)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import rainflow_counting as rf
    import numpy as np

    # array of turning points
    array_ext = np.array([3, -2, 4, 2, 6, -1, 1, 0, 3, -2, 4, 2, 5, -1, 1, 0, 3, -2, 4, 2, 5, -1, 1, 0, 3])
    # 3, -2, 4, 2, 5, -1, 1, 0, 3
    # calculate cycle counts with default values for lfm (0),
    #  l_ult (1e16), and uc_mult (0.5)
    array_out = rf.rainflow(array_ext)

    # print array_out
    # sort array_out by cycle range
    # array_out = array_out[:, array_out[0, :].argsort()]

    # ---------------------------- printing/plotting ------------------------------

    # theoretical cycle counts (range,count)
    theo_cycles = [[1, 1], [2, 1], [4, 0.5], [5, 0.5], [6, 0.5], [7, 0.5]]
    print('\nTheoretical cycle count:')
    print('\n{:>7s}{:>8s}'.format('Range', 'Count'))
    print('------------------')
    for i in range(len(theo_cycles)):
        print('{:7.1f}{:8.1f}'.format(*theo_cycles[i]))

    # print cycle range, cycle count, cycle mean, goodman-adjusted range (GAR), and
    #   goodman-adjusted range with zero fixed-load mean (GAR-ZFLM)
    print('\nCalculated cycle count:')
    print('\n{:>7s}{:>8s}{:>8s}{:>8s}{:>12s}'.format('Range', 'Count',
                                                     'Mean', 'GAR', 'GAR-ZFLM'))
    print('----------------------------------------------')
    for i in range(len(array_out[0])):
        print('{:7.1f}   {:8.1f}'.format(array_out[0][i], array_out[1][i]))

    # plot turning points for vizualization
    plt.figure(1, figsize=(6.5, 3.5))
    plt.clf()

    plt.plot(array_ext)
    plt.grid('on')
    plt.xlabel('Time')
    plt.ylabel('Turning Points')
    plt.title('Turning Points for Rainflow Demo - J. Rinker')
    plt.tight_layout()

    plt.show()
