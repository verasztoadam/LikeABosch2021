import sys
import pygame

import gui_model
from gui_constants import GUIConstants
from colors import Colors


class GUI:
    def __init__(self):
        """Initializes the window of the application and the class variables"""
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption(GUIConstants.WINDOW_TITLE)
        game_icon = pygame.image.load('res/logo.png')
        pygame.display.set_icon(game_icon)

        co1 = gui_model.CircleObject(self.screen, (50, 50), 30)
        co2 = gui_model.CircleObject(self.screen, (200, 200), 50)

        self.circle_objects = [co1, co2]
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.circle_objects)

    def update(self):
        """Updates the content of the window"""
        self.screen.fill(Colors.LIGHTSLATEGREY)

        self.draw_containers()

        mouse_pos = pygame.mouse.get_pos()

        """Handle the occurred events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                """Check the draggable components"""
                for circle_object in self.circle_objects:
                    if circle_object.is_clicked(mouse_pos):
                        circle_object.set_dragged(circle_object.gui_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for circle_object in self.circle_objects:
                    if circle_object.is_dragged:
                        # TODO: Check collision with other objects
                        if circle_object.is_colliding(self.sprites):
                            circle_object.set_gui_pos(circle_object.pick_up_pos)
                        circle_object.is_dragged = False

        """Draw objects"""
        for circle_object in self.circle_objects:
            if circle_object.is_dragged:
                circle_object.set_gui_pos(mouse_pos)
            circle_object.draw()

        pygame.display.update()

    def draw_containers(self):
        """Draws the containers of the gui"""
        """Game map"""
        rect = pygame.Rect(GUIConstants.GAME_MAP_MARGIN,
                           GUIConstants.GAME_MAP_MARGIN,
                           0.75 * self.width - 2 * GUIConstants.GAME_MAP_MARGIN,
                           self.height - 2 * GUIConstants.GAME_MAP_MARGIN)
        pygame.draw.rect(self.screen, Colors.LIGHTGREY, rect)
        pygame.draw.rect(self.screen, Colors.PRIMARY, rect, 5)

    def draw_circle(self, x, y, r):
        pygame.draw.circle(self.screen, Colors.PRIMARY, (100, 100), 10)
