import numpy as np


def resistance(blade_speed):
    x = [9.43, 10.47, 18.85]
    y = [2.47, 2.73, 3.77]

    # add an extra point
    x += [2 * x[-1] - x[-2]]
    y += [2 * y[-1] - y[-2]]

    if blade_speed > max(y) and False:
        raise ValueError('YOUVE BROKEN THE GENERATOR LOL')
    return np.interp(blade_speed, x, y)


def knots(x):
    return x * 0.5144


def ms(x):
    return x / 0.5144


def rpm(x):
    return x * 0.1047


def rads(x):
    return x / 0.1047


system = (0.945, resistance)