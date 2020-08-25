import sys, math 
import pygame as pg
import numpy as np
from pygame import gfxdraw
import pygame_lib, nn_lib
import pygame.freetype
from pygame_lib import color
import random
import copy
import auto_maze
import node_vis
import generic_game

class main_game:
    def __init__(self):
        self.size = (2560, 1440)
        self.nn_vis_box = (1000, 400)
        self.nn_vis_off = (self.size[0]-self.nn_vis_box[0], 0)
        self.game_box = pg.Rect(0, self.nn_vis_box[1], self.size[0], self.size[1]-self.nn_vis_box[1])

        self.screen, self.clock = pygame_lib.init_pygame(self.size, False)
        self.game_board = auto_maze.board(self.game_box, self.screen)

        self.num_players = 40
        self.player_cloud = generic_game.gen_player_cloud(self.num_players, auto_maze.player)

        self.init_nn()
        self.init_UI()

        self.nn_vis = node_vis.nn_vis(self.screen, self.h_layers, self.inp_num, self.outputs , self.nn_vis_off ,self.text_boxes, ["Δy"], ["Vy"], self.nn_vis_box)
        self.weights = self.nn.generations[self.gen_num].instances[self.inst_num].extract_weights()

    def add_UI_elements(self):
        #Need to make changes to way global args is handled

        self.text_boxes.add_box((20,20),"gen_label", text = "Generation", interact = False)
        self.text_boxes.add_box((240,20),"gen_num", global_arg = "gen_num", min_width = 50, interact = False)
        self.text_boxes.add_box((240,60),"inst_num", global_arg = "inst_num", min_width = 50, interact = False)
        self.text_boxes.add_box((20,60),"instance_label", text = "Instance", interact = False)

        self.buttons.add_box((300, 60 ),"increase_inst", self.change_instance_up,   text = "+", min_width = 50, centre_text = True)
        self.buttons.add_box((360, 60),"decrease_inst", self.change_instance_down, text = "-", min_width = 50, centre_text = True)
        self.buttons.add_box((1280, 260),"advance_gen", self.advance_gen, text = "Run Single Generation", min_width = 250, centre_text = True)
        self.buttons.add_box((1280, 340),"toggle_advance_gen", self.auto_advance_gen, active_text = "Stop Auto Advancing", min_width = 250, inactive_text = "Auto Advance Gens", is_toggle = True, centre_text = True)

    def advance_gen(self):
        self.run_next_gen = True

    def auto_advance_gen(self):
        self.auto_run_gen = not self.auto_run_gen

    def change_instance_up(self):
        self.inst_num = self.player_cloud.get_next_active_player(self.inst_num)
        self.weights = self.nn.generations[self.gen_num].instances[self.inst_num].extract_weights()
        #if self.inst_num < self.num_players-1:
        #    self.inst_num += 1
        #    #Should add a method for that
        #    self.weights = self.nn.generations[self.gen_num].instances[self.inst_num].extract_weights()

    def change_instance_down(self):
        self.inst_num = self.player_cloud.get_next_active_player(self.inst_num, True)
        self.weights = self.nn.generations[self.gen_num].instances[self.inst_num].extract_weights()

        #if self.inst_num > 0:
        #    self.inst_num -= 1
        #    #Should add a method for that
        #    self.weights = self.nn.generations[self.gen_num].instances[self.inst_num].extract_weights()

    def draw_others(self):
        rect = pygame.Rect(self.size[0]-self.nn_vis_box[0],0,self.nn_vis_box[0],self.nn_vis_box[1])
        pygame_lib.fill_gradient(self.screen, pg.Color("lightgray"), pg.Color("slategray"), rect)
        pygame.draw.rect(self.screen, pg.Color("dimgray"),rect,5)

    def init_UI(self):
        self.text_boxes = pygame_lib.text_boxes(default_centre_text = True)
        self.buttons = pygame_lib.buttons()
        self.add_UI_elements()
        self.auto_change_instance_flag = True

    def auto_change_instance(self):
        if self.auto_change_instance_flag == True:
            if self.player_cloud.players[self.inst_num].active == False:
                for ind, player in enumerate(self.player_cloud.players):
                    if player.active == True:
                        self.inst_num = ind
        
    def init_nn(self):
        self.inp_num = 1
        self.h_layers = [4, 4]
        self.outputs = 1
        self.start_inputs = np.zeros(self.inp_num)
        self.nn = nn_lib.nn_tmp(self.h_layers, self.inp_num, self.outputs, self.num_players, 0)
        self.inputs_arr = [[0]] *  self.num_players
        self.outputs_arr = [None] * self.num_players
        self.val_arr = [None] * self.num_players

        self.gen_num = 0
        self.inst_num = 0
        self.run_next_gen = False 
        self.auto_run_gen = False  

    def run_game(self): 
        done = False
        while not done:
            #t = self.clock.tick(70)
            self.clock.tick(40)
            #print(self.clock.get_fps())

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key==pg.K_ESCAPE:
                        done = True
                self.text_boxes.check_events(event)
                self.buttons.check_events(event)
   
            self.screen.fill((60,60,60))
            self.draw_others()
            for n in range(self.num_players):
                self.outputs_arr[n], self.val_arr[n] = self.nn.generations[self.gen_num].instances[n].calculate_output(self.inputs_arr[n])

            status, all_inputs = self.player_cloud.update_players(self.screen, self.game_board, self.outputs_arr ,self.inputs_arr)
            self.auto_change_instance()

            if(status == 0):
                if self.run_next_gen or self.auto_run_gen:
                    best_players = self.player_cloud.get_best_players()

                    self.nn.advance_generation(best_players)
                    self.gen_num += 1
                    self.player_cloud.reset_players()
                    self.game_board.reset()

                    self.run_next_gen = False


            self.nn_vis.update_and_draw(self.text_boxes, self.val_arr[self.inst_num], self.weights)
            self.text_boxes.display_boxes(self.screen, self)
            self.buttons.display_boxes(self.screen, None)
            self.game_board.draw(self.player_cloud, 10, status)
            self.player_cloud.draw_players(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    game = main_game()
    game.run_game()
    pygame.quit()

