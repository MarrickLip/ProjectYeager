from airfoil import Airfoil
from blade import Blade
import numpy as np

import matplotlib.pyplot as plt


def resistance(blade_speed):
    x = (9.43, 10.47, 18.85)
    y = (2.47, 2.73, 3.77)

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


wind_speed = knots(10)
blade_speed = rpm(140)
torque = resistance(blade_speed) / 3 # (per blade)

system = (0.945, resistance)

path = r'C:\Users\mlip814\airfoil_data\airfoil_data\ag17-il'
airfoil = Airfoil.from_folder(path, 100000, 9)

blade = Blade(airfoil, 3)
blade.design(wind_speed, torque, blade_speed)

blade_speeds = np.linspace(rpm(90), rpm(180), 10)
torques = [blade.simulate(wind_speed, blade_speed) * 3 for blade_speed in blade_speeds]
resistances = [resistance(blade_speed) for blade_speed in blade_speeds]

ax = plt.subplot(1, 2, 1)
ax.plot(blade_speeds, torques, label='Torque Output')
ax.plot(blade_speeds, resistances, label='Resistance')
ax.legend()

ax.set_xlabel('Blade Speed (rad/s)')
ax.set_ylabel('Torque (nm)')

ax.set_title('Blade Speed vs Torque for an AG17 airfoil at 10 knots')


ax = plt.subplot(1, 2, 2)
wind_speeds = np.linspace(knots(8), knots(12), 20)
results = [blade.solve(wind_speed, system)[0] for wind_speed in wind_speeds]

wind_speeds = [ms(x) for x in wind_speeds]
results = [rads(x) for x in results]

ax.plot(wind_speeds, results)

ax.set_xlabel('Wind Speed (knots)')
ax.set_ylabel('Blade Speed (rpm)')

plt.show()

plt.figure()