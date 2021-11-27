from gui import*
from sim_constants import SensorLocations
import numpy
import math



class Rectangle:
    """ Upper right corner: pos_tuple (x,y) """
    def __init__(self, pos_tuple, width, length, angle):
        self.upleft_corner = pos_tuple
        self.width = width
        self.length = length
        self.angle = angle

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
        min = 1000
        if self.direct_echoes != []:
            for i, echo in enumerate (self.direct_echoes):
                dist = distance(self.x, self.y, echo[0], echo[1])
                if dist < min:
                     min = dist
        else:
            min = 0
        self.direct_val = min
        return min

    def cross_vals(self):
        """ Calculating travel distances for cross-echoes """
        if self.cross_echo1:
            self.cross_val1 = distance(self.x, self.y, self.cross_echo1[0], self.cross_echo1[1]) \
                            + distance(self.cross_echo1[0], self.cross_echo1[1],
                                       self.cross_echo1[2], self.cross_echo1[3])
        else :
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
        self.direct_list = []             # [(x1, y1),(x2, y2)] [(), ()] ...
        self.cross_list = []              # [(x1, y1),(x2, y2), (x3, y3)] [(), (), ()] ...
        self.sensor_list = []
        for i in range(6):
            self.sensor_list.append( (Sensor(self.car_pos, i)) )
        self.move = False

    """ Run the simulation """
    def step(self):
        self.calc_positions()
        self.calc_rays()
        self.sensor_values()

    def calc_positions(self):
        for i, sensor in enumerate (self.sensor_list):
            sensor.update_loc(self.car_pos)

    def calc_rays(self):
        """ Direct echoes: """
        self.direct_list = []
        for i, sensor in enumerate(self.sensor_list):
            for j, rect in enumerate(self.rect_list):
                direct_point = rect_solve(sensor, rect)
                """If found, append to lists"""
                if direct_point != (0,0):
                    self.direct_list.append( [(sensor.x, sensor.y), direct_point] )
                    sensor.direct_echoes.append(direct_point)

            for k, circle in enumerate(self.circle_list):
                direct_point = circle_solve(sensor, circle)
                """If found, append to lists"""
                if direct_point != (0,0):
                    self.direct_list.append( [(sensor.x, sensor.y), direct_point] )
                    sensor.direct_echoes.append(direct_point)

        """ Cross-echoes: """
        self.cross_list = []
        for i, sensor in enumerate(self.sensor_list):
            for j, rect in enumerate(self.rect_list):
                cross_point = cross_rectsolve( sensor, self.sensor_list[i+1], rect)
                """If found, append to lists"""
                if cross_point != (0, 0):
                    self.cross_list.append([(sensor.x, sensor.y), cross_point,
                                            (self.sensor_list[i+1].x, self.sensor_list[i+1].y)])
                    sensor.cross_echo2 = [cross_point[0], cross_point[1],
                                          self.sensor_list[i+1].x, self.sensor_list[i+1].y]
                    self.sensor_list[i+1].cross_echo1 = [cross_point[0], cross_point[1], sensor.x, sensor.y]

            for k, circle in enumerate(self.circle_list):
                cross_point = cross_circlesolve(sensor, self.sensor_list[i+1], circle)
                """If found, append to lists"""
                if cross_point != (0, 0):
                    self.cross_list.append([(sensor.x, sensor.y), cross_point,
                                             (self.sensor_list[i+1].x, self.sensor_list[i+1].y)])
                    sensor.cross_echo2 = [cross_point[0], cross_point[1],
                                          self.sensor_list[i+1].x, self.sensor_list[i+1].y]
                    self.sensor_list[i+1].cross_echo1 = [cross_point[0], cross_point[1], sensor.x, sensor.y]


    def sensor_values(self):
        for i, sensor in enumerate(self.sensor_list):
            sensor.min_direct()
            sensor.cross_vals()
