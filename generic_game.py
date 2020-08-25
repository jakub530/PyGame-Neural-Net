import numpy as np
import pygame as pg

class gen_player_cloud:
    def __init__ (self, num_players, player_class):
        self.init_players(num_players, player_class)
        self.set_random_colors()
        self.tick = 0

    def init_players(self, num_players, player_class):
        self.active_players_num = num_players
        self.players = []
        self.ticks = []
        self.last_dist = []
        for index in range(num_players):
            self.players.append(player_class())
            self.ticks.append(0)
            self.last_dist.append(0)

    def modify_colors(self, sorted_scores):
        for ind, player_ind in enumerate(sorted_scores):
                    new_color = self.validate_color(255*ind/len(self.players))
                    self.players[player_ind].color = (0,0,new_color)
                    if(ind<20):
                        winner_color = self.validate_color((255 * (20-ind))/20)
                        self.players[player_ind].color = (0,winner_color,0)

    def get_best_players(self):
        scores = np.array([self.players[i].score for i in range(len(self.players))])#  np.array(self.ticks)
        arg_sorted_scores = np.argsort(scores)
        arg_sorted_scores = arg_sorted_scores[::-1]
        self.modify_colors(arg_sorted_scores)
            
        return arg_sorted_scores

    def reset_players(self):
        self.tick = 0
        self.active_players_num = len(self.players)
        for ind, player in enumerate(self.players):
            player.reset_player()
            self.ticks[ind] = 0

    def validate_color(self, ind):
        val_ind = int(max(min(255,ind),0))
        return val_ind

    def set_random_colors(self):
        for player in self.players:
            player.color = list(np.random.choice(range(256), size=3))

    def get_next_active_player(self, current_index, reverse = False):
        start_index = current_index
        delta = 1
        if reverse:
            delta = -1
        while(True):
            current_index += delta
            if current_index < 0 or current_index >= len(self.players):
                return start_index
            else:
                if self.players[current_index].active:
                    return current_index
            
    def update_players(self, screen, board, nn_outputs, nn_inputs):
        self.tick+=1
        active_players = True

        for ind, player in enumerate(self.players):
            if player.active:
                deactivate_flag, nn_inputs[ind] = player.update(board, screen, nn_outputs[ind])
                if deactivate_flag:
                    self.active_players_num -= 1

        if self.active_players_num == 0:
            active_players = False

        return active_players, nn_inputs

    def draw_players(self,screen):
        for player in self.players:
            if player.active:
                player.draw(screen)

class gen_player:
    def __init__(self):
        self.active = True
        self.pos = self.start_pos.copy()
        self.speed = self.start_speed.copy()
        self.acc = self.start_acc
        self.ticks = 0

    def update_nn_inputs(self, board):
        #Specific
        print("No specific nn inputs update")

    def apply_nn_outputs(self, nn_outputs):
        #Specific
        print("No specific nn outputs application")

    def apply_specific_movement(self):
        #Specific
        print("No specific movement implemented")
        pass

    def move_player(self, nn_outputs):
        #Generic
        self.apply_nn_outputs(nn_outputs)
        self.pos += self.speed
        self.speed += self.acc
        self.apply_specific_movement()

    def reset_player(self):
        self.active = True
        self.pos = self.start_pos.copy()
        self.speed = self.start_speed.copy()
        self.acc = self.start_acc.copy()
        self.ticks = 0

    def calculate_score(self, board):
        #Specific
        print("Implement Score Calculation")
        pass

    def elimination_condition(self, board):
        #Specific
        print("Implement Elimination Condition")
        pass
        
    def update(self, board, screen, nn_outputs):
        #Generic
        deactivated = False
        new_nn_inputs = None

        if self.active == True:
            self.ticks+=1
            self.move_player(nn_outputs)    
            new_nn_inputs = self.update_nn_inputs(board)

            deactivated = self.elimination_condition(board)
            if deactivated == True:
                self.calculate_score(board)

        return deactivated, new_nn_inputs


    def draw(self, screen):
        #Specific
        print("No draw function implemented")