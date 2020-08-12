import sys, pygame,math 
import numpy as np
from pygame import gfxdraw
import pygame_lib, nn_lib
import random

def set_color(value, min_val, max_val):
    if(value > 0):
        norm_val = int((value / max_val) * 255)
        return (0, norm_val, 0)
    else:
        norm_val = int((abs(value) / min_val) * 255)
        return (norm_val, 0, 0)

def transform_color(color):
    mult = 0.7
    return (int(color[0]*mult),int(color[1]*mult),int(color[2]*mult))


class node_vis(nn_lib.node):
    def __init__(self):
        self.val =  random.random() - 0.5
        #self.val = -1

    def set_pos(self,pos):
        self.pos = pos

    def set_size(self, diameter):
        self.radius = int(diameter/2)

    def draw_node(self, offset, min_val, max_val, surface):
        x_pos = self.pos[0] + offset[0]
        y_pos = self.pos[1] + offset[1]
        self.trans_pos = (x_pos,y_pos)
        self.color = set_color(self.val, min_val, max_val)
        self.draw_circle(surface)

    def draw_circle(self, surface):
        gfxdraw.aacircle(surface, self.trans_pos[0], self.trans_pos[1], self.radius, transform_color(self.color))
        gfxdraw.filled_circle(surface, self.trans_pos[0], self.trans_pos[1], self.radius, transform_color(self.color))
        radius_mult = 0.8
        gfxdraw.aacircle(surface, self.trans_pos[0], self.trans_pos[1], int(self.radius * radius_mult), self.color)
        gfxdraw.filled_circle(surface, self.trans_pos[0], self.trans_pos[1], int(self.radius * radius_mult), self.color)    



class layer_vis(nn_lib.layer):
    def __init__(self, size):
        super().__init__(size)

    
    def init_nodes(self):
        for ind in range(self.size):
            self.nodes.append(node_vis())


    def set_pos(self, box_dim, gaps, node_size, h_pos):
        v_gap = int((box_dim[1] - (self.size) * node_size) / (self.size + 1) )
        v_pos = [v_gap + int(node_size/2) + (v_gap + node_size) * i for i in range(self.size)]

        for ind, pos in enumerate(v_pos):
            self.nodes[ind].set_pos((h_pos, pos))
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
        min_val, max_val = self.normalize_values()
        for layer in self.layers:
            layer.draw_layer(offset, min_val, max_val, self.surface)

    def draw_line(self, prev_node, next_node, val):
        gfxdraw.line(self.surface, prev_node.trans_pos[0], prev_node.trans_pos[1], next_node.trans_pos[0], next_node.trans_pos[1], pygame_lib.color.WHITE.value)


    def draw_connections(self):
        for ind in range(self.layer_number-1):
            for prev_node in self.layers[ind].nodes:
                for next_node in self.layers[ind+1].nodes:
                    val = 0
                    self.draw_line(prev_node, next_node, val)



        

if __name__ == "__main__":
    size = (1920,1000)
    screen, clock  = pygame_lib.init_pygame(size)
    new_nn = nn_vis(screen, 7,5,8)
    new_nn.draw_nodes((1320,0))
    print("Test")
    
    while 1:
        t = clock.tick(40)
        print(t)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        X = pygame_lib.color.BLACK
        screen.fill(pygame_lib.color.BLACK.value)
        new_nn.draw_nodes((1420,0))
        new_nn.draw_connections()

        #pygame.draw.circle(screen, pygame_lib.color.GREEN.value , [100,100],10)
        pygame.display.flip()
