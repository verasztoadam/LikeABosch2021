from gui import *
from sim_constants import SensorLocations
import math


class Rectangle:
    """ Upper left corner: pos_tuple (x,y) """

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
        self.cross_val_l = 0
        self.cross_val_r = 0
        self.x = car_pos[0] + SensorLocations.list[index][0]
        self.y = car_pos[1] + SensorLocations.list[index][1]
        self.pos = (self.x, self.y)
        """ 
        Direct echoes: list of tuples [(x1,y1), (x2, y2)]
        Cross echo: [x1,y1,x2,y2] - (echopoint, other sensor)        
        """
        self.direct_echoes = []
        self.cross_echo_l = []
        self.cross_echo_r = []

    def update_loc(self, car_pos):
        self.x = car_pos[0] + SensorLocations.list[self.index][0]
        self.y = car_pos[1] + SensorLocations.list[self.index][1]
        self.pos = (self.x, self.y)

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
        if self.cross_echo_l:
            self.cross_val_l = (distance(self.x, self.y, self.cross_echo_l[0], self.cross_echo_l[1]) \
                               + distance(self.cross_echo_l[0], self.cross_echo_l[1],
                                          self.cross_echo_l[2], self.cross_echo_l[3])) / 2
        else:
            self.cross_val_l = 0

        if self.cross_echo_r:
            self.cross_val_r = (distance(self.x, self.y, self.cross_echo_r[0], self.cross_echo_r[1]) \
                               + distance(self.cross_echo_r[0], self.cross_echo_r[1],
                                          self.cross_echo_r[2], self.cross_echo_r[3]))/2
        else:
            self.cross_val_r = 0


class Model:
    """Initialize model for simulation """

    def __init__(self):
        """ Inputs """
        self.rect_list = []
        self.circle_list = []
        self.car_pos = (0, 0)
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
        """ Updating sensor coordinates """
        for i, sensor in enumerate(self.sensor_list):
            sensor.update_loc(self.car_pos)

    def calc_rays(self):
        """ Direct echoes: """
        self.direct_list = []
        for sensor in self.sensor_list:
            sensor.cross_echo_l.clear()
            sensor.cross_echo_r.clear()
            sensor.direct_echoes.clear()

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
            if i == 5:
                break
            """For rectangles"""
            for j, rect in enumerate(self.rect_list):
                cross_point = cross_rectsolve(sensor, self.sensor_list[i + 1], rect)
                """If found, append to lists"""
                if cross_point != (0, 0):
                    self.cross_list.append([(sensor.x, sensor.y), cross_point,
                                            (self.sensor_list[i + 1].x, self.sensor_list[i + 1].y)])
                    sensor.cross_echo_r = [cross_point[0], cross_point[1],
                                           self.sensor_list[i + 1].x, self.sensor_list[i + 1].y]
                    self.sensor_list[i + 1].cross_echo_l = [cross_point[0], cross_point[1], sensor.x, sensor.y]

            """ For circles: """
            for k, circle in enumerate(self.circle_list):
                cross_point = cross_circlesolve(sensor, self.sensor_list[i + 1], circle)
                """If found, append to lists"""
                if cross_point != (0, 0):
                    self.cross_list.append([(sensor.x, sensor.y), cross_point,
                                            (self.sensor_list[i + 1].x, self.sensor_list[i + 1].y)])
                    sensor.cross_echo_r = [cross_point[0], cross_point[1],
                                           self.sensor_list[i + 1].x, self.sensor_list[i + 1].y]
                    self.sensor_list[i + 1].cross_echo_l = [cross_point[0], cross_point[1], sensor.x, sensor.y]

    def sensor_values(self):
        for i, sensor in enumerate(self.sensor_list):
            sensor.min_direct()
            sensor.cross_vals()


def distance(x1, y1, x2, y2):
    """ Euclidean Distance: """
    d = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return d


def distance_p(point1, point2):
    return distance(point1[0], point1[1], point2[0], point2[1])


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
        min_angle = -math.pi / 3
        max_angle = math.pi / 3
    dx = x2 - x1
    dy = y2 - y1
    if min_angle < math.atan2(dy, dx) < max_angle:
        return 1
    return 0


def line_intersection(line1, line2):
    """ Computing the intersection of two lines """
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

    if 0 <= rectangle.angle < math.pi / 2:
        """ AD and CD"""
        line_AD = [rectangle.corner_A, rectangle.corner_D]
        ray2AD = [(sensor.x, sensor.y), (sensor.x + normal_DA[0] * 3, sensor.y + normal_DA[1] * 3)]
        point = line_intersection(line_AD, ray2AD)
        if point != (0, 0):
            if range_check(sensor, point):
                point = (round(point[0], 10), round(point[1], 10))
                line_AD = [(round(line_AD[0][0], 10), round(line_AD[0][1], 10)),
                           (round(line_AD[1][0], 10), round(line_AD[1][1], 10))]
                if ((line_AD[0][0] >= point[0] >= line_AD[1][0]) or (line_AD[0][0] <= point[0] <= line_AD[1][0])) \
                        and ((line_AD[0][1] >= point[1] >= line_AD[1][1]) or (
                        line_AD[0][1] <= point[1] <= line_AD[1][1])):
                    return point

        line_CD = [rectangle.corner_C, rectangle.corner_D]
        ray2CD = [(sensor.x, sensor.y), (sensor.x + normal_CD[0] * 3, sensor.y + normal_CD[1] * 3)]
        point = line_intersection(line_CD, ray2CD)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_CD = [(round(line_CD[0][0], 10), round(line_CD[0][1], 10)),
                       (round(line_CD[1][0], 10), round(line_CD[1][1], 10))]
            if range_check(sensor, point):
                if ((line_CD[0][0] >= point[0] >= line_CD[1][0]) or (line_CD[0][0] <= point[0] <= line_CD[1][0])) \
                        and ((line_CD[0][1] >= point[1] >= line_CD[1][1]) or (
                        line_CD[0][1] <= point[1] <= line_CD[1][1])):
                    return point
        return 0, 0

    elif math.pi / 2 <= rectangle.angle < math.pi:
        """ CD and BC """
        line_CD = [rectangle.corner_C, rectangle.corner_D]
        ray2CD = [(sensor.x, sensor.y), (sensor.x + normal_CD[0] * 3, sensor.y + normal_CD[1] * 3)]
        point = line_intersection(line_CD, ray2CD)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_CD = [(round(line_CD[0][0], 10), round(line_CD[0][1], 10)),
                       (round(line_CD[1][0], 10), round(line_CD[1][1], 10))]
            if range_check(sensor, point):
                if ((line_CD[0][0] >= point[0] >= line_CD[1][0]) or (line_CD[0][0] <= point[0] <= line_CD[1][0])) \
                        and ((line_CD[0][1] >= point[1] >= line_CD[1][1]) or (
                        line_CD[0][1] <= point[1] <= line_CD[1][1])):
                    return point

        line_BC = [rectangle.corner_B, rectangle.corner_C]
        ray2BC = [(sensor.x, sensor.y), (sensor.x + normal_BC[0] * 3, sensor.y + normal_BC[1] * 3)]
        point = line_intersection(line_BC, ray2BC)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_BC = [(round(line_BC[0][0], 10), round(line_BC[0][1], 10)),
                       (round(line_BC[1][0], 10), round(line_BC[1][1], 10))]
            if range_check(sensor, point):
                if ((line_BC[0][0] >= point[0] >= line_BC[1][0]) or (line_BC[0][0] <= point[0] <= line_BC[1][0])) \
                        and ((line_BC[0][1] >= point[1] >= line_BC[1][1]) or (
                        line_BC[0][1] <= point[1] <= line_BC[1][1])):
                    return point
        return 0, 0

    elif math.pi <= rectangle.angle < math.pi * 3 / 2:
        """ BC and AB """
        line_BC = [rectangle.corner_B, rectangle.corner_C]
        ray2BC = [(sensor.x, sensor.y), (sensor.x + normal_BC[0] * 3, sensor.y + normal_BC[1] * 3)]
        point = line_intersection(line_BC, ray2BC)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_BC = [(round(line_BC[0][0], 10), round(line_BC[0][1], 10)),
                       (round(line_BC[1][0], 10), round(line_BC[1][1], 10))]
            if range_check(sensor, point):
                if ((line_BC[0][0] >= point[0] >= line_BC[1][0]) or (line_BC[0][0] <= point[0] <= line_BC[1][0])) \
                        and ((line_BC[0][1] >= point[1] >= line_BC[1][1]) or (
                        line_BC[0][1] <= point[1] <= line_BC[1][1])):
                    return point

        line_AB = [rectangle.corner_A, rectangle.corner_B]
        ray2AB = [(sensor.x, sensor.y), (sensor.x + normal_AB[0] * 3, sensor.y + normal_AB[1] * 3)]
        point = line_intersection(line_AB, ray2AB)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_AB = [(round(line_AB[0][0], 10), round(line_AB[0][1], 10)),
                       (round(line_AB[1][0], 10), round(line_AB[1][1], 10))]
            if range_check(sensor, point):
                if ((line_AB[0][0] >= point[0] >= line_AB[1][0]) or (line_AB[0][0] <= point[0] <= line_AB[1][0])) \
                        and ((line_AB[0][1] >= point[1] >= line_AB[1][1]) or (
                        line_AB[0][1] <= point[1] <= line_AB[1][1])):
                    return point
        return 0, 0
    else:
        """ AB and DA """
        line_AB = [rectangle.corner_A, rectangle.corner_B]
        ray2AB = [(sensor.x, sensor.y), (sensor.x + normal_AB[0] * 3, sensor.y + normal_AB[1] * 3)]
        point = line_intersection(line_AB, ray2AB)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_AB = [(round(line_AB[0][0], 10), round(line_AB[0][1], 10)),
                       (round(line_AB[1][0], 10), round(line_AB[1][1], 10))]
            if range_check(sensor, point):
                if ((line_AB[0][0] >= point[0] >= line_AB[1][0]) or (line_AB[0][0] <= point[0] <= line_AB[1][0])) \
                        and ((line_AB[0][1] >= point[1] >= line_AB[1][1]) or (
                        line_AB[0][1] <= point[1] <= line_AB[1][1])):
                    return point

        line_AD = [rectangle.corner_A, rectangle.corner_D]
        ray2AD = [(sensor.x, sensor.y), (sensor.x + normal_DA[0] * 3, sensor.y + normal_DA[1] * 3)]
        point = line_intersection(line_AD, ray2AD)
        if point != (0, 0):
            point = (round(point[0], 10), round(point[1], 10))
            line_AD = [(round(line_AD[0][0], 10), round(line_AD[0][1], 10)),
                       (round(line_AD[1][0], 10), round(line_AD[1][1], 10))]
            if range_check(sensor, point):
                if ((line_AD[0][0] >= point[0] >= line_AD[1][0]) or (line_AD[0][0] <= point[0] <= line_AD[1][0])) \
                        and ((line_AD[0][1] >= point[1] >= line_AD[1][1]) or (
                        line_AD[0][1] <= point[1] <= line_AD[1][1])):
                    return point
        return 0, 0


def circle_solve(sensor, circle):
    """ Finding the direct echo point with the given circle """
    x1, y1 = sensor.x, sensor.y
    x2, y2 = circle.center[0], circle.center[1]
    dx = x2 - x1
    dy = y2 - y1
    d = distance(x1, y1, x2, y2)
    point = (x1 + dx * (1 - circle.radius / d), y1 + dy * (1 - circle.radius / d))
    if range_check(sensor, point):
        return point
    else:
        return 0, 0


def mirror_point(point, line):
    """ Mirroring a point to a P1(x1,y1) - P2(x2, y2) line"""
    x1, y1 = line[0][0], line[0][1]
    x2, y2 = line[1][0], line[1][1]
    normal = normal_vect(x1, y1, x2, y2)
    """ Projection: """
    ray = [(point[0], point[1]), (point[0] + normal[0] * 10, point[1] + normal[1] * 10)]
    inter_point = line_intersection(ray, line)
    if inter_point != (0, 0):
        d = distance_p(point, inter_point)
        mirrored_point = (point[0] + normal[0] * d * 2, point[1] + normal[1] * d * 2)
        return mirrored_point
    else:
        return 0, 0


def cross_rectsolve(sensor1, sensor2, rectangle):
    """ Cross-echo point of two adjacent sensors on a rectangle """
    sensor_p1 = (sensor1.x, sensor1.y)
    sensor_p2 = (sensor2.x, sensor2.y)

    if 0 <= rectangle.angle < math.pi / 2:
        """ AD and CD"""
        line_AD = [rectangle.corner_D, rectangle.corner_A]
        mirror_s1 = mirror_point(sensor_p1, line_AD)
        mirror_s2 = mirror_point(sensor_p2, line_AD)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_AD = [(round(line_AD[0][0], 10), round(line_AD[0][1], 10)),
                           (round(line_AD[1][0], 10), round(line_AD[1][1], 10))]
                if ((line_AD[0][0] >= cross_echo_p[0] >= line_AD[1][0]) or (
                        line_AD[0][0] <= cross_echo_p[0] <= line_AD[1][0])) \
                        and ((line_AD[0][1] >= cross_echo_p[1] >= line_AD[1][1]) or (
                        line_AD[0][1] <= cross_echo_p[1] <= line_AD[1][1])):
                    return cross_echo_p

        line_CD = [rectangle.corner_C, rectangle.corner_D]
        mirror_s1 = mirror_point(sensor_p1, line_CD)
        mirror_s2 = mirror_point(sensor_p2, line_CD)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_CD = [(round(line_CD[0][0], 10), round(line_CD[0][1], 10)),
                           (round(line_CD[1][0], 10), round(line_CD[1][1], 10))]
                if ((line_CD[0][0] >= cross_echo_p[0] >= line_CD[1][0]) or (
                        line_CD[0][0] <= cross_echo_p[0] <= line_CD[1][0])) \
                        and ((line_CD[0][1] >= cross_echo_p[1] >= line_CD[1][1]) or (
                        line_CD[0][1] <= cross_echo_p[1] <= line_CD[1][1])):
                    return cross_echo_p
        return 0, 0

    elif math.pi / 2 <= rectangle.angle < math.pi:
        """ CD and BC """
        line_CD = [rectangle.corner_C, rectangle.corner_D]
        mirror_s1 = mirror_point(sensor_p1, line_CD)
        mirror_s2 = mirror_point(sensor_p2, line_CD)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_CD = [(round(line_CD[0][0], 10), round(line_CD[0][1], 10)),
                           (round(line_CD[1][0], 10), round(line_CD[1][1], 10))]
                if ((line_CD[0][0] >= cross_echo_p[0] >= line_CD[1][0]) or (
                        line_CD[0][0] <= cross_echo_p[0] <= line_CD[1][0])) \
                        and ((line_CD[0][1] >= cross_echo_p[1] >= line_CD[1][1]) or (
                        line_CD[0][1] <= cross_echo_p[1] <= line_CD[1][1])):
                    return cross_echo_p

        line_BC = [rectangle.corner_B, rectangle.corner_C]
        mirror_s1 = mirror_point(sensor_p1, line_BC)
        mirror_s2 = mirror_point(sensor_p2, line_BC)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_BC = [(round(line_BC[0][0], 10), round(line_BC[0][1], 10)),
                           (round(line_BC[1][0], 10), round(line_BC[1][1], 10))]
                if ((line_BC[0][0] >= cross_echo_p[0] >= line_BC[1][0]) or (
                        line_BC[0][0] <= cross_echo_p[0] <= line_BC[1][0])) \
                        and ((line_BC[0][1] >= cross_echo_p[1] >= line_BC[1][1]) or (
                        line_BC[0][1] <= cross_echo_p[1] <= line_BC[1][1])):
                    return cross_echo_p
        return 0, 0

    elif math.pi <= rectangle.angle < math.pi * 3 / 2:
        """ BC and AB """
        line_BC = [rectangle.corner_B, rectangle.corner_C]
        mirror_s1 = mirror_point(sensor_p1, line_BC)
        mirror_s2 = mirror_point(sensor_p2, line_BC)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_BC = [(round(line_BC[0][0], 10), round(line_BC[0][1], 10)),
                           (round(line_BC[1][0], 10), round(line_BC[1][1], 10))]
                if ((line_BC[0][0] >= cross_echo_p[0] >= line_BC[1][0]) or (
                        line_BC[0][0] <= cross_echo_p[0] <= line_BC[1][0])) \
                        and ((line_BC[0][1] >= cross_echo_p[1] >= line_BC[1][1]) or (
                        line_BC[0][1] <= cross_echo_p[1] <= line_BC[1][1])):
                    return cross_echo_p

        line_AB = [rectangle.corner_A, rectangle.corner_B]
        mirror_s1 = mirror_point(sensor_p1, line_AB)
        mirror_s2 = mirror_point(sensor_p2, line_AB)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_AB = [(round(line_AB[0][0], 10), round(line_AB[0][1], 10)),
                           (round(line_AB[1][0], 10), round(line_AB[1][1], 10))]
                if ((line_AB[0][0] >= cross_echo_p[0] >= line_AB[1][0]) or (
                        line_AB[0][0] <= cross_echo_p[0] <= line_AB[1][0])) \
                        and ((line_AB[0][1] >= cross_echo_p[1] >= line_AB[1][1]) or (
                        line_AB[0][1] <= cross_echo_p[1] <= line_AB[1][1])):
                    return cross_echo_p
        return 0, 0

    else:
        """ AB and DA """
        line_AB = [rectangle.corner_A, rectangle.corner_B]
        mirror_s1 = mirror_point(sensor_p1, line_AB)
        mirror_s2 = mirror_point(sensor_p2, line_AB)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_AB = [(round(line_AB[0][0], 10), round(line_AB[0][1], 10)),
                           (round(line_AB[1][0], 10), round(line_AB[1][1], 10))]
                if ((line_AB[0][0] >= cross_echo_p[0] >= line_AB[1][0]) or (
                        line_AB[0][0] <= cross_echo_p[0] <= line_AB[1][0])) \
                        and ((line_AB[0][1] >= cross_echo_p[1] >= line_AB[1][1]) or (
                        line_AB[0][1] <= cross_echo_p[1] <= line_AB[1][1])):
                    return cross_echo_p

        line_AD = [rectangle.corner_D, rectangle.corner_A]
        mirror_s1 = mirror_point(sensor_p1, line_AD)
        mirror_s2 = mirror_point(sensor_p2, line_AD)
        if (mirror_s1 != (0, 0)) & (mirror_s2 != (0, 0)):
            cross_echo_p = line_intersection((sensor_p1, mirror_s2), (sensor_p2, mirror_s1))
            if range_check(sensor1, cross_echo_p) & range_check(sensor2, cross_echo_p):
                cross_echo_p = (round(cross_echo_p[0], 10), round(cross_echo_p[1], 10))
                line_AD = [(round(line_AD[0][0], 10), round(line_AD[0][1], 10)),
                           (round(line_AD[1][0], 10), round(line_AD[1][1], 10))]
                if ((line_AD[0][0] >= cross_echo_p[0] >= line_AD[1][0]) or (
                        line_AD[0][0] <= cross_echo_p[0] <= line_AD[1][0])) \
                        and ((line_AD[0][1] >= cross_echo_p[1] >= line_AD[1][1]) or (
                        line_AD[0][1] <= cross_echo_p[1] <= line_AD[1][1])):
                    return cross_echo_p
        return 0, 0


def cross_circlesolve(sensor1: Sensor, sensor2: Sensor, circle: Circle):
    """Searching fot the cross echo point in the section between the lines connecting the sensors with the center of
     the circle"""
    v1 = (circle.center[0] - sensor1.x, circle.center[1] - sensor1.y)
    v2 = (circle.center[0] - sensor2.x, circle.center[1] - sensor2.y)
    d1 = distance(circle.center[0], circle.center[1], sensor1.x, sensor1.y)
    d2 = distance(circle.center[0], circle.center[1], sensor2.x, sensor2.y)
    fi1 = math.atan2(v1[1], v1[0])
    fi2 = math.atan2(v2[1], v2[0])

    if fi1 < 0:
        fi1 += math.pi * 2
    if fi2 < 0:
        fi2 += math.pi * 2

    min_angle = fi2
    max_angle = fi1
    if fi1 < fi2:
        min_angle = fi1
        max_angle = fi2

    step_size = math.pi / 18000
    current_angle = min_angle
    min_point = (circle.center[0] - circle.radius * math.cos(current_angle),
                 circle.center[1] - circle.radius * math.sin(current_angle))
    min_dist = distance(min_point[0], min_point[1], sensor1.x, sensor1.y) + \
               distance(min_point[0], min_point[1], sensor2.x, sensor2.y)

    while current_angle <= max_angle:
        current_angle += step_size
        current_point = (circle.center[0] - circle.radius * math.cos(current_angle),
                         circle.center[1] - circle.radius * math.sin(current_angle))
        current_dist = distance(current_point[0], current_point[1], sensor1.x, sensor1.y) + \
                       distance(current_point[0], current_point[1], sensor2.x, sensor2.y)

        if current_dist < min_dist:
            min_dist = current_dist
            min_point = current_point

        if range_check(sensor1, min_point) & range_check(sensor2, min_point):
            return min_point
    return 0, 0
