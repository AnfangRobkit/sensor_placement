import matplotlib.pyplot as plt
import numpy as np

from sensor_class.sensor import CSensor


class CMate(CSensor):
    mate_number = 0

    # Mate is kind of combination of laser and fence
    # it used visualization method from fence, but detection method from laser
    # please that two first

    def __init__(self, name='mat', x=0, y=0, width=1, length=1):
        super(CMate, self).__init__(name, x, y)
        self.width = width
        self.length = length
        self._calc_contour()
        CMate.mate_number += 1
        self.__corner_x = [(ix * np.cos(self.heading) + iy * np.sin(self.heading)) +
                           self.x_base for (ix, iy) in zip(self.mate_x[0:4], self.mate_y[0:4])]
        self.__corner_y = [(ix * np.sin(self.heading) - iy * np.cos(self.heading)) +
                           self.y_base for (ix, iy) in zip(self.mate_x[0:4], self.mate_y[0:4])]

    def _calc_contour(self):
        self.mate_x = []
        self.mate_y = []

        self.mate_x.append(self.length / 2)
        self.mate_y.append(self.width / 2)

        self.mate_x.append(self.length / 2)
        self.mate_y.append(-self.width / 2)

        self.mate_x.append(-self.length / 2)
        self.mate_y.append(-self.width / 2)

        self.mate_x.append(-self.length / 2)
        self.mate_y.append(self.width / 2)

        self.mate_x.append(self.length / 2)
        self.mate_y.append(self.width / 2)

        self.__mate_x, self.__mate_y = CMate._interpolate(self.mate_x, self.mate_y)

    @staticmethod
    def _interpolate(x, y):
        rx, ry = [], []
        theta = 0.05
        for i in range(len(x) - 1):
            rx.extend([(1.0 - θ) * x[i] + θ * x[i + 1]  # interpolate the edges
                       for θ in np.arange(0.0, 1.0, theta)])
            ry.extend([(1.0 - θ) * y[i] + θ * y[i + 1]
                       for θ in np.arange(0.0, 1.0, theta)])
        return rx, ry

    def calc_global_contour(self):
        gx = [(ix * np.cos(self.heading) + iy * np.sin(self.heading)) +
              self.x_base for (ix, iy) in zip(self.__mate_x, self.__mate_y)]
        gy = [(ix * np.sin(self.heading) - iy * np.cos(self.heading)) +
              self.y_base for (ix, iy) in zip(self.__mate_x, self.__mate_y)]
        return gx, gy

    def detection(self, human, plt):
        mx, my = self.detect_human(human)
        if len(mx) > 1:
            self.plot_scan(plt, mx, my, color='y')

    def detect_human(self, human):
        x, y = [], []
        in_range = np.hypot(human.x - self.x_base, human.y - self.y_base) < np.hypot(self.length, self.width)
        if in_range:
            gx, gy = human.standing_area()
            for vx, vy in zip(gx, gy):
                if CMate.check(self.__corner_x, self.__corner_y, vx, vy):
                    x.append(vx)
                    y.append(vy)
            return x, y
        else:
            return x, y

    @staticmethod
    def area(x1, y1, x2, y2, x3, y3):

        return abs((x1 * (y2 - y3) +
                    x2 * (y3 - y1) +
                    x3 * (y1 - y2)) / 2.0)

    @staticmethod
    def check(corner_x, corner_y, x, y):
        x1 = corner_x[0]
        x2 = corner_x[1]
        x3 = corner_x[2]
        x4 = corner_x[3]
        y1 = corner_y[0]
        y2 = corner_y[1]
        y3 = corner_y[2]
        y4 = corner_y[3]
        A = (CMate.area(x1, y1, x2, y2, x3, y3) + CMate.area(x1, y1, x4, y4, x3, y3))
        A1 = CMate.area(x, y, x1, y1, x2, y2)
        A2 = CMate.area(x, y, x2, y2, x3, y3)
        A3 = CMate.area(x, y, x3, y3, x4, y4)
        A4 = CMate.area(x, y, x1, y1, x4, y4)
        return np.abs(A1 + A2 + A3 + A4 - A) < 0.01

    def visualization(self, fig):
        self.plot(fig)
        plt.text(-7, -7, f"Generate One Mat", fontsize=14, color='red')

    def plot(self, fig):
        fig.plot(self.x_base, self.y_base, ".b")
        gx, gy = self.calc_global_contour()
        plt.plot(gx, gy, "--b")
        plt.text(self.x_base, self.y_base, self.name)

    def plot_scan(self, plt, ox, oy, color='y'):
        x = [ox[i] for i in range(len(ox))]
        y = [oy[i] for i in range(len(ox))]

        for (ix, iy) in zip(x, y):
            plt.plot([self.x_base, ix], [self.y_base, iy], color)

    def cover_area(self):
        return self.length * self.width

    def coverage_dangerous_zone(self, coverage_dict, dangerous_zone_radius=1.5):
        in_range = np.hypot(self.x_base, self.y_base) < (np.hypot(self.length, self.width) + dangerous_zone_radius)
        bad_placement_flag = True
        if not in_range:
            return bad_placement_flag
        else:
            for (x, y) in coverage_dict:
                if CMate.check(self.__corner_x, self.__corner_y, x, y):
                    coverage_dict[(x, y)] += 1
                    bad_placement_flag = False
            return bad_placement_flag

    class Factory:
        @staticmethod
        def create(parameters): return CMate(**parameters)
