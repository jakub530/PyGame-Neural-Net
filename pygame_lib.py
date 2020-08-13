import sys
import pygame as pg
import re
from enum import Enum

class color(Enum):
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE =(0,0,255)
    BLACK =(0,0,0)
    WHITE =(255,255,255)
    GRAY =(150,150,150)

class e_text_box:
    def __init__(self, loc, font_size, color_active, color_inactive, min_width, text_color):
        self.gap = 5
        self.border_width = 2
        self.loc = loc
        self.font = pg.font.Font(None, font_size)
        self.text_color = text_color
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.min_width = min_width
        self.change_active(False) 
        self.find_height()
        self.update_text('')
        self.set_text_loc()
        
    def find_height(self):
        self.text_height = self.font.get_height()

    def set_box(self):
        self.height = self.text_height + 2 * self.gap
        self.width = max(self.min_width, self.txt_surface.get_width() + 2 * self.gap)
        self.rect = pg.Rect(*self.loc, self.width, self.height)

    def update_text(self, new_text):
        self.text = new_text
        self.txt_surface = self.font.render(self.text, True, self.text_color)
        self.set_box()
    
    def change_active(self, new_state):
        self.active = new_state
        if new_state == True:
            self.color = self.color_active
        else:
            self.color = self.color_inactive

    def set_text_loc(self):
        self.text_loc = (self.rect.x + self.gap, self.rect.y + self.gap)

class e_text_boxes:
    def __init__(self, **kwargs):
        self.default_font_size = 32
        self.default_color_active  =  pg.Color('dodgerblue2') 
        self.default_color_inactive = pg.Color('lightskyblue3')
        self.default_min_width = 200
        self.default_text_color = pg.Color('white')

        for elem in vars(self):
            if elem in kwargs:
                setattr(self, elem, kwargs[elem])

        self.boxes = {}

    def add_box(self, loc, box_name, **kwargs):
        params = {}
        for full_arg in vars(self):
            if(re.search("^default_", full_arg)):
                arg = re.sub("default_","",full_arg)
                if(arg in kwargs):
                    params[arg] = kwargs[arg]
                else:
                    params[arg] = getattr(self, full_arg)

        new_box = e_text_box(loc, params["font_size"], params["color_active"], params["color_inactive"], params["min_width"], params["text_color"])
        
        box_name = str(box_name)
        while(True):
            if box_name in self.boxes:
                box_name = box_name + "_bis"
            else:
                self.boxes[box_name] = new_box
                return

    def check_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
            for input_box in self.boxes.values():
                if input_box.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    input_box.change_active(not input_box.active)
                else:
                    input_box.change_active(False)
        if event.type == pg.KEYDOWN:
            for input_box in self.boxes.values():
                if input_box.active:
                    if event.key == pg.K_RETURN:
                        print(input_box.text)
                        input_box.update_text('')
                    elif event.key == pg.K_BACKSPACE:
                        input_box.update_text(input_box.text[:-1])
                    else:
                        input_box.update_text(input_box.text + event.unicode)

    def display_boxes(self, screen):
        for input_box in self.boxes.values():
            screen.blit(input_box.txt_surface, input_box.text_loc)
            pg.draw.rect(screen, input_box.color, input_box.rect, input_box.border_width)

    def get_texbox_value(self, key):
        if key in self.boxes:
            return self.boxes[key].text
        else:
            print("Box with identifier {key} not found".format(key = key))

class buttons:
    def __init__(self, **kwargs):
        pass


def init_pygame(size):
    pg.init()
    screen = pg.display.set_mode(size)
    clock  = pg.time.Clock()
    return screen, clock

