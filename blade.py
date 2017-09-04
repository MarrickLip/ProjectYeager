from math import sqrt, pi
from blade_element import BladeElement
import numpy as np
rho_air = 1.225


class Blade:
    def __init__(self, airfoil, blade_count):
        self.airfoil = airfoil
        self.blade_count = blade_count

        self.radius = None
        self.torque = None
        self.power_coefficient = None
        self.elements = None

    def design(self, wind_speed, target_torque, blade_speed):
        tol = 0.05 / 100
        n_elements = 30

        target_power = target_torque * blade_speed
        C_P = 0.45  # initial guess
        radius = sqrt((2 * target_power * self.blade_count) / (C_P * rho_air * pi * (wind_speed ** 3)))

        converged = False
        elements = None
        torque = None
        while not converged:
            elements = []
            boundaries = np.linspace(0, radius, n_elements + 1)
            for r1, r2 in zip(boundaries[:-1], boundaries[1:]):
                element = BladeElement(r1, r2, radius, self.blade_count, blade_speed, wind_speed, self.airfoil)
                elements.append(element)

            torque = sum(element.torque for element in elements)
            if (1 - tol) <= (torque / target_torque) <= (1 + tol):
                converged = True
            else:
                # torque increases with the square-ish of radius
                radius = radius * sqrt(target_torque / torque)

        self.torque = torque
        self.elements = elements
        self.radius = radius
        self.power_coefficient = 12

    def simulate(self, wind_speed, blade_speed):
        torque = 0
        for element in self.elements:
            element.simulate(wind_speed, blade_speed)
            torque += element.torque
        return torque

    def solve(self, wind_speed, system):
        blade_speed, resistance = system
        step = 0.01
        torque = None
        converged = False
        while not converged:
            torque = self.simulate(wind_speed, blade_speed)
            min_torque = resistance(blade_speed) / self.blade_count
            if torque < min_torque:
                self.torque = torque
                converged = True
            else:
                excess_pct = 100 * (torque - min_torque) / min_torque
                step_size = step * (excess_pct + 1)

                blade_speed += min(step_size, 100 * step)

        return blade_speed, torque

