karman = 0.41  # von Karman constant

 
def b(deficit, ct):  # Wake width measure
    if deficit <= 0.0:
        deficit = 0.0000000000001
    if 1.0 - 0.5 * deficit < 0.0:
        print deficit, "raro_viejo"
    return (3.56 * ct / (8.0 * deficit * (1.0 - 0.5 * deficit))) ** 0.5


def F(x):  # Factor for near and far wake
    if x >= 5.5:
        return 1.0
    if x < 5.5:
        if x >= 4.5:
            return 0.65 + ((x - 4.5) / 23.32) ** (1.0 / 3.0)
        else:
            return 0.65 - ((- x + 4.5) / 23.32) ** (1.0 / 3.0)


def E(x1, Ud, Dm, u0, i0, ct):  # Eddy viscosity term
    eddy = F(x1) * ((0.015 * b(Dm, ct) * (u0 - Ud)) + (karman ** 2.0) * i0)
    return eddy
