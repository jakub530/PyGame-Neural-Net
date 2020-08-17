import numpy as np
import pygame_lib
import nn_lib
import node_vis
import pygame as pg
import random
import copy

class player:
    def __init__(self):
        self.start_pos = np.array([50,900])
        self.start_speed =  np.array([10,0])
        self.start_acc =  np.array([0, 0 ])
        self.max_pos = 1000
        self.size = (50, 50)
        self.active = True
        
        self.pos = self.start_pos.copy()
        self.speed = self.start_speed.copy()
        self.acc = self.start_acc

    def colision_detection(self, board):
        if self.rect.collidelist(board.rects) != -1:
            miss_delta_y = board.get_miss_delta(self.pos[0], self.pos[1])
            self.active = False
            return True, miss_delta_y
        #if self.pos[0] > 2300:
        #    self.active = False
        #    return True,0

        return False, None

    def update_nn_inputs(self, board):
        input_1 = board.get_y_delta(self.pos[0], self.pos[1])/100
        input_2 = self.speed[1]/10
        return np.array([input_1])

    def move_player(self, nn_outputs):
        #print(nn_outputs)
        #self.pos[1] = nn_outputs[0]*500+1000
        self.speed[1] = nn_outputs[0]*10


        if(self.pos[0] > self.max_pos):
            self.speed[0] = 0
        #        self.pos[1] += self.speed[1]
        #else:
        self.pos += self.speed
        self.rect = pg.Rect(*self.pos,*self.size)
        self.speed += self.acc

    def reset_player(self):
        self.active = True
        self.pos = self.start_pos.copy()
        self.speed = self.start_speed.copy()
        self.acc = self.start_acc.copy()
        

    def update(self, board, screen, nn_outputs, color):
        #print("Pos is " + str(self.pos))
        deactivated = False
        new_nn_inputs = None

        if self.active == True:
            self.move_player(nn_outputs)    
            new_nn_inputs = self.update_nn_inputs(board)

            deactivated, smallest_dist = self.colision_detection(board)
            
            self.draw(screen, color)

        return deactivated, new_nn_inputs, smallest_dist

    def draw(self, screen, color):
        pg.draw.rect(screen,color, self.rect)


class obstacle:
    def __init__(self, board, pos_centre, width, gap):
        self.pos_centre = np.array(pos_centre)
        self.offset = board.box
        self.width = width
        self.gap = gap

        self.find_real_pos()
        

        self.calculate_rect()
        
    def find_real_pos(self):
        self.r_pos = np.array(self.pos_centre)+np.array(self.offset.topleft)

    def calculate_rect(self):
        self.upper_rect = pg.Rect(self.r_pos[0]-self.width/2 ,self.offset.y, self.width, self.r_pos[1]-self.offset.y-self.gap/2)
        self.lower_rect = pg.Rect(self.upper_rect.x, self.upper_rect.bottom + self.gap, self.upper_rect.w, self.offset.bottom + self.gap/2 - self.r_pos[1])

    def move(self, horizontal_speed):
        self.pos_centre = self.pos_centre - np.array([horizontal_speed, 0])
        #self.r_pos()
        if self.r_pos[0] < 0:
            return True
        else:
            self.find_real_pos()
            self.calculate_rect()

            return False

    def draw(self, screen):
        pg.draw.rect(screen,pg.Color("white"), self.upper_rect)
        pg.draw.rect(screen,pg.Color("white"), self.lower_rect)

    def get_rects(self):
        return [self.upper_rect, self.lower_rect]

    def __str__(self):
        return self.r_pos

    def __repr__(self):
        return self.r_pos





    

class board:
    def __init__(self, rect, screen,**kwargs):
        self.box = rect
        self.border_width = 10

        self.generate_border()
  
        self.obst_width = 10
        self.start_x_pos = 300
        self.start_y_pos = 400
        self.obst_dist_x = 300
        self.obst_gap_height = 250
        self.player_thershold = 1000
        self.obst_delta_min_y = self.obst_gap_height*0.5
        self.obst_delta_max_y = self.obst_gap_height
    
        self.generate_init_obstacles()
        self.screen = screen
        
    def generate_border(self):
        l_border = pg.Rect(self.box.left, self.box.top, self.border_width, self.box.height)
        r_border = pg.Rect(self.box.right - self.border_width, self.box.top, self.border_width, self.box.height)
        t_border = pg.Rect(self.box.left, self.box.top, self.box.width, self.border_width)
        b_border = pg.Rect(self.box.left, self.box.bottom - self.border_width, self.box.width, self.border_width)
        self.borders = [l_border, r_border, t_border, b_border]

    def get_miss_delta(self, pos_x, pos_y):
        for ind, obstacle in enumerate(self.obstacles):
            if(obstacle.pos_centre[0] > pos_x):
                upper_edge_dist = abs(obstacle.upper_rect.bottom - pos_y)
                lower_edge_dist = abs(obstacle.lower_rect.top - pos_y)

                min_dist = min(upper_edge_dist, lower_edge_dist)
                #print("Tets")
                return min_dist

    def get_y_delta(self, pos_x, pos_y):
        for obstacle in self.obstacles:
            if obstacle.pos_centre[0] > pos_x:
                y_delta = obstacle.pos_centre[1] + 400 - pos_y
                #print("Y Delta is {y_delta} Y pos is {y_pos} obstacle centre is {center}".format(y_delta = y_delta,y_pos = pos_y, center = obstacle.pos_centre[1]))
                return y_delta

    def add_next_obstacle(self, last_obstacle):
        if last_obstacle.pos_centre[0] < self.box.right - self.obst_dist_x:
            x_pos = self.generate_x_pos(last_obstacle.pos_centre[0])
            y_pos = self.generate_y_pos(last_obstacle.pos_centre[1])
            self.obstacles.append(obstacle(self, np.array([x_pos,y_pos]), self.obst_width, self.obst_gap_height))

    def draw(self, player_pos, player_speed):
        self.draw_border()
        self.update_obstacles(player_pos, player_speed)

    def draw_border(self):
        for border in self.borders:
            pg.draw.rect(self.screen,pg.Color("white"), border)

    def update_obstacles(self, player_pos, player_speed):
        delete_flag = False

        for obstacle in self.obstacles:
            if player_pos > self.player_thershold:
                delete_flag = obstacle.move(player_speed)
            obstacle.draw(self.screen)

        self.add_next_obstacle(self.obstacles[-1])
        if delete_flag:
            del self.obstacles[0]

        self.update_rects()

    def generate_y_pos(self, pos_y):
        random_delta = random.uniform(self.obst_delta_min_y, self.obst_delta_max_y)
        sign = random.choice([-1,1])
        if pos_y < self.obst_delta_max_y:
            sign = 1
        if pos_y > self.box.height - self.obst_delta_max_y:
            sign = -1
        #print("pos_y is {pos} random_delta {random_delta} sign {sign} obst_max_delta {obst}".format(pos = pos_y,random_delta = random_delta,sign = sign,obst = self.obst_delta_max_y))
        return pos_y + random_delta * sign

    def generate_x_pos(self, pos_x):
        return pos_x + self.obst_dist_x   

    def update_rects(self):
        self.rects = []
        for obstacle in self.obstacles:
            self.rects += obstacle.get_rects()
        self.rects += self.borders
    
    def reset(self):
        self.obstacles = copy.deepcopy(self.init_obstacles)

    def generate_init_obstacles(self):
        self.obstacles = []
        x_pos = self.start_x_pos
        y_pos = self.start_y_pos

        self.obstacles.append(obstacle(self, np.array([x_pos,y_pos]), self.obst_width, self.obst_gap_height))

        while(self.obstacles[-1].r_pos[0] < self.box.width - self.obst_dist_x):
            self.add_next_obstacle(self.obstacles[-1])
        self.init_obstacles = copy.deepcopy(self.obstacles)
        self.update_rects()

    

class player_cloud:
    def __init__ (self, num_players):
        self.init_players(num_players)
        self.gen_colors()
        self.tick = 0

    def init_players(self, num_players):
        self.active_players_num = num_players
        self.players = []
        self.ticks = []
        self.last_dist = []
        for index in range(num_players):
            self.players.append(player())
            self.ticks.append(0)
            self.last_dist.append(0)

    def get_best_players(self):
        scores = np.array(self.ticks)
        #print(self.last_dist)
        scores = scores * 1000 - np.array(self.last_dist)
        arg_sorted_scores = np.argsort(scores)
        arg_sorted_scores = arg_sorted_scores[::-1]
        for ind, color_ind in enumerate(arg_sorted_scores):
            new_color = self.validate_color(255*ind/len(self.players))
            self.colors[color_ind] = (0,0,new_color)
            if(ind<20):
                winner_color = self.validate_color((255 * (20-ind))/20)
                self.colors[color_ind] = (0,winner_color,0)
            
        #print("Tick")

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

    def gen_colors(self):
        self.colors = []
        for ind in range(len(self.players)):
            color = list(np.random.choice(range(256), size=3))
            self.colors.append(color)
            
    def update_players(self, screen, board, nn_outputs, nn_inputs):
        self.tick+=1
        status = 1
        max_dist = 0

        for ind, player in enumerate(self.players):
            if player.active:
                deactivate_flag, nn_inputs[ind], smallest_dist = player.update(board, screen, nn_outputs[ind], self.colors[ind])
                max_dist = max(max_dist, player.pos[0])
                if deactivate_flag:
                    self.active_players_num -= 1
                    self.ticks[ind] = self.tick
                    self.last_dist[ind] = smallest_dist

        if self.active_players_num == 0:
            status = 0

        return max_dist, status, nn_inputs
        


        



def main_game():
    done = False
    screen,clock = pygame_lib.init_pygame((2560,1440), True)

    box = pg.Rect(0,600,2560,840)
    game_board = board(box, screen)
    player_char = player(screen)

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key==pg.K_ESCAPE:
                    done = True
        screen.fill((30, 30, 30))
        
        game_board.draw(player_char.pos[0], player_char.speed[0])
        #game_board.draw_obstacles(player_char.pos[0], player_char.speed[0])
        player_char.update()
        pg.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    pg.init()
    main_game()
    pg.quit()

    
    

