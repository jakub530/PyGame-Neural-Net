import sys, pygame
from enum import Enum

class color(Enum):
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE =(0,0,255)
    BLACK =(0,0,0)
    WHITE =(255,255,255)
    GRAY =(150,150,150)

def init_pygame(size):
    pygame.init()
    screen = pygame.display.set_mode(size)
    clock  = pygame.time.Clock()
    return screen, clock