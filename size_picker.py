import pygame
from gui_constants import GUIConstants
from colors import Colors


class SizePicker:
    """Size picker for the drag in elements"""

    def __init__(self, screen, gui_pos):
        self.gui_pos = gui_pos
        self.screen = screen
        self.rectangles = []
        self.selected = 1

    def set_selected(self, selected):
        self.selected = selected

    def draw(self):
        """Draws the size picker to the screen"""
        rect = pygame.Rect(self.gui_pos[0], self.gui_pos[1],
                           GUIConstants.SIZE_PICKER_SIZE * GUIConstants.SIZE_PICKER_CELL, GUIConstants.SIZE_PICKER_CELL)
        pygame.draw.rect(self.screen, Colors.WHITE, rect)
        self.draw_grid()
        for i in range(GUIConstants.SIZE_PICKER_SIZE):
            self.draw_text(i, str(i + 1))

    def draw_grid(self):
        """Draws the grid of the size picker"""
        self.rectangles.clear()
        for x in range(0, GUIConstants.SIZE_PICKER_SIZE * GUIConstants.SIZE_PICKER_CELL, GUIConstants.SIZE_PICKER_CELL):
            rect = pygame.Rect(x + self.gui_pos[0], self.gui_pos[1],
                               GUIConstants.SIZE_PICKER_CELL, GUIConstants.SIZE_PICKER_CELL)
            if (x / GUIConstants.SIZE_PICKER_CELL) + 1 == self.selected:
                pygame.draw.rect(self.screen, (255, 0, 0), rect)
                pygame.draw.rect(self.screen, Colors.LIGHTGREY, rect, 1)
            else:
                pygame.draw.rect(self.screen, Colors.LIGHTGREY, rect, 1)
            self.rectangles.append(rect)

    def draw_text(self, x, msg):
        """Draws a message into a cell"""
        font = pygame.font.SysFont(None, 20)
        img = font.render(msg, True, Colors.BLACK)
        self.screen.blit(img, ((x + 0.5) * GUIConstants.SIZE_PICKER_CELL - img.get_width() * 0.5 + self.gui_pos[0],
                               0.5 * GUIConstants.SIZE_PICKER_CELL - img.get_height() * 0.5 + self.gui_pos[1]))
