from airfoil import Airfoil
from main import WindTurbine
from math import pi

from glob import glob


import time
s = time.time()
i = 1
folders = glob('/Users/Marrick/airfoil_data/*')
for folder in folders:
	try:
		print(i, len(folders))
		i += 1

		airfoil = Airfoil.from_folder(folder, 100000, 5)

		def rpm_to_rads(rpm):
			return rpm * 2 * pi / 60

		torque = 3.25
		blade_speed = rpm_to_rads(140)
		wind_speed = 5

		turbine = WindTurbine(3, airfoil)
		blade_design = turbine.solve(wind_speed, torque, blade_speed)
	except:
		print('FAILED',i)
print('Completed in:', time.time() - s)