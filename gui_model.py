import math

import pygame

from colors import Colors
from gui_constants import GUIConstants


class DragAndDrop(pygame.sprite.Sprite):
    """Stores the drag state and the previous state of the object for the case of invalid release position"""

    def __init__(self):
        super().__init__()
        self.is_dragged = False
        self.pick_up_pos = None

    def set_dragged(self, pick_up_pos):
        self.is_dragged = True
        self.pick_up_pos = pick_up_pos


class CircleObject(DragAndDrop):
    """Draggable circle object"""

    def __init__(self, screen, gui_pos, r):
        super().__init__()
        self.screen = screen
        self.gui_pos = gui_pos
        self.rect = pygame.Rect(self.gui_pos[0] - r, self.gui_pos[1] - r, r * 2, r * 2)
        self.surface = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, Colors.BLACK, (r, r), r)
        self.mask = pygame.mask.from_surface(self.surface)
        self.radius = r

    def draw(self):
        """Draws the circle object"""
        pygame.draw.circle(self.screen, Colors.CIRCLE_OBJECT, self.gui_pos, self.radius)
        pygame.draw.circle(self.screen, Colors.CIRCLE_OBJECT_BORDER, self.gui_pos, self.radius, 2)

    def set_gui_pos(self, pos):
        """Sets the position of the gui and its rectangle"""
        self.gui_pos = pos
        self.rect = pygame.Rect(self.gui_pos[0] - self.radius, self.gui_pos[1] - self.radius, self.radius * 2,
                                self.radius * 2)

    def is_clicked(self, point):
        """Checks if the given point is inside the circle"""
        return math.sqrt((self.gui_pos[0] - point[0]) ** 2 + (self.gui_pos[1] - point[1]) ** 2) <= self.radius

    def is_colliding(self, sprite):
        """Return True if the object collides with the other object."""
        return pygame.sprite.collide_mask(self, sprite)


class RectangleObject(DragAndDrop):
    """Draggable rectangle object"""

    def __init__(self, screen, gui_pos, rot, width, height):
        super().__init__()
        self.screen = screen
        self.gui_pos = gui_pos
        self.rot = rot
        self.width = width
        self.height = height
        self.points = []
        self.surface = None
        self.mask = None

        self.calculate_mask()

    def calculate_mask(self):
        """Mask creation"""
        self.points = [
            self.gui_pos,
            (self.width * math.cos(self.rot) + self.gui_pos[0], self.width * math.sin(self.rot) + self.gui_pos[1]),
            (self.width * math.cos(self.rot) - self.height * math.sin(self.rot) + self.gui_pos[0],
             self.width * math.sin(self.rot) + self.height * math.cos(self.rot) + self.gui_pos[1]),
            (-self.height * math.sin(self.rot) + self.gui_pos[0], self.height * math.cos(self.rot) + self.gui_pos[1])
        ]

        min_x = min(map(lambda point: point[0], self.points))
        max_x = max(map(lambda point: point[0], self.points))
        width = max_x - min_x
        min_y = min(map(lambda point: point[1], self.points))
        max_y = max(map(lambda point: point[1], self.points))
        height = max_y - min_y

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.rect = pygame.Rect(min_x, min_y, width, height)
        pygame.draw.polygon(self.surface,
                            Colors.BLACK,
                            [(self.points[0][0] - min_x, self.points[0][1] - min_y),
                             (self.points[1][0] - min_x, self.points[1][1] - min_y),
                             (self.points[2][0] - min_x, self.points[2][1] - min_y),
                             (self.points[3][0] - min_x, self.points[3][1] - min_y)])
        self.mask = pygame.mask.from_surface(self.surface)

    def draw(self):
        """Draws the rectangle object"""
        pygame.draw.polygon(self.screen, Colors.RECTANGLE_OBJECT, self.points)
        pygame.draw.polygon(self.screen, Colors.RECTANGLE_OBJECT_BORDER, self.points, 2)

    def is_colliding(self, sprite):
        """Return True if the object collides with the other object."""
        return pygame.sprite.collide_mask(self, sprite)

    def is_clicked(self, point):
        """Creates a sprite element for the clicked point and checks if it is colliding with the object"""
        click = pygame.sprite.Sprite()
        surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.BLACK, pygame.Rect(0, 0, 1, 1))
        click.rect = pygame.Rect(point[0], point[1], 1, 1)
        click.mask = pygame.mask.from_surface(surface)
        return pygame.sprite.collide_mask(self, click)

    def set_gui_pos(self, pos):
        """Sets the position of the gui and its rectangle"""
        self.gui_pos = pos
        self.calculate_mask()

    def set_rot(self, rot):
        """Sets the rotation of the object and its rectangle"""
        self.rot = rot
        self.calculate_mask()


class CarObject(DragAndDrop):
    """Draggable car object"""

    def __init__(self, screen, gui_pos, width, height):
        super().__init__()
        self.screen = screen
        self.image = pygame.transform.scale(pygame.image.load("res/car.png"), (width, height))
        self.width = width
        self.height = height
        self.gui_pos = gui_pos
        self.rect = pygame.Rect(gui_pos[0] - width, gui_pos[1], width, height)

        # self.mask = pygame.mask.from_surface(self.image)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.BLACK, pygame.Rect(0, 0, width, height))
        self.mask = pygame.mask.from_surface(surface)

        self.sensors = []
        self.init_sensors()

    def is_colliding(self, sprite):
        """Return True if the object collides with the other object."""
        return pygame.sprite.collide_mask(self, sprite)

    def is_clicked(self, point):
        """Creates a sprite element for the clicked point and checks if it is colliding with the object"""
        click = pygame.sprite.Sprite()
        surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        pygame.draw.rect(surface, Colors.BLACK, pygame.Rect(0, 0, 1, 1))
        click.rect = pygame.Rect(point[0], point[1], 1, 1)
        click.mask = pygame.mask.from_surface(surface)
        return pygame.sprite.collide_mask(self, click)

    def set_gui_pos(self, pos):
        """Sets the position of the gui and its rectangle"""
        self.gui_pos = (pos[0], self.gui_pos[1])
        self.calculate_rect()
        self.init_sensors()

    def calculate_rect(self):
        """Calculates the rectangle of the object"""
        self.rect = pygame.Rect(self.gui_pos[0] - self.width, self.gui_pos[1], self.width, self.height)

    def init_sensors(self):
        """Initializes the sensors of the car"""
        self.sensors.clear()
        self.sensors.append(
            self.SensorObject(self.screen, (self.gui_pos[0] - self.height / 220 * 5, self.gui_pos[1]), -math.pi / 4,
                              self.height * GUIConstants.SENSOR_SIZE, self.height))
        self.sensors.append(
            self.SensorObject(self.screen, (self.gui_pos[0], self.gui_pos[1] + self.height / 220 * 40), 0,
                              self.height * GUIConstants.SENSOR_SIZE, self.height))
        self.sensors.append(
            self.SensorObject(self.screen, (self.gui_pos[0], self.gui_pos[1] + self.height / 220 * 80), 0,
                              self.height * GUIConstants.SENSOR_SIZE, self.height))
        self.sensors.append(
            self.SensorObject(self.screen, (self.gui_pos[0], self.gui_pos[1] + self.height / 220 * 140), 0,
                              self.height * GUIConstants.SENSOR_SIZE, self.height))
        self.sensors.append(
            self.SensorObject(self.screen, (self.gui_pos[0], self.gui_pos[1] + self.height / 220 * 180), 0,
                              self.height * GUIConstants.SENSOR_SIZE, self.height))
        self.sensors.append(
            self.SensorObject(self.screen, (self.gui_pos[0] - self.height / 220 * 5, self.gui_pos[1] + self.height),
                              math.pi / 4, self.height * GUIConstants.SENSOR_SIZE, self.height))

    def draw(self):
        """Draws the car on the screen"""
        self.screen.blit(self.image, self.rect)
        for sensor in self.sensors:
            sensor.draw()

    class SensorObject:
        """Sensor object of the car"""

        def __init__(self, screen, gui_pos, rot, size, car_height):
            self.screen = screen
            self.gui_pos = gui_pos
            self.rot = rot
            self.size = size
            self.color = Colors.GREEN
            self.points = []
            self.beam_points = []
            self.car_height = car_height
            self.beam_radius = self.car_height / 220 * 300
            self.calculate_points(gui_pos)

        def calculate_points(self, gui_pos):
            """Set the points of the sensor according to the position and rotation"""
            self.gui_pos = gui_pos
            self.points = calculate_rotation(
                [
                    (-self.size, -self.size / 2),
                    (0, -self.size / 2),
                    (0, self.size / 2),
                    (-self.size, self.size / 2)
                ],
                self.rot,
                self.gui_pos
            )
            self.beam_points = calculate_rotation(
                [
                    (self.beam_radius / 2, -math.sqrt(3) / 2 * self.beam_radius),
                    (self.beam_radius / 2, math.sqrt(3) / 2 * self.beam_radius)
                ],
                self.rot,
                self.gui_pos
            )

        def draw(self):
            """Draws the sensor on the screen"""
            """Beam of the sensor"""
            pygame.draw.line(self.screen,
                             "yellow",
                             self.gui_pos,
                             self.beam_points[0])
            pygame.draw.line(self.screen,
                             "yellow",
                             self.gui_pos,
                             self.beam_points[1])
            pygame.draw.arc(self.screen,
                            "yellow",
                            pygame.Rect(self.gui_pos[0] - self.beam_radius, self.gui_pos[1] - self.beam_radius,
                                        2 * self.beam_radius, 2 * self.beam_radius),
                            -math.pi / 3 - self.rot,
                            math.pi / 3 - self.rot,
                            1)

            """Sensor 'box'"""
            pygame.draw.polygon(self.screen,
                                self.color,
                                self.points)

            pygame.draw.polygon(self.screen,
                                Colors.BLACK,
                                self.points,
                                1)

        def set_color(self, values):
            not_zero = []
            for val in values:
                if val != 0:
                    not_zero.append(val)

            if not not_zero:
                self.color = Colors.GREEN
            else:
                value = min(not_zero)
                if value <= GUIConstants.DANGER:
                    self.color = Colors.RED
                elif value <= GUIConstants.WARNING:
                    self.color = "orange"
                elif value <= GUIConstants.OBJECT_DETECTED:
                    self.color = "yellow"
            self.draw()


def calculate_rotation(rel_points, rot, rot_point):
    """Calculates the rotated location of the given point"""
    ret = []

    for rel_point in rel_points:
        ret.append((
            math.cos(rot) * rel_point[0] - math.sin(rot) * rel_point[1] + rot_point[0],
            math.sin(rot) * rel_point[0] + math.cos(rot) * rel_point[1] + rot_point[1]
        ))

    return ret
