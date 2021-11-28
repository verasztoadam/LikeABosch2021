import pygame
from gui_constants import GUIConstants
from colors import Colors


class Table:
    def __init__(self, screen, gui_pos):
        """Table element for the display of the measured values"""
        self.screen = screen
        self.gui_pos = gui_pos

    def draw(self):
        pygame.draw.rect(self.screen,
                         Colors.WHITE,
                         pygame.Rect(self.gui_pos[0], self.gui_pos[1],
                                     4 * GUIConstants.TABLE_CELL_WIDTH,
                                     7 * GUIConstants.TABLE_CELL_HEIGHT))
        self.draw_grid()
        self.draw_text(1, 0, "Direct echo [m]")
        self.draw_text(2, 0, "Left cross echo [m]")
        self.draw_text(3, 0, "Right cross echo [m]")
        self.draw_text(0, 1, "Sensor 1")
        self.draw_text(0, 2, "Sensor 2")
        self.draw_text(0, 3, "Sensor 3")
        self.draw_text(0, 4, "Sensor 4")
        self.draw_text(0, 5, "Sensor 5")
        self.draw_text(0, 6, "Sensor 6")

    def draw_grid(self):
        """Draws the grid of the table"""
        for x in range(0, 4 * GUIConstants.TABLE_CELL_WIDTH, GUIConstants.TABLE_CELL_WIDTH):
            for y in range(0, 7 * GUIConstants.TABLE_CELL_HEIGHT, GUIConstants.TABLE_CELL_HEIGHT):
                rect = pygame.Rect(x + self.gui_pos[0], y + self.gui_pos[1],
                                   GUIConstants.TABLE_CELL_WIDTH, GUIConstants.TABLE_CELL_HEIGHT)
                pygame.draw.rect(self.screen, Colors.LIGHTGREY, rect, 1)

    def draw_text(self, x, y, msg):
        """Draws a message into the cell"""
        font = pygame.font.SysFont(None, 20)
        img = font.render(msg, True, Colors.BLACK)
        self.screen.blit(img, ((x + 0.5) * GUIConstants.TABLE_CELL_WIDTH - img.get_width() * 0.5 + self.gui_pos[0],
                               (y + 0.5) * GUIConstants.TABLE_CELL_HEIGHT - img.get_height() * 0.5 + self.gui_pos[1]))

    def draw_value(self, x, y, value):
        """Draws a value into the cell"""
        text = "X"
        if value != 0:
            text = str(round(value, 3))
        self.draw_text(x, y, text)