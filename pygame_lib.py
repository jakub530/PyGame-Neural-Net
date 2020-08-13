import sys
import pygame as pg
import re
from enum import Enum
import copy
import numpy as np

class color(Enum):
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE =(0,0,255)
    BLACK =(0,0,0)
    WHITE =(255,255,255)
    GRAY =(150,150,150)

def fill_gradient(surface, color, gradient, rect=None, vertical=True, forward=True):
    """fill a surface with a gradient pattern
    Parameters:
    color -> starting color
    gradient -> final color
    rect -> area to fill; default is surface's rect
    vertical -> True=vertical; False=horizontal
    forward -> True=forward; False=reverse
    
    Pygame recipe: http://www.pygame.org/wiki/GradientCode
    """
    if rect is None: rect = surface.get_rect()
    x1,x2 = rect.left, rect.right
    y1,y2 = rect.top, rect.bottom
    if vertical: h = y2-y1
    else:        h = x2-x1
    if forward: a, b = color, gradient
    else:       b, a = color, gradient
    rate = (
        float(b[0]-a[0])/h,
        float(b[1]-a[1])/h,
        float(b[2]-a[2])/h
    )
    fn_line = pg.draw.line
    if vertical:
        for line in range(y1,y2):
            color = (
                min(max(a[0]+(rate[0]*(line-y1)),0),255),
                min(max(a[1]+(rate[1]*(line-y1)),0),255),
                min(max(a[2]+(rate[2]*(line-y1)),0),255)
            )
            fn_line(surface, color, (x1,line), (x2,line))
    else:
        for col in range(x1,x2):
            color = (
                min(max(a[0]+(rate[0]*(col-x1)),0),255),
                min(max(a[1]+(rate[1]*(col-x1)),0),255),
                min(max(a[2]+(rate[2]*(col-x1)),0),255)
            )
            fn_line(surface, color, (col,y1), (col,y2))

class UI_colors:
    def __init__(self):
        self.colors = { "background_c" : {"active" : pg.Color('grey'), "inactive" : pg.Color('black')},
                        "frame_c"      : {"active" : pg.Color('red'), "inactive" : pg.Color('green')},
                        "text_c"       : {"active" : pg.Color('yellow'), "inactive" : pg.Color('white')},
                        "gradient_c"   : {"active" : pg.Color('darkslategray'), "inactive" : pg.Color('darkslategray')}}

class UI_elem:
    def __init__(self, loc, colors, params): #font_size, text, use_frame, use_gradient, use_background, fixed_width, match_size, size, min_width):
        self.gap = 5
        self.border_width = 2
        self.loc = loc
        self.font = pg.font.Font(None, params["font_size"])
        self.colors = colors
        self.use_frame = params["use_frame"]
        self.use_gradient = params["use_gradient"]
        self.use_background = params["use_background"]
        self.fixed_width = params["fixed_width"]
        self.match_size = params["match_size"]
        self.default_size = params["size"]
        self.min_width = params["min_width"]
        self.active = False
        self.interact = params["interact"]
        self.find_height()
        self.update_text(params["text"])
        self.set_text_loc()

    def find_height(self):
        self.text_height = self.font.get_height()

    def get_active(self):
        if(self.active):
            return "active"
        else:
            return "inactive"

    def set_box(self):
        if self.fixed_width:
            self.rect = pg.Rect(*self.loc,*self.default_size)
        else:
            self.height = self.text_height + 2 * self.gap
            if self.match_size == True:
                self.width = self.txt_surface.get_width() + 2 * self.gap
            else:
                self.width = max(self.min_width, self.txt_surface.get_width() + 2 * self.gap)
            self.rect = pg.Rect(*self.loc, self.width, self.height)

    def update_text(self, new_text):
        self.text = new_text
        self.txt_surface = self.font.render(self.text, True, self.colors.colors["text_c"][self.get_active()])
        self.set_box()
    
    def change_active(self, new_state):
        self.active = new_state
        self.update_text(self.text)

    def set_text_loc(self):
        self.text_loc = (self.rect.x + self.gap, self.rect.y + self.gap)

    def display_elem(self, screen):
        
        if self.use_background:
            if self.use_gradient:
                fill_gradient(screen, self.colors.colors["background_c"][self.get_active()], self.colors.colors["gradient_c"][self.get_active()], self.rect)
            else:
                pg.draw.rect(screen, self.colors.colors["background_c"][self.get_active()], self.rect)

        if self.use_frame:
            pg.draw.rect(screen, self.colors.colors["frame_c"][self.get_active()], self.rect, self.border_width)
        screen.blit(self.txt_surface, self.text_loc)

class UI_elems:
    def __init__(self, **kwargs):
        self.default_font_size = 32
        self.default_colors = UI_colors()
        self.default_use_frame = True
        self.default_use_gradient = True
        self.default_use_background = True
        self.default_fixed_width = False
        self.default_match_size = False
        self.default_size = np.array([200,40])
        self.default_min_width = 200
        self.default_text = ""
        self.default_interact = True

        for elem in vars(self):
            if elem in kwargs:
                setattr(self, elem, kwargs[elem])

        self.default_colors = self.parse_colors(**kwargs)

    def parse_colors(self,**kwargs):
        new_colors = copy.deepcopy(self.default_colors)
        for elem in new_colors.colors:
            if elem in kwargs:
                if isinstance(kwargs[elem],dict):
                    for color_type in kwargs[elem]:
                        new_colors.colors[elem][color_type] = kwargs[elem][color_type]
                else:
                    new_colors.colors[elem]["active"] = kwargs[elem]
                    new_colors.colors[elem]["inactive"] = kwargs[elem]
        return new_colors

    def parse_default_args(self,**kwargs):
        params = {}
        elem_colors = self.parse_colors(**kwargs)
        for full_arg in vars(self):
            if(re.search("^default_", full_arg)):
                arg = re.sub("default_","",full_arg)
                if(arg in kwargs):
                    params[arg] = kwargs[arg]
                else:
                    params[arg] = getattr(self, full_arg)
        return params, elem_colors    

class text_boxes(UI_elems):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.boxes = {}

    def add_box(self, loc, box_name, **kwargs):
        params, colors = super().parse_default_args(**kwargs)

        new_box = UI_elem(loc, colors, params)
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
                if input_box.interact == True:
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
            input_box.display_elem(screen)

    def get_texbox_value(self, key):
        if key in self.boxes:
            return self.boxes[key].text
        else:
            print("Box with identifier {key} not found".format(key = key))


                


        


class button:
    def __init__(self, **kwargs):
        pass

class buttons:
    def __init__(self, **kwargs):
        self.default_font_size = 32
        self.default_color = pg.Color('dodgerblue2') 
        self.default_color_grad = pg.Color('lightskyblue3')
        self.default_match_size = True
        self.default_min_width = False
        self.default_size = (200, 50)
        self.default_use_grad = True
        self.default_text_color = pg.Color('white')

        for elem in vars(self):
            if elem in kwargs:
                setattr(self, elem, kwargs[elem])

        self.buttons = {}

    def add_button(self, loc, text, **kwargs):
        pass


def init_pygame(size):
    pg.init()
    screen = pg.display.set_mode(size)
    clock  = pg.time.Clock()
    return screen, clock

