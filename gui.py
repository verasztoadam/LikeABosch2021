import math
import sys
import pygame

import gui_model
from gui_constants import GUIConstants
from colors import Colors
from button import Button
from table import Table
from control import Control
from size_picker import SizePicker
import simulation
import conversion


class GUI:
    def __init__(self):
        """Initializes the window of the application and the class variables"""
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1280, 720))
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption(GUIConstants.WINDOW_TITLE)
        game_icon = pygame.image.load('res/logo.png')
        pygame.display.set_icon(game_icon)

        self.play_btn = Button(self.screen, "Start animation",
                               (0 + GUIConstants.BUTTON_MARGIN, self.height * 0.5 + GUIConstants.BUTTON_MARGIN))
        button_height = self.play_btn.rect.height
        self.stop_btn = Button(self.screen, "Stop animation",
                               (0 + GUIConstants.BUTTON_MARGIN, self.height * 0.5 + 2 * GUIConstants.BUTTON_MARGIN +
                                button_height))
        self.reset_btn = Button(self.screen, "Reset simulation",
                                (0 + GUIConstants.BUTTON_MARGIN, self.height * 0.5 + 3 * GUIConstants.BUTTON_MARGIN
                                 + 2 * button_height))
        self.exit_btn = Button(self.screen, "Exit",
                               (0 + GUIConstants.BUTTON_MARGIN, self.height * 0.5 + 4 * GUIConstants.BUTTON_MARGIN + 3 *
                                button_height))

        self.data_table = Table(self.screen, (self.play_btn.rect.width + 2 * GUIConstants.BUTTON_MARGIN,
                                              self.height * 0.5 + GUIConstants.BUTTON_MARGIN))

        self.car = gui_model.CarObject(self.screen,
                                       (300, self.height * 0.25 - self.width * 0.075 / 2),
                                       self.width * 0.15,
                                       self.width * 0.075)
        GUIConstants.PX_TO_M = 2.2/(self.width * 0.075)

        self.left_border = gui_model.RectangleObject(self.screen, (-5, 0), 0, 10, self.height * 0.5 - 1)
        self.right_border = gui_model.RectangleObject(self.screen, (self.width - 5, 0), 0, 10, self.height * 0.5 - 1)

        self.rectangle_objects = [self.left_border, self.right_border]
        self.sprites = [self.left_border, self.car, self.right_border]

        self.drag_in_container = pygame.Rect(890, self.height * 0.5 + GUIConstants.BUTTON_MARGIN + 50, 350, 230)
        self.drag_in_circle = gui_model.CircleObject(self.screen,
                                                     (970, self.height * 0.5 + GUIConstants.BUTTON_MARGIN + 170),
                                                     50)
        self.drag_in_rectangle = gui_model.RectangleObject(self.screen,
                                                           (1075, self.height * 0.5 + GUIConstants.BUTTON_MARGIN + 140),
                                                           0, 100, 50)

        self.dashboard_container = pygame.sprite.Sprite()
        self.dashboard_container.rect = pygame.Rect(0, 0.5 * self.height, self.width, 0.5 * self.height)
        surface = pygame.Surface((self.width, 0.5 * self.height))
        pygame.draw.rect(surface, Colors.BLACK, pygame.Rect(0, 0, self.width, 0.5 * self.height))
        self.dashboard_container.mask = pygame.mask.from_surface(surface)

        self.size_picker = SizePicker(self.screen,
                                      (890, self.height * 0.5 + GUIConstants.BUTTON_MARGIN))

        self.is_running = False
        self.clock = pygame.time.Clock()

        """Init simulation"""
        self.model = simulation.Model()

        """Init control"""
        self.control = Control()

    def update(self):
        """Updates the content of the window"""
        self.screen.fill(Colors.WHITE)

        self.draw_game_map()

        mouse_pos = pygame.mouse.get_pos()

        """Handle animation"""
        if self.is_running:
            time_delay = self.clock.get_time()
            start_pos = self.car.gui_pos
            self.car.set_gui_pos((start_pos[0] + time_delay / 10000 * self.width * self.control.get_speed(), 0))
            if self.is_colliding_any(self.car):
                self.car.set_gui_pos(start_pos)

        """Handle the occurred events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                """Button clicks"""
                if self.exit_btn.rect.collidepoint(mouse_pos):
                    """Exit the application"""
                    pygame.quit()
                    sys.exit(0)

                if self.play_btn.rect.collidepoint(mouse_pos):
                    """Start animation"""
                    self.is_running = True

                if self.stop_btn.rect.collidepoint(mouse_pos):
                    """Stop animation"""
                    self.is_running = False

                if self.reset_btn.rect.collidepoint(mouse_pos):
                    """Reset the obstacles"""
                    self.sprites.clear()
                    self.car.set_gui_pos((300, 0))
                    self.sprites = [self.car, self.left_border, self.right_border]
                    self.rectangle_objects = [self.left_border, self.right_border]

                """Size picker clicks"""
                for i in range(len(self.size_picker.rectangles)):
                    if self.size_picker.rectangles[i].collidepoint(mouse_pos):
                        self.size_picker.set_selected(i + 1)

                """If the drag in are was clicked then add a new drag and drop element simulation"""
                if self.drag_in_circle.is_clicked(mouse_pos):
                    co = gui_model.CircleObject(self.screen,
                                                mouse_pos,
                                                self.height * 0.2 * self.size_picker.selected / 10)
                    co.set_dragged(mouse_pos)
                    self.sprites.append(co)

                if self.drag_in_rectangle.is_clicked(mouse_pos):
                    ro = gui_model.RectangleObject(self.screen,
                                                   mouse_pos,
                                                   0,
                                                   self.height * 0.4 * self.size_picker.selected / 10,
                                                   self.height * 0.2 * self.size_picker.selected / 10)
                    ro.set_dragged(mouse_pos)
                    self.rectangle_objects.append(ro)
                    self.sprites.append(ro)

                """Check the draggable components"""
                for sprite in self.sprites:
                    if sprite in [self.left_border, self.right_border]:
                        continue
                    if sprite.is_clicked(mouse_pos):
                        sprite.set_dragged(sprite.gui_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                """Release dragged components"""
                for sprite in self.sprites:
                    if sprite.is_dragged:
                        if self.is_colliding_any(sprite) or sprite.is_colliding(self.dashboard_container):
                            sprite.set_gui_pos(sprite.pick_up_pos)
                        sprite.is_dragged = False
                        if self.drag_in_container.collidepoint(sprite.gui_pos):
                            """Remove element if it is 'placed' in the drag in container"""
                            self.sprites.remove(sprite)
                            if isinstance(sprite, gui_model.RectangleObject):
                                self.rectangle_objects.remove(sprite)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in [4, 5]:
                """Rotate the rectangle objects with the mouse wheel (+/- 5 degrees)"""
                for rectangle_object in self.rectangle_objects:
                    if rectangle_object in [self.left_border, self.right_border]:
                        continue
                    if rectangle_object.is_clicked(mouse_pos):
                        start_rot = rectangle_object.rot
                        if event.button == 4:
                            rectangle_object.set_rot((rectangle_object.rot + math.pi / 36) % (2 * math.pi))
                        elif event.button == 5:
                            rectangle_object.set_rot((rectangle_object.rot - math.pi / 36) % (2 * math.pi))
                        if self.is_colliding_any(rectangle_object) or \
                                rectangle_object.is_colliding(self.dashboard_container):
                            rectangle_object.set_rot(start_rot)

        """Draw dashboard"""
        self.draw_dashboard()

        """Simulation update"""
        sim_rectangles = []
        sim_circles = []
        for sprite in self.sprites:
            if isinstance(sprite, gui_model.CircleObject):
                sim_circles.append(conversion.gui_to_sim_circle(self.height * 0.5, sprite))
            elif isinstance(sprite, gui_model.RectangleObject):
                sim_rectangles.append(conversion.gui_to_sim_rect(self.height * 0.5, sprite))

        self.model.rect_list = sim_rectangles
        self.model.circle_list = sim_circles
        self.model.car_pos = (self.car.gui_pos[0] * GUIConstants.PX_TO_M,
                              (self.height*0.5 - self.car.gui_pos[1]) * GUIConstants.PX_TO_M)
        self.model.step()

        """Draw objects"""
        for sprite in self.sprites:
            if sprite.is_dragged:
                sprite.set_gui_pos(mouse_pos)
                """If the dragged object is the car, then do not allow collision during dragging"""
                if isinstance(sprite, gui_model.CarObject):
                    if self.is_colliding_any(sprite):
                        sprite.set_gui_pos(sprite.pick_up_pos)
                    else:
                        sprite.set_dragged(sprite.gui_pos)
            sprite.draw()

        """Get cross echo list"""
        for cross in self.model.cross_list:
            pygame.draw.line(self.screen, Colors.PURPLE,
                             (cross[0][0] / GUIConstants.PX_TO_M,
                              self.height * 0.5 - (cross[0][1] / GUIConstants.PX_TO_M)),
                             (cross[1][0] / GUIConstants.PX_TO_M,
                              self.height * 0.5 - (cross[1][1] / GUIConstants.PX_TO_M)),
                             3)
            pygame.draw.line(self.screen, Colors.PURPLE,
                             (cross[2][0] / GUIConstants.PX_TO_M,
                              self.height * 0.5 - (cross[2][1] / GUIConstants.PX_TO_M)),
                             (cross[1][0] / GUIConstants.PX_TO_M,
                              self.height * 0.5 - (cross[1][1] / GUIConstants.PX_TO_M)),
                             3)

        """Get echo list"""
        for direct in self.model.direct_list:
            pygame.draw.line(self.screen, Colors.GREEN,
                             (direct[0][0] / GUIConstants.PX_TO_M,
                              self.height * 0.5 - (direct[0][1] / GUIConstants.PX_TO_M)),
                             (direct[1][0] / GUIConstants.PX_TO_M,
                              self.height * 0.5 - (direct[1][1] / GUIConstants.PX_TO_M)),
                             3)

        """Get sensor values"""
        self.control.input.clear()
        for i, sensor in enumerate(self.model.sensor_list):
            self.control.input.append(sensor.direct_val)
            self.control.input.append(sensor.cross_val_r)
            self.control.input.append(sensor.cross_val_l)
            self.car.sensors[sensor.index].set_color([sensor.direct_val, sensor.cross_val_l, sensor.cross_val_r])
            self.data_table.draw_value(1, i + 1, sensor.direct_val)
            self.data_table.draw_value(2, i + 1, sensor.cross_val_l)
            self.data_table.draw_value(3, i + 1, sensor.cross_val_r)

        self.clock.tick(30)
        pygame.display.update()

    def draw_game_map(self):
        """Draws the game map of the gui"""
        rect = pygame.Rect(0, 0, self.width, self.height * 0.5)
        pygame.draw.rect(self.screen, Colors.LIGHTGREY, rect)

    def draw_dashboard(self):
        """Draws the dashboard of the gui"""
        pygame.draw.rect(self.screen, Colors.LIGHTSLATEGREY, self.dashboard_container.rect)
        self.play_btn.draw()
        self.exit_btn.draw()
        self.reset_btn.draw()
        self.stop_btn.draw()
        self.data_table.draw()
        self.draw_obstacle_drag_in()
        self.size_picker.draw()

    def draw_obstacle_drag_in(self):
        """Draws the obstacle drag in section"""
        pygame.draw.rect(self.screen, Colors.WHITE, self.drag_in_container)
        self.drag_in_circle.draw()
        self.drag_in_rectangle.draw()

    def is_colliding_any(self, sprite):
        """Return if the given sprite is colliding with one of the sprites in the sprite list"""
        collision_counter = 0
        for collide_sprite in self.sprites:
            if sprite.is_colliding(collide_sprite):
                collision_counter += 1
        return collision_counter > 1
