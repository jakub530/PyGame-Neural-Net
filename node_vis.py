import sys, pygame,math 
import numpy as np
from pygame import gfxdraw
import pygame_lib, nn_lib
import pygame.freetype
from pygame_lib import color
import random
import copy
import auto_maze

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
        #self.val =  random.random() - 0.5
        self.val = 0

    def set_pos(self,pos,offset):
        self.pos = pos
        self.trans_pos = offset + self.pos

    def set_size(self, diameter):
        self.radius = int(diameter/2)

    def draw_node(self, offset, min_val, max_val, surface, img, color_img):
        self.color = set_color(self.val, min_val, max_val)
        self.draw_circles_pygame(surface)
        #self.draw_circles_import(surface, img, color_img)

    def draw_circles_pygame(self, surface):
        self.draw_circle(surface,self.radius,transform_color(self.color))
        radius_mult = 0.8
        self.draw_circle(surface,int(self.radius * radius_mult),self.color)

    def draw_circles_import(self, surface, img, color_img):
        new_img = img.copy()
        color_img.fill(self.color)
        new_img.blit(color_img, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        surface.blit(new_img, self.trans_pos-np.array([self.radius,self.radius]))

    def draw_circle(self, surface, radius, color):
        gfxdraw.aacircle(surface, *self.trans_pos, radius, color)
        gfxdraw.filled_circle(surface, *self.trans_pos, radius, color)



class layer_vis(nn_lib.layer):
    def __init__(self, size):
        super().__init__(size)

    def init_nodes(self):
        for ind in range(self.size):
            self.nodes.append(node_vis())

    def set_pos(self, node_size, h_pos, v_pos, offset):
        for ind, pos in enumerate(v_pos):
            self.nodes[ind].set_pos(np.array([h_pos, pos]), offset)
            self.nodes[ind].set_size(node_size)

    def draw_layer(self, offset, min_val, max_val, surface, img, color_img):
        for node in self.nodes:
            node.draw_node(offset, min_val, max_val, surface, img, color_img)

class nn_vis(nn_lib.nn):
    def __init__(self, surface, h_layers, inputs, outputs, offset, text_boxes, box_dim = (600,400),gaps = (30,10), path = 'Graphics/Node_Grad_2.png'):
        self.surface = surface
        self.offset = offset
        self.init_layers(h_layers, inputs, outputs, layer_vis)
        self.calculate_grid(box_dim, gaps)
        self.init_node_image(path)
        self.setup_text_boxes(text_boxes)

    def update_and_draw(self, txt_boxes, values, mock_val):
        self.set_node_val(values)
        self.draw_connections(mock_val)
        self.draw_nodes(self.offset)
        self.update_txt_values(txt_boxes)
        
    def init_layers(self, h_layers, inputs, outputs, layer_type):
        super().init_layers(h_layers, inputs, outputs, layer_type)

    def init_node_image(self, path):
        node_img = pygame.image.load(path)
        self.node_img = pygame.transform.scale(node_img,(self.node_size,self.node_size))
        self.color_img = pygame.Surface(node_img.get_size()).convert_alpha()  

    def calculate_max_size(self, box_dim, gap, frame, inst, txt_box_mult = 0, txt_box_num = 0):
        allocated_space = box_dim
        framed_space = allocated_space - 2 * frame
        space_after_gaps = framed_space - gap * (inst + 1 + txt_box_num) 
        max_size = int(space_after_gaps / (inst + txt_box_num * txt_box_mult)) 
        return max_size

    def calculate_gap(self, dim, size, inst, frame, txt_box_mult = 0, txt_box_num = 0):
        available_space = dim - size * inst - size * txt_box_mult * txt_box_num - 2 * frame
        gap = int(available_space / (inst + txt_box_num + 1))
        return gap

    def calculate_node_h_pos(self, size, gap, inst, frame, txt_box_mult, txt_box_num):
        #calculates centres of the circles
        start_offset =  int(frame + (1 + (txt_box_num-1)) * gap + size * (0.5 + (txt_box_num-1)*txt_box_mult )) # offset by txt_box and radius of circle
        h_pos = [start_offset + i * (gap + size) for i in range(inst)]
        return h_pos

    def calibrate_font(self, txt_box_mult, size):
        font_size = 1
        mock_text = "-0.30"
        while(1):
            font = pygame.font.Font(None, font_size)
            txt_surface = font.render(mock_text, True, pygame.Color("white"))
            #print(str(txt_surface.get_width()) + str(txt_surface.get_height()))
            if txt_surface.get_width() > txt_box_mult * size or (20 + txt_surface.get_height()) > size * 0.8:
                self.font_size = font_size
                self.txt_field_size = (txt_surface.get_width() + 10 , txt_surface.get_height() + 10)
                return
            else:
                font_size += 1

    def calculate_txt_pos(self, frame, box_dim):
        self.txt_s_h_pos = frame + self.h_gap # tenatively for now 
        self.txt_s_v_pos = []
        for v_pos in self.v_pos[0]:
            tmp_v_pos = v_pos - self.txt_field_size[1] / 2 
            self.txt_s_v_pos.append(tmp_v_pos)

        self.txt_e_h_pos = self.h_pos[-1] + self.h_gap + self.node_size/2
        self.txt_e_v_pos = []
        for v_pos in self.v_pos[-1]:
            tmp_v_pos = v_pos - self.txt_field_size[1] / 2 
            self.txt_e_v_pos.append(tmp_v_pos)

        return 

    def calculate_grid(self, box_dim, gaps, frame = 5, txt_box_mult = 1.5, txt_box_num = 3):
        self.largest_layer = max(self.layers[i].size for i in range(self.layer_number))
        max_h = self.calculate_max_size(box_dim[0], gaps[0], frame, self.layer_number, txt_box_mult, txt_box_num)
        max_v = self.calculate_max_size(box_dim[1], gaps[1], frame, self.largest_layer)

        self.node_size = min(max_v, max_h)

        self.h_gap = self.calculate_gap(box_dim[0], self.node_size, self.layer_number, frame, txt_box_mult, txt_box_num)
        self.h_pos = self.calculate_node_h_pos(self.node_size, self.h_gap, self.layer_number, frame, txt_box_mult, txt_box_num)

        self.v_gap = []
        self.v_pos = []
        for layer in self.layers:
            self.v_gap.append(self.calculate_gap(box_dim[1], self.node_size, layer.size, frame))
            l_pos = []
            for ind in range(len(layer.nodes)):
                l_pos.append(int(frame + self.v_gap[-1] + self.node_size * 0.5 + ind * (self.v_gap[-1] + self.node_size)))
            self.v_pos.append(l_pos.copy())

        self.calibrate_font(txt_box_mult, self.node_size)
        self.calculate_txt_pos(frame, box_dim)
        
        for ind, layer in enumerate(self.layers):
            layer.set_pos(self.node_size, self.h_pos[ind], self.v_pos[ind], self.offset)

    def normalize_values(self):
        min_val = min(self.layers[i].nodes[j].val for i in range(self.layer_number) for j in range(self.layers[i].size))
        min_val = abs(min(min_val, 0.0))
        self.min_val = min_val
        max_val = max(self.layers[i].nodes[j].val for i in range(self.layer_number) for j in range(self.layers[i].size))
        max_val = abs(max(max_val, 0.0))
        self.max_val = max_val
        return min_val, max_val

    def draw_nodes(self, offset):
        self.offset = np.array(offset)
        min_val, max_val = self.normalize_values()
        for layer in self.layers:
            layer.draw_layer(self.offset, min_val, max_val, self.surface, self.node_img, self.color_img)

    def draw_line(self, prev_node, next_node, val, min_weight, max_weight):
        x = np.array(prev_node.trans_pos)
        if val > 0:
            maximum = max_weight
            base_color = np.array([0,1,0,0])
        else:
            maximum = abs(min_weight)
            base_color = np.array([1,0,0,0])
            val = abs(val)
        max_thickness = 5
        thick = max(int(max_thickness * val/maximum), 1)
        color = base_color * int(255 * (val/maximum))


        pygame.draw.line(self.surface, color, prev_node.trans_pos, next_node.trans_pos, thick)


    def draw_connections(self, weights):
        min_weight = min(weights[i][j][k] for i in range(len(weights)) for j in range(len(weights[i])) for k in range(len(weights[i][j])))
        max_weight = max(weights[i][j][k] for i in range(len(weights)) for j in range(len(weights[i])) for k in range(len(weights[i][j])))
        
        for ind in range(self.layer_number-1):
            for next_node_ind, next_node in enumerate(self.layers[ind+1].nodes):
                for prev_node_ind, prev_node in enumerate(self.layers[ind].nodes):
                    val = weights[ind][next_node_ind][prev_node_ind]
                    self.draw_line(prev_node, next_node, val, min_weight, max_weight)

    def set_node_val(self, inp):
        for layer_ind,layer in enumerate(self.layers):
            for node_ind,node in enumerate(layer.nodes):
                node.val = inp[layer_ind][node_ind]

    def format_text(self, text):
        if text[0]!="-":
            text = " " + text
        while(len(text)<5):
            text = text + "0"
        return text

    def update_txt_values(self, all_text_boxes):
        name = ["input", "output"]
        for layer_ind, layer in enumerate([self.layers[0], self.layers[-1]]):
            for ind, node in enumerate(layer.nodes):
                if all_text_boxes.elems[name[layer_ind]+"_"+str(ind)].active == False:
                    text = str(np.around(node.val,2))
                    text = self.format_text(text)
                    all_text_boxes.elems[name[layer_ind]+"_"+str(ind)].update_text(text)

    def update_inputs(self, all_text_boxes, old_inputs):
        
        inputs = old_inputs.copy()
        for ind, node in enumerate(self.layers[0].nodes):
            if all_text_boxes.elems["input_"+str(ind)].active == False:
                txtbox_value = all_text_boxes.get_texbox_value("input_"+str(ind))
                try:
                    node.val = float(txtbox_value)
                except:
                    node.val = 0
                inputs[ind] = node.val
        
        return inputs    


    def setup_text_boxes(self, all_text_boxes):
        for ind, node in enumerate(self.layers[0].nodes):
            text = str(np.around(node.val,2))
            text = self.format_text(text)
            pos = np.array([self.txt_s_h_pos, self.txt_s_v_pos[ind]]) + self.offset
            all_text_boxes.add_box(pos, "input_"+str(ind), text = text, font_size = self.font_size, min_width = self.node_size * 1.5)

        for ind, node in enumerate(self.layers[-1].nodes):
            text = str(np.around(node.val,2))
            text = self.format_text(text)
            pos = np.array([self.txt_e_h_pos, self.txt_e_v_pos[ind]]) + self.offset
            all_text_boxes.add_box((pos), "output_"+str(ind), text = text, font_size = self.font_size, min_width = self.node_size * 1.5, interact = False )


def draw_others(surface, size, box_dim):
    rect = pygame.Rect(size[0]-box_dim[0],0,box_dim[0],box_dim[1])
    pygame_lib.fill_gradient(surface, pygame.Color("lightgray"), pygame.Color("slategray"), rect)
    pygame.draw.rect(surface, pygame.Color("dimgray"),rect,5)
    

def change_instance_up(button, global_params):
    my_nn = global_params["nn"]
    current_gen = my_nn.generations[global_params["gen_number"]]
    
    if(global_params["inst_number"] < len(current_gen.instances)-1):
        global_params["inst_number"] = int(global_params["inst_number"]) + 1
        global_params["weights"] = current_gen.instances[global_params["inst_number"]].extract_weights()

def change_instance_down(button, global_params):
    my_nn = global_params["nn"]
    current_gen = my_nn.generations[global_params["gen_number"]]
    
    if global_params["inst_number"] > 0 :
        global_params["inst_number"] = int(global_params["inst_number"]) - 1
        global_params["weights"] = current_gen.instances[global_params["inst_number"]].extract_weights()

def init_UI(text_boxes, buttons):
    text_boxes.add_box((20,20),"gen_label", text = "Generation", interact = False)
    text_boxes.add_box((240,20),"gen_index", global_arg = "gen_number", min_width = 50, interact = False)
    text_boxes.add_box((240,60),"gen_index", global_arg = "inst_number", min_width = 50, interact = False)
    text_boxes.add_box((20,60),"instance_label", text = "Instance", interact = False)
    
    buttons.add_box((300, 60 ),"increase_inst", change_instance_up,   text = "+", min_width = 50, centre_text = True)
    buttons.add_box((360, 60),"decrease_inst", change_instance_down, text = "-", min_width = 50, centre_text = True)


def main():
    size = (2560, 1440)
    box_dim = (1000, 400)

    screen, clock  = pygame_lib.init_pygame(size,True)
    offset = (size[0]-box_dim[0], 0)

    box = pygame.Rect(0,box_dim[1],2560,size[1]-box_dim[1])
    game_board = auto_maze.board(box, screen)
    #player_char = auto_maze.player(screen)
    
    global_args = {}
    global_args["inst_number"] = 0
    global_args["gen_number"] = 0
    
    input_number = 3
    hidden_layers = [6,6,6,6] 
    outputs = 1
    s_inputs = [0,0,0]
    num_player = 10

    my_nn = nn_lib.nn_tmp(hidden_layers, input_number, outputs, num_player, 0)
    players = auto_maze.player_cloud(num_player)

    all_inputs = []
    all_outputs = []
    all_val = []
    for ind in range(num_player):
        all_inputs.append(s_inputs)
        all_outputs.append(None)
        all_val.append(None)
        

    current_gen = my_nn.generations[global_args["gen_number"]]
    global_args["nn"] = my_nn

    text_boxes = pygame_lib.text_boxes(default_centre_text = True)
    buttons = pygame_lib.buttons()
    init_UI(text_boxes, buttons)
    

    my_nn_vis = nn_vis(screen, hidden_layers, input_number,outputs , offset ,text_boxes, box_dim)

    global_args["weights"] = current_gen.instances[global_args["inst_number"]].extract_weights()

    break_flag = False
    event_flag = False
    start_flag = True

    done = False
    while not done:
        t = clock.tick(70)
        global_args["time"] = t
        #print(t)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                break_flag = True
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    done = True
            text_boxes.check_events(event)
            buttons.check_events(event, global_args)
                
        if(break_flag):
            break      

        screen.fill((60,60,60 ))
        draw_others(screen,size,box_dim)
        #if start_flag == False:
        #    inputs = my_nn_vis.update_inputs(text_boxes, inputs)
        #print(inputs)
        #inputs = np.random.uniform(-0.2,0.2,input_number)
        for n in range(num_player):
            all_outputs[n], all_val[n] = current_gen.instances[n].calculate_output(all_inputs[n])
        
        
        status, all_inputs = players.update_players(screen, game_board, all_outputs,all_inputs)
        if(status == 0):
            best_players = players.get_best_players()
            current_gen.retrain_nn(best_players)
            players.reset_players()

            # Sort by fitness
            # Retrain
            # Reset Pos
            # Run again
            print(players.ticks)
            print("Done")

        my_nn_vis.update_and_draw(text_boxes, all_val[0], global_args["weights"])

        text_boxes.display_boxes(screen, global_args)
        buttons.display_boxes(screen, global_args)
        game_board.draw(0, 0)
        #game_board.draw_obstacles(player_char.pos[0], player_char.speed[0])
        #player_char.update()
        pygame.display.flip()
        start_flag = False


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()    
    
    
