from airfoil import Airfoil
from blade import Blade
from utilities import *

from random import sample
from glob import glob
import numpy as np
import matplotlib.pyplot as plt

wind_speed = knots(10)
blade_speed = rpm(140)

ax = plt.subplot(1, 1, 1)
ax.set_xlabel('Wind Speed (knots)')
ax.set_ylabel('Blade Speed (rpm)')

import time
start_time = time.time()
i = 0

path = glob(r'C:\Users\mlip814\airfoil_data\airfoil_data\*')[56]
airfoil = Airfoil.from_folder(path, 100000, 9)

for n in (2, 3, 6, 12):
    blade = Blade(airfoil, n)
    torque = resistance(blade_speed) / n  # (per blade)
    blade.design(knots(10), torque, rpm(140))

    wind_speeds = np.linspace(8, 12, 20)
    results = [blade.solve(knots(wind_speed), system) for wind_speed in wind_speeds]
    blade_speeds = [rads(result[0]) for result in results]

    ax.plot(wind_speeds, blade_speeds, label=str(n))

ax.legend()

print(time.time() - start_time)
if input('Save?') != '':
    plt.savefig('image_n_blades.png')
plt.show()