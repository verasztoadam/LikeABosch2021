import math

import pygame

from colors import Colors


class DragAndDrop(pygame.sprite.Sprite):
    """Stores the drag state and the previous state of the object for the case of invalid release position"""

    def __init__(self):
        super().__init__()
        self.is_dragged = False
        self.pick_up_pos = None

    def set_dragged(self, pick_up_pos):
        self.is_dragged = True
        self.pick_up_pos = pick_up_pos


def circle_surface(color, radius):
    shape_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    return shape_surf


class CircleObject(DragAndDrop):
    """Draggable circle object"""

    def __init__(self, screen, gui_pos, r):
        super().__init__()
        self.screen = screen
        self.gui_pos = gui_pos
        self.rect = pygame.Rect(self.gui_pos[0] - r, self.gui_pos[1] - r, r * 2, r * 2)
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

    def is_colliding(self, collide_group):
        """Return True if the object collides with another objects. The collide group contains the object,
        therefore two or more collided objects mean real collision."""
        collisions = pygame.sprite.spritecollide(self, collide_group, False, pygame.sprite.collide_circle)
        return len(collisions) > 1

class RectangleObject(DragAndDrop):
    """Draggable rectangle object"""
    pass
