from airfoil import Airfoil
from blade import Blade
from utilities import *

from random import sample
from glob import glob
import numpy as np
import matplotlib.pyplot as plt

wind_speed = knots(10)
blade_speed = rpm(140)

ax1 = plt.subplot(2, 1, 1)
ax1.set_xlabel('Wind Speed (knots)')
ax1.set_ylabel('Blade Speed (rpm)')

ax2 = plt.subplot(2, 1, 2)
ax2.set_xlabel('Wind Speed (knots)')
ax2.set_ylabel('Power (W)')

import time
start_time = time.time()
i = 0

paths = glob(r'C:\Users\mlip814\airfoil_data\airfoil_data\*')
for path in sample(paths, 10):
    try:
        airfoil = Airfoil.from_folder(path, 100000, 9)

        blade = Blade(airfoil, 3)
        torque = resistance(blade_speed) / 3  # (per blade)
        blade.design(knots(10), torque, rpm(140))

        wind_speeds = np.linspace(8, 12, 5)
        results = [blade.solve(knots(wind_speed), system) for wind_speed in wind_speeds]

        blade_speeds = [rads(result[0]) for result in results]
        #torques = [result[1] for result in results]
        powers = [result[0] * result[1] for result in results]

        for a, b in zip(blade_speeds, powers):
            print(a, b)

        print('*'*10)

        ax1.plot(wind_speeds, blade_speeds)
        ax2.plot(wind_speeds, powers)
    except:
        pass

    i += 1
    print(i, len(paths))

print(time.time() - start_time)
if input('Save?') != '':
    plt.savefig('image.png')
plt.show()