from math import pi, sqrt, sin, cos, atan2, acos, exp, pow, atan
import numpy as np

rho_air = 1.225


class WindTurbine:
	def __init__(self, blade_count, airfoil):
		self.blade_count = blade_count
		self.airfoil = airfoil

	def solve(self, wind_speed, torque, blade_speed):
		target_torque = torque / self.blade_count
		blade = BladeDesign(self.airfoil, self.blade_count, wind_speed, target_torque, blade_speed)

		#temp
		blade._solve()

		return blade

class BladeDesign:
	def __init__(self, airfoil, blade_count, wind_speed, target_torque, blade_speed):
		self.airfoil = airfoil

		self.blade_count = blade_count
		self.wind_speed = wind_speed
		self.target_torque = target_torque
		self.blade_speed = blade_speed

	def _solve(self):
		tol = 0.5 / 100
		n_elements = 30

		target_power = self.target_torque * self.blade_speed
		C_P = 0.5  # initial guess
		radius = sqrt((2 * target_power) / (C_P * rho_air * pi * (self.wind_speed ** 3)))

		converged = False
		while not converged:
			elements = []
			boundaries = np.linspace(0, radius, n_elements + 1)
			for r1, r2 in zip(boundaries[:-1], boundaries[1:]):
				mean_radius = (r1 + r2) / 2
				local_ratio = (mean_radius * self.blade_speed) / self.wind_speed

				element = BladeElement(r1, r2, radius, self.blade_count, local_ratio, self.wind_speed, self.airfoil)
				elements.append(element)

			torque = sum(element.torque for element in elements)

			if (1 - tol) <= (torque / self.target_torque) <= (1 + tol):
				converged = True
			else:
				new_radius = radius * (self.target_torque / torque)
				radius = (0.8 * new_radius) + (0.2 * radius)


class BladeElement:
	def __init__(self, r1, r2, max_radius, blade_count, local_ratio, wind_speed, airfoil):
		self.r1 = r1
		self.r2 = r2
		self.max_radius = max_radius
		self.radius = (r1 + r2) / 2

		self.blade_count = blade_count

		self.local_ratio = local_ratio
		self.wind_speed = wind_speed
		self.airfoil = airfoil

		self._solved = False
		self._axial_induction = None
		self._angular_induction = None
		self._chord_length = None
		self._solidity = None
		self._alpha = None
		self._blade_angle = None
		self._wind_angle = None
		self._tangential_pressure = None
		self._torque = None
		self._power_coefficient = None

	def _solve(self):
		if not self._solved:
			self._solve_geometry()
			self._solve_torque()

			self._solved = True

	def _solve_geometry(self):
		tol = 0.5 / 100

		chord_length = None
		solidity = None
		wind_angle = None

		axial_induction = 1/3
		angular_induction = 5

		alpha = self.airfoil.optimal_alpha
		ideal_alpha = alpha

		blade_angle = atan2(2, 3 * self.local_ratio) - ideal_alpha

		converged = False
		while not converged:
			old = (axial_induction, angular_induction)

			wind_angle = atan((1 - axial_induction) / (self.local_ratio * (1 + angular_induction)))
			alpha = wind_angle - blade_angle

			C_L = self.airfoil.lift_coefficient(alpha)
			C_n = self.airfoil.normal_component(alpha, wind_angle)
			C_t = self.airfoil.tangential_component(alpha, wind_angle)

			chord_length = (8 * pi * self.radius) * (1 - cos(wind_angle)) / (self.blade_count * C_L)
			solidity = (self.blade_count * chord_length) / (2 * pi * self.radius)

			prandtl_f = (self.blade_count * (self.max_radius - self.radius)) / (2 * self.radius * sin(wind_angle))
			prandtl_F = (2 / pi) * acos(exp(-prandtl_f))

			axial_induction = (solidity * C_n) / ((4 * prandtl_F * pow(sin(wind_angle), 2)) + (solidity * C_n))
			angular_induction = (solidity * C_t) / ((4 * prandtl_F * sin(wind_angle) * cos(wind_angle)) - (solidity * C_t))

			new = (axial_induction, angular_induction)
			pct_change = (abs(old[i] - new[i]) / new[i] for i in (0, 1))
			if max(pct_change) <= tol:
				converged = True

		self._axial_induction = axial_induction
		self._angular_induction = angular_induction
		self._chord_length = chord_length
		self._solidity = solidity
		self._alpha = alpha
		self._blade_angle = blade_angle
		self._wind_angle = wind_angle

	def _solve_torque(self):
		C_L = self.airfoil.lift_coefficient(self._alpha)
		C_D = self.airfoil.lift_coefficient(self._alpha)

		term_1 = 0.5 * rho_air * self._chord_length
		term_2 = pow(self.wind_speed, 2) * pow(1 - self._axial_induction, 2) / pow(sin(self._wind_angle), 2)
		term_3 = (C_L * sin(self._wind_angle)) - (C_D * cos(self._wind_angle))

		tangential_pressure = term_1 * term_2 * term_3
		self._tangential_pressure = tangential_pressure
		self._torque = tangential_pressure * (self.r2 - self.r1)

		area = pi * (pow(self.r2, 2) - pow(self.r1, 2))
		total_power = 0.5 * rho_air * area * pow(self.wind_speed, 3)

		blade_speed = self.local_ratio * self.wind_speed / self.radius
		power_extracted = self._torque * blade_speed

		self._power_coefficient = power_extracted / total_power

	def __getattr__(self, item):
		solved_values = ['axial_induction', 'angular_induction',
		                 'chord_length', 'solidity', 'alpha',
		                 'blade_angle', 'wind_angle', 'tangential_pressure',
		                 'torque', 'power_coefficient',
		                 ]

		if item in solved_values:
			self._solve()
			return self.__getattribute__('_' + item)
		else:
			raise ValueError(item)