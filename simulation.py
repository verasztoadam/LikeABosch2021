from gui import *
from sim_constants import SensorLocations
import numpy
import math


class Rectangle:
    """ Upper right corner: pos_tuple (x,y) """

    def __init__(self, pos_tuple, width, length, angle):
        self.width = width
        self.length = length
        self.angle = angle
        self.corner_A = pos_tuple
        self.corner_B = (pos_tuple[0] + length * math.cos(angle), pos_tuple[1] - length * math.sin(angle))
        self.corner_D = (pos_tuple[0] - width * math.sin(angle), pos_tuple[1] - width * math.cos(angle))
        self.corner_C = (self.corner_D[0] + length * math.cos(angle), self.corner_D[1] - length * math.sin(angle))


class Circle:
    def __init__(self, pos_tuple, radius):
        self.center = pos_tuple
        self.radius = radius


class Sensor:
    def __init__(self, car_pos, index):
        self.index = index
        self.direct_val = 0
        self.cross_val1 = 0
        self.cross_val2 = 0
        self.x = car_pos[0] + SensorLocations.list[index][0]
        self.y = car_pos[1] + SensorLocations.list[index][1]
        """ 
        Direct echoes: list of tuples [(x1,y1), (x2, y2)]
        Cross echo: [x1,y1,x2,y2] - (echopoint, other sensor)        
        """
        self.direct_echoes = []
        self.cross_echo1 = []
        self.cross_echo2 = []

    def update_loc(self, car_pos):
        self.x = car_pos[0] + SensorLocations.list[self.index][0]
        self.y = car_pos[1] + SensorLocations.list[self.index][1]

    def min_direct(self):
        """ Calculating travel distances for direct echoes"""
        min_dist = 1000
        if self.direct_echoes != []:
            for i, echo in enumerate(self.direct_echoes):
                dist = distance(self.x, self.y, echo[0], echo[1])
                if dist < min_dist:
                    min_dist = dist
        else:
            min_dist = 0
        self.direct_val = min_dist
        return min_dist

    def cross_vals(self):
        """ Calculating travel distances for cross-echoes """
        if self.cross_echo1:
            self.cross_val1 = distance(self.x, self.y, self.cross_echo1[0], self.cross_echo1[1]) \
                              + distance(self.cross_echo1[0], self.cross_echo1[1],
                                         self.cross_echo1[2], self.cross_echo1[3])
        else:
            self.cross_val1 = 0

        if self.cross_echo2:
            self.cross_val2 = distance(self.x, self.y, self.cross_echo2[0], self.cross_echo2[1]) \
                              + distance(self.cross_echo2[0], self.cross_echo2[1],
                                         self.cross_echo2[2], self.cross_echo2[3])
        else:
            self.cross_val2 = 0


class Model:
    """Initialize model for simulation """

    def __init__(self):
        """ Inputs """
        self.rect_list = []
        self.circle_list = []
        self.car_pos = [0, 0]
        """ Outputs """
        self.direct_list = []  # [(x1, y1),(x2, y2)] [(), ()] ...
        self.cross_list = []  # [(x1, y1),(x2, y2), (x3, y3)] [(), (), ()] ...
        self.sensor_list = []
        for i in range(6):
            self.sensor_list.append((Sensor(self.car_pos, i)))
        self.move = False

    """ Run the simulation """

    def step(self):
        self.calc_positions()
        self.calc_rays()
        self.sensor_values()

    def calc_positions(self):
        for i, sensor in enumerate(self.sensor_list):
            sensor.update_loc(self.car_pos)

    def calc_rays(self):
        """ Direct echoes: """
        self.direct_list = []
        for i, sensor in enumerate(self.sensor_list):
            for j, rect in enumerate(self.rect_list):
                direct_point = rect_solve(sensor, rect)
                """If found, append to lists"""
                if direct_point != (0, 0):
                    self.direct_list.append([(sensor.x, sensor.y), direct_point])
                    sensor.direct_echoes.append(direct_point)

            for k, circle in enumerate(self.circle_list):
                direct_point = circle_solve(sensor, circle)
                """If found, append to lists"""
                if direct_point != (0, 0):
                    self.direct_list.append([(sensor.x, sensor.y), direct_point])
                    sensor.direct_echoes.append(direct_point)

        """ Cross-echoes: """
        self.cross_list = []
        for i, sensor in enumerate(self.sensor_list):
            for j, rect in enumerate(self.rect_list):
                cross_point = cross_rectsolve(sensor, self.sensor_list[i + 1], rect)
                """If found, append to lists"""
                if cross_point != (0, 0):
                    self.cross_list.append([(sensor.x, sensor.y), cross_point,
                                            (self.sensor_list[i + 1].x, self.sensor_list[i + 1].y)])
                    sensor.cross_echo2 = [cross_point[0], cross_point[1],
                                          self.sensor_list[i + 1].x, self.sensor_list[i + 1].y]
                    self.sensor_list[i + 1].cross_echo1 = [cross_point[0], cross_point[1], sensor.x, sensor.y]

            for k, circle in enumerate(self.circle_list):
                cross_point = cross_circlesolve(sensor, self.sensor_list[i + 1], circle)
                """If found, append to lists"""
                if cross_point != (0, 0):
                    self.cross_list.append([(sensor.x, sensor.y), cross_point,
                                            (self.sensor_list[i + 1].x, self.sensor_list[i + 1].y)])
                    sensor.cross_echo2 = [cross_point[0], cross_point[1],
                                          self.sensor_list[i + 1].x, self.sensor_list[i + 1].y]
                    self.sensor_list[i + 1].cross_echo1 = [cross_point[0], cross_point[1], sensor.x, sensor.y]

    def sensor_values(self):
        for i, sensor in enumerate(self.sensor_list):
            sensor.min_direct()
            sensor.cross_vals()


def distance(x1, y1, x2, y2):
    """ Euclidean Distance: """
    d = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return d


def normal_vect(x1, y1, x2, y2):
    """ Right side normal for a vector from P1 to P2 """
    dx = x2 - x1
    dy = y2 - y1
    ret = (dy / (math.sqrt(dx ** 2 + dy ** 2)), -dx / (math.sqrt(dx ** 2 + dy ** 2)))
    return ret


def range_check(sensor, point):
    """ Is a given point in range of the sensor? """
    x1, y1 = sensor.x, sensor.y
    x2, y2 = point[0], point[1]
    if 3 < distance(x1, y1, x2, y2):
        return 0

    """ Angle of view: """
    if 0 == sensor.index:
        min_angle = math.pi / 4 - math.pi / 3
        max_angle = math.pi / 4 + math.pi / 3
    elif 5 == sensor.index:
        min_angle = -math.pi / 4 - math.pi / 3
        max_angle = -math.pi / 4 + math.pi / 3
    else:
        min_angle = math.pi / 3
        max_angle = -math.pi / 3
    dx = x2 - x1
    dy = y2 - y1
    if min_angle < math.atan2(dy, dx) < max_angle:
        return 1
    return 0


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        """ No intersection """
        return 0, 0

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def rect_solve(sensor, rectangle):
    """ Compute the direct echo point for a given rectangle:
    The upper left corner of the rect is A,
    clockwise, the other corners are B, C and D.
    Its sides are AB, BC, CD, DA respectively
    Based on the inclination angle, two sides can be sensor facing at one point in time
    """
    normal_AB = normal_vect(rectangle.corner_A[0], rectangle.corner_A[1],
                            rectangle.corner_B[0], rectangle.corner_B[1])
    normal_BC = normal_vect(rectangle.corner_B[0], rectangle.corner_B[1],
                            rectangle.corner_C[0], rectangle.corner_C[1])
    normal_CD = normal_vect(rectangle.corner_C[0], rectangle.corner_C[1],
                            rectangle.corner_D[0], rectangle.corner_D[1])
    normal_DA = normal_vect(rectangle.corner_D[0], rectangle.corner_D[1],
                            rectangle.corner_A[0], rectangle.corner_A[1])

    if 0 < rectangle.angle < math.pi / 2:
        """ AD and CD"""
        line_AD = [rectangle.corner_A, rectangle.corner_D]
        ray2AD = [(sensor.x, sensor.y), (normal_DA * 3)]
        point = line_intersection(line_AD, ray2AD)
        if point != (0, 0):
            if range_check(sensor, point):
                return point

        line_CD = [rectangle.corner_C, rectangle.corner_D]
        ray2CD = [(sensor.x, sensor.y), (normal_CD * 3)]
        point = line_intersection(line_CD, ray2CD)
        if point != (0, 0):
            if range_check(sensor, point):
                return point
        return 0, 0

    elif math.pi / 2 <= rectangle.angle < math.pi:
        """ CD and BC """
        line_CD = [rectangle.corner_C, rectangle.corner_D]
        ray2CD = [(sensor.x, sensor.y), (normal_CD * 3)]
        point = line_intersection(line_CD, ray2CD)
        if point != (0, 0):
            if range_check(sensor, point):
                return point

        line_BC = [rectangle.corner_B, rectangle.corner_C]
        ray2BC = [(sensor.x, sensor.y), (normal_BC * 3)]
        point = line_intersection(line_BC, ray2BC)
        if point != (0, 0):
            if range_check(sensor, point):
                return point
        return 0, 0

    elif math.pi <= rectangle.angle < math.pi * 3 / 2:
        """ BC and AB """
        line_BC = [rectangle.corner_B, rectangle.corner_C]
        ray2BC = [(sensor.x, sensor.y), (normal_BC * 3)]
        point = line_intersection(line_BC, ray2BC)
        if point != (0, 0):
            if range_check(sensor, point):
                return point

        line_AB = [rectangle.corner_A, rectangle.corner_B]
        ray2AB = [(sensor.x, sensor.y), (normal_AB * 3)]
        point = line_intersection(line_AB, ray2AB)
        if point != (0, 0):
            if range_check(sensor, point):
                return point
        return 0, 0
    else:
        """ AB and DA """
        line_AB = [rectangle.corner_A, rectangle.corner_B]
        ray2AB = [(sensor.x, sensor.y), (normal_AB * 3)]
        point = line_intersection(line_AB, ray2AB)
        if point != (0, 0):
            if range_check(sensor, point):
                return point

        line_AD = [rectangle.corner_A, rectangle.corner_D]
        ray2AD = [(sensor.x, sensor.y), (normal_DA * 3)]
        point = line_intersection(line_AD, ray2AD)
        if point != (0, 0):
            if range_check(sensor, point):
                return point
        return 0, 0


def circle_solve(sensor, circle):
    """ Finding the direct echo point with the given circle """
    x1, y1 = sensor.x, sensor.y
    x2, y2 = circle.center[0], circle.center[1]
    dx = x2 - x1
    dy = y2 - y1
    d = distance(x1, y1, x2, y2)
    point = (x1 + dx * circle.radius / d, y1 + dy * circle.radius / d)
    if range_check(sensor, point):
        return point
    else:
        return 0, 0
