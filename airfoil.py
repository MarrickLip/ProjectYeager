from math import sin, cos, pi
from glob import glob
import os
from collections import defaultdict
import linecache
import numpy as np

class Airfoil:
	def __init__(self, reynolds, ncrit):
		self.reynolds = reynolds
		self.ncrit = ncrit

		self._alphas = None
		self._optimal_alpha = None
		self.min_alpha = None
		self.max_alpha = None

		self._lift_coefficients = None
		self._drag_coefficients = None

	def lift_coefficient(self, alpha):
		if self.min_alpha <= alpha <= self.max_alpha:
			return np.interp(alpha, self._alphas, self._lift_coefficients)
		else:
			raise ValueError('Cannot extrapolate lift coefficients.')

	def drag_coefficient(self, alpha):
		if self.min_alpha <= alpha <= self.max_alpha:
			return np.interp(alpha, self._alphas, self._drag_coefficients)
		else:
			raise ValueError('Cannot extrapolate drag coefficients.')

	def _find_optimal_alpha(self):
		step = 0.1

		alpha = np.arange(self.min_alpha, self.max_alpha + step, step)
		lift_coefficients = np.interp(alpha, self._alphas, self._lift_coefficients)
		drag_coefficients = np.interp(alpha, self._alphas, self._drag_coefficients)

		ratio = lift_coefficients / drag_coefficients
		ideal_index = np.argmax(ratio)

		self._optimal_alpha = alpha[ideal_index]

	@property
	def optimal_alpha(self):
		if self._optimal_alpha is None:
			self._find_optimal_alpha()

		return self._optimal_alpha

	def normal_component(self, alpha, angle):
		C_L = self.lift_coefficient(alpha)
		C_D = self.drag_coefficient(alpha)

		return C_L * cos(angle) + C_D * sin(angle)

	def tangential_component(self, alpha, angle):
		C_L = self.lift_coefficient(alpha)
		C_D = self.drag_coefficient(alpha)

		return C_L * sin(angle) - C_D * cos(angle)

	@classmethod
	def from_folder(cls, path, reynolds, ncrit):
		txt_paths = glob(os.path.join(path, '*.txt'))
		csv_paths = glob(os.path.join(path, '*.csv'))

		assert(len(txt_paths) == 1 and len(csv_paths) > 0)

		traces_by_ncrit = defaultdict(dict)
		for csv_path in csv_paths:
			reynolds_line = linecache.getline(csv_path, 4).strip()
			reynolds_value = float(reynolds_line.split(',')[1])

			ncrit_line = linecache.getline(csv_path, 5).strip()
			ncrit_value = float(ncrit_line.split(',')[1])

			traces_by_ncrit[ncrit_value][reynolds_value] = csv_path

		if ncrit not in traces_by_ncrit:
			raise FileNotFoundError('Cannot find files for ncrit of ' + str(ncrit))

		traces = traces_by_ncrit[ncrit]

		files = ()
		weights = ()
		if reynolds in traces:
			files = (traces[reynolds],)
			weights = (1,)
		else:
			closest_above = min(r for r in traces if r > reynolds)
			closest_below = max(r for r in traces if r < reynolds)

			norm_dist = (reynolds - closest_below) / (closest_above - closest_below)
			weights = (1 - norm_dist, norm_dist)

			files = (traces[closest_below], traces[closest_above])

		alphas = []
		lift_coefficients = []
		drag_coefficients = []
		for file in files:
			data = np.genfromtxt(file, skip_header=11, usecols=(0, 1, 2), delimiter=',')

			alpha = data[:, 0] * (pi / 180)
			alphas.append(alpha)

			lift_coefficients.append(data[:, 1])
			drag_coefficients.append(data[:, 2])

		airfoil = cls(reynolds, ncrit)

		if len(files) == 1:
			airfoil._alphas = alphas[0]
			airfoil._lift_coefficients = lift_coefficients[0]
			airfoil._drag_coefficients = drag_coefficients[0]
		else:
			assert(alphas[0] == alphas[1])
			airfoil._alphas = alphas[0]

			part1 = lift_coefficients[0] * weights[0]
			part2 = lift_coefficients[1] * weights[1]
			lift_coefficients = part1 + part2
			airfoil._lift_coefficients = lift_coefficients

			part1 = drag_coefficients[0] * weights[0]
			part2 = drag_coefficients[1] * weights[1]
			drag_coefficients = part1 + part2
			airfoil._drag_coefficients = drag_coefficients

		airfoil.min_alpha = min(airfoil._alphas)
		airfoil.max_alpha = max(airfoil._alphas)

		return airfoil