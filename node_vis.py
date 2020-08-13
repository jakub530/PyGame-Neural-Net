import sys, pygame,math 
import numpy as np
from pygame import gfxdraw
import pygame_lib, nn_lib
import pygame.freetype
from pygame_lib import color
import random
import copy

def set_color(value, min_val, max_val):
    if(value > 0):
        norm_val = (value / max_val) * 255
        return np.array([0, norm_val, 0], dtype=int)
    else:
        norm_val = (abs(value) / min_val) * 255
        return np.array([norm_val, 0, 0], dtype=int)

def transform_color(color):
    mult = 0.7
    return color * mult


class node_vis(nn_lib.node):
    def __init__(self):
        self.val =  random.random() - 0.5
        #self.val = -1

    def set_pos(self,pos):
        self.pos = pos

    def set_size(self, diameter):
        self.radius = int(diameter/2)

    def draw_node(self, offset, min_val, max_val, surface):
        self.trans_pos = offset + self.pos
        self.color = set_color(self.val, min_val, max_val)
        self.draw_circles(surface)

    def draw_circles(self, surface):
        self.draw_circle(surface,self.radius,transform_color(self.color))
        radius_mult = 0.8
        self.draw_circle(surface,int(self.radius * radius_mult),self.color)

    def draw_circle(self, surface, radius, color):
        gfxdraw.aacircle(surface, *self.trans_pos, radius, color)
        gfxdraw.filled_circle(surface, *self.trans_pos, radius, color)



class layer_vis(nn_lib.layer):
    def __init__(self, size):
        super().__init__(size)

    def init_nodes(self):
        for ind in range(self.size):
            self.nodes.append(node_vis())

    def set_pos(self, box_dim, gaps, node_size, h_pos):
        v_gap = int((box_dim[1] - (self.size) * node_size) / (self.size + 1) )
        v_pos = [v_gap + (v_gap + node_size) * i for i in range(self.size)]

        for ind, pos in enumerate(v_pos):
            self.nodes[ind].set_pos(np.array([h_pos, pos]))
            self.nodes[ind].set_size(node_size)

    def draw_layer(self, offset, min_val, max_val, surface):
        for node in self.nodes:
            node.draw_node(offset, min_val, max_val, surface)

class nn_vis(nn_lib.nn):
    def __init__(self, surface, h_layers, inputs, outputs, box_dim = (600,400), gaps = (10,10)):
        self.surface = surface
        self.init_layers(h_layers, inputs, outputs, layer_vis)
        self.calculate_grid(box_dim, gaps)

    def init_layers(self, h_layers, inputs, outputs, layer_type):
        super().init_layers(h_layers, inputs, outputs, layer_type)

    def calculate_grid(self, box_dim, gaps):
        max_v = int((box_dim[0] - (self.layer_number + 1) * gaps[0]) / self.layer_number )
        self.max_layer = max(self.layers[i].size for i in range(self.layer_number))
        max_h = int((box_dim[1] - (self.max_layer + 1) * gaps[1]) / self.max_layer )
        self.node_size = min(max_v, max_h)

        h_gap = int((box_dim[0] - (self.layer_number) * self.node_size) / (self.layer_number + 1) )
        h_pos = [h_gap + (h_gap + self.node_size) * i for i in range(self.layer_number)]

        for ind, layer in enumerate(self.layers):
            layer.set_pos(box_dim, gaps, self.node_size, h_pos[ind])

    def normalize_values(self):
        min_val = min(self.layers[i].nodes[j].val for i in range(self.layer_number) for j in range(self.layers[i].size))
        min_val = abs(min(min_val, -0.0001))
        max_val = max(self.layers[i].nodes[j].val for i in range(self.layer_number) for j in range(self.layers[i].size))
        max_val = abs(max(max_val, 0.0001))
        return min_val, max_val

    def draw_nodes(self, offset):
        offset = np.array(offset) + int(self.node_size / 2)
        min_val, max_val = self.normalize_values()
        for layer in self.layers:
            layer.draw_layer(offset, min_val, max_val, self.surface)

    def draw_line(self, prev_node, next_node, val):
        x = np.array(prev_node.trans_pos)

        new_color = (np.array([1,1,1]) * val * 255)

        pygame.draw.line(self.surface, new_color.astype(int), prev_node.trans_pos, next_node.trans_pos, 2)


    def draw_connections(self, mock_val):
        for ind in range(self.layer_number-1):
            for prev_node_ind, prev_node in enumerate(self.layers[ind].nodes):
                for next_node_ind, next_node in enumerate(self.layers[ind+1].nodes):
                    val = mock_val[ind][prev_node_ind][next_node_ind]
                    self.draw_line(prev_node, next_node, val)

    def set_node_val(self, inp):
        for layer_ind,layer in enumerate(self.layers):
            for node_ind,node in enumerate(layer.nodes):
                node.val = inp[layer_ind][node_ind]

    def display_values(self):
        font = pygame.font.Font(None, int(self.node_size/2))
        text_offset_s = np.array([ -int(self.node_size*3/2), -int(self.node_size/8)])
        text_offset_e = np.array([  int(self.node_size*2/3), -int(self.node_size/8)])

        for node in self.layers[0].nodes:
            text = str(np.around(node.val,2))
            if text[0]!="-":
                text = " " + text
            
            txt_surface = font.render(text, True, (255,255,255))
            screen.blit(txt_surface, node.trans_pos+text_offset_s)

        for node in self.layers[-1].nodes:
            text = str(np.around(node.val,2))
            if text[0]!="-":
                text = " " + text
            txt_surface = font.render(text, True, (255,255,255))
            screen.blit(txt_surface, node.trans_pos+text_offset_e)



def generate_value():
    return random.random()

def mock_values(inp, hidden, output, rand = False):
    layers = [inp, *hidden, output]
    values = []
    for layer_ind in range(len(layers)-1):
        tmp_val_mid = []
        for prev_ind in range(layers[layer_ind]):
            tmp_val_bot = []
            for next_ind in range(layers[layer_ind+1]):
                val = generate_value()
                tmp_val_bot.append(val)
            tmp_val_mid.append(tmp_val_bot)
        values.append(tmp_val_mid)
    return values


if __name__ == "__main__":
    size = (2000, 1000)
    box_dim = (600, 400)
    offset = (size[0]-box_dim[0], 0)

    inputs = 5
    hidden_layers = [6,6,6,6,6]
    outputs = 3

    screen, clock  = pygame_lib.init_pygame(size)
    my_nn = nn_lib.nn(hidden_layers, inputs, outputs)
    my_nn.init_weights()
    my_nn_vis = nn_vis(screen, hidden_layers, inputs,outputs , box_dim)
    


    mock_val = mock_values(inputs, hidden_layers, outputs)
    print("Test")
    my_nn_vis.draw_nodes(offset)

    break_flag = False

    while 1:
        t = clock.tick(120)
        print(t)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                break_flag = True
                pygame.quit()
                
        if(break_flag):
            break      

        screen.fill((60,60,60 ))
        output, all_values = my_nn.calculate_output(np.random.uniform(-0.2,0.2,inputs))
        my_nn_vis.draw_connections(mock_val)
        my_nn_vis.draw_nodes(offset)
        my_nn_vis.set_node_val(all_values)
        
        my_nn_vis.display_values()

        #pygame.draw.circle(screen, pygame_lib.color.GREEN.value , [100,100],10)
        pygame.display.flip()
    
    
