from math import pi, sin, cos, atan2, acos, exp, pow
rho_air = 1.225


class BladeElement:
    def __init__(self, r1, r2, max_radius, blade_count, blade_speed, wind_speed, airfoil):
        self.r1 = r1
        self.r2 = r2
        self.max_radius = max_radius
        self.radius = (r1 + r2) / 2

        self.blade_count = blade_count
        self.blade_speed = blade_speed
        self.wind_speed = wind_speed

        self.airfoil = airfoil

        self.solved = False
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

    @property
    def local_ratio(self):
        return (self.blade_speed * self.radius) / self.wind_speed

    def simulate(self, wind_speed, blade_speed):
        self.wind_speed = wind_speed
        self.blade_speed = blade_speed

        self.solved = False
        self._solve()

    def _solve(self):
        if not self.solved:
            self._solve_geometry()
            self._solve_torque()

            self.solved = True

    def _solve_geometry(self):
        alpha = self.airfoil.optimal_alpha
        blade_angle = atan2(2, 3 * self.local_ratio) - alpha

        wind_angle = (2/3) * atan2(1, self.local_ratio)

        C_L = self.airfoil.lift_coefficient(alpha)
        C_n = self.airfoil.normal_component(alpha, wind_angle)
        C_t = self.airfoil.tangential_component(alpha, wind_angle)

        chord_length = (8 * pi * self.radius) * (1 - cos(wind_angle)) / (self.blade_count * C_L)
        solidity = (self.blade_count * chord_length) / (2 * pi * self.radius)

        prandtl_f = (self.blade_count * (self.max_radius - self.radius)) / (2 * self.radius * sin(wind_angle))
        prandtl_F = (2 / pi) * acos(exp(-prandtl_f))

        axial_induction = (solidity * C_n) / ((4 * prandtl_F * pow(sin(wind_angle), 2)) + (solidity * C_n))
        angular_induction = (solidity * C_t) / ((4 * prandtl_F * sin(wind_angle) * cos(wind_angle)) - (solidity * C_t))

        self._axial_induction = axial_induction
        self._angular_induction = angular_induction
        self._chord_length = chord_length
        self._solidity = solidity
        self._alpha = alpha
        self._blade_angle = blade_angle
        self._wind_angle = wind_angle

    def _solve_torque(self):
        term_1 = 0.5 * rho_air * self._chord_length
        term_2 = pow(self.wind_speed, 2) * pow(1 - self._axial_induction, 2) / pow(sin(self._wind_angle), 2)
        term_3 = self.airfoil.tangential_component(self._alpha, self._wind_angle)

        tangential_pressure = term_1 * term_2 * term_3
        self._tangential_pressure = tangential_pressure
        self._torque = tangential_pressure * (self.r2 - self.r1) * self.radius

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