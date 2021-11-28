import pygame
from colors import Colors
from gui_constants import GUIConstants

class Button:
    """Button class"""

    def __init__(self, screen, text, gui_pos):
        self.screen = screen
        self.gui_pos = gui_pos
        self.font = pygame.font.SysFont(None, 30)
        self.text = self.font.render(text, True, Colors.WHITE)
        self.size = self.text.get_size()
        self.surface = pygame.Surface((300, 50))
        self.surface.fill(Colors.PRIMARY)
        self.surface.blit(self.text, (150 - self.size[0]/2, 25 - self.size[1]/2))
        self.rect = pygame.Rect(self.gui_pos[0], self.gui_pos[1], 300,
                                50)

    def draw(self):
        self.screen.blit(self.surface, self.gui_pos)
