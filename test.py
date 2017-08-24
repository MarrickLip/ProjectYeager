from airfoil import Airfoil
from main import WindTurbine
from math import pi

folder = '/Users/Marrick/airfoil_data/naca22112-jf'
airfoil = Airfoil.from_folder(folder, 100000, 5)

def rpm_to_rads(rpm):
	return rpm * 2 * pi / 60

torque = 3.25
blade_speed = rpm_to_rads(140)
wind_speed = 5

turbine = WindTurbine(3, airfoil)
blade_design = turbine.solve(wind_speed, torque, blade_speed)