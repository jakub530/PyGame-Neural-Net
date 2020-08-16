import numpy as np
import pygame_lib
import nn_lib
import node_vis
import pygame as pg
import random

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
        if self.rect.collidelist(board.obstacles) != -1:
            smallest_dist = board.get_smallest_distance(self.pos[0], self.pos[1])
            self.active = False
            return True,smallest_dist
        if self.pos[0] > 2300:
            self.active = False
            return True,0

        return False, None

    def update_nn_inputs(self, board):
        new_nn_inputs = board.get_next_gap_pos(self.pos[0], self.pos[1])
        return new_nn_inputs

    def move_player(self, nn_outputs):
        print(nn_outputs)
        #self.pos[1] = nn_outputs[0]*500+1000
        self.speed[1] = nn_outputs[0]*10


        #if(self.pos[0] > self.max_pos):
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
        

    def update(self, board, screen, nn_outputs):
        print("Pos is " + str(self.pos))
        deactivated = False
        new_nn_inputs = None

        if self.active == True:
            self.move_player(nn_outputs)    
            new_nn_inputs = self.update_nn_inputs(board)

            deactivated, smallest_dist = self.colision_detection(board)
            
            self.draw(screen)

        return deactivated, new_nn_inputs, smallest_dist

    def draw(self, screen):
        pg.draw.rect(screen,pg.Color("red"), self.rect)


#class obstacle:
    #def __init__(self, offset, pos_centre):

class board:
    def __init__(self, rect, screen, b_width = 10):
        self.generate_border(rect, b_width)
        self.box = rect
        self.obstacles = []
        self.generate_init_obstacles()
        
        self.screen = screen
        
    def generate_border(self, rect, b_width):
        l_border = pg.Rect(rect.left, rect.top, b_width, rect.height)
        r_border = pg.Rect(rect.right - b_width, rect.top, b_width, rect.height)
        t_border = pg.Rect(rect.left, rect.top, rect.width, b_width)
        b_border = pg.Rect(rect.left, rect.bottom - b_width, rect.width, b_width)
        self.borders = [l_border, r_border, t_border, b_border]

    def get_smallest_distance(self, pos_x, pos_y):
        for ind, obstacle in enumerate(self.obstacles):
            if(obstacle.x > pos_x):
                search_ind = ind

        upper_edge = self.obstacles[ind].height + self.box.y
        lower_edge = upper_edge + self.obst_gap_height

        min_dist = min(abs(pos_y - upper_edge), abs(pos_y - lower_edge))
        return min_dist


    def get_next_gap_pos(self, pos_x, pos_y):
        dist = 0
        search_ind = 0
        for ind, obstacle in enumerate(self.obstacles):
            if(obstacle.x > pos_x):
                dist = (obstacle.x - pos_x)/1000
                search_ind = ind
                break
        
        upper_edge = pos_y - (self.obstacles[ind].height + self.box.y  )
        lower_edge = (upper_edge + self.obst_gap_height)

        return [upper_edge/self.box.height, lower_edge/self.box.height, dist]

    def move_obstacles(self, player_speed):
        if self.obstacles[0].x - player_speed < 0:
            del self.obstacles[0]
            del self.obstacles[0]
        
        for ind, obstacle in enumerate(self.obstacles):
            self.obstacles[ind] = obstacle.move((-player_speed,0))
        
        if self.obstacles[-1].x < self.box.right - self.obst_dist_x:
            self.gen_obstacle(self.obstacles[-1].x + self.obst_dist_x, self.gen_y_pos(self.obstacles[-2].height+self.obst_gap_height/2))

    def draw(self, player_pos, player_speed):
        self.draw_border()
        self.draw_obstacles(player_pos, player_speed)

    def draw_border(self):
        for border in self.borders:
            pg.draw.rect(self.screen,pg.Color("white"), border)

    def draw_obstacles(self, player_pos, player_speed):
        #if player_pos > 1000:
        #    self.move_obstacles(player_speed)
        for obst in self.obstacles:
            pg.draw.rect(self.screen,pg.Color("white"), obst)

    def gen_obstacle(self, x_pos, y_pos):
        upper_part = pg.Rect(self.box.x + x_pos, self.box.y, self.obst_width, int(y_pos - self.obst_gap_height/2))
        lower_part = pg.Rect(self.box.x + x_pos, self.box.y + y_pos + self.obst_gap_height, self.obst_width, self.box.height - int(y_pos - self.obst_gap_height/2))
        self.obstacles.append(upper_part)
        self.obstacles.append(lower_part)

    def gen_y_pos(self, pos_y):
        random_delta = random.uniform(self.obst_gap_min_y, self.obst_gap_max_y)
        sign = random.uniform(-1,1)
        sign = sign/abs(sign)
        if pos_y < self.obst_gap_height*2:
            sign = 1
        if pos_y > self.box.height - self.obst_gap_height*2:
            sign = -1

        new_pos = pos_y + random_delta * sign
        #if new_pos - obst_gap_height/2 < 0:
        #    new_pos = obst_gap_height/2 
        #
        #if new_pos + obst_gap_height/2 > self.box.height:
        #    new_pos = self.box.height - obst_gap_height/2

        return new_pos

    def gen_x_pos(self, pos_x):
        return pos_x + self.obst_dist_x   

    def generate_init_obstacles(self):
        self.obst_width = 10
        self.start_x_pos = 500
        self.start_y_pos = 400
        self.obst_dist_x = 300
        self.obst_gap_height = 350
        self.obst_gap_min_y = self.obst_gap_height*0.5
        self.obst_gap_max_y = self.obst_gap_height

        tmp_x_pos = self.start_x_pos
        tmp_y_pos = self.start_y_pos
        while(tmp_x_pos < self.box.width):
            tmp_y_pos = self.gen_y_pos(tmp_y_pos)
            self.gen_obstacle(tmp_x_pos,tmp_y_pos)
            tmp_x_pos = self.gen_x_pos(tmp_x_pos)

    

class player_cloud:
    def __init__ (self, num_players):
        self.init_players(num_players)
        self.tick = 0
        pass

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
        scores = scores * 1000 - np.array(self.last_dist)
        arg_sorted_scores = np.argsort(scores)
        arg_sorted_scores = arg_sorted_scores[::-1]
        #print("Tick")

        return arg_sorted_scores

    def reset_players(self):
        self.tick = 0
        self.active_players_num = len(self.players)
        for ind, player in enumerate(self.players):
            player.reset_player()
            self.ticks[ind] = 0


    def update_players(self, screen, board, nn_outputs, nn_inputs):
        self.tick+=1
        status = 1
        for ind, player in enumerate(self.players):
            if player.active:
                deactivate_flag, nn_inputs[ind], smallest_dist = player.update(board, screen, nn_outputs[ind])
                if deactivate_flag:
                    self.active_players_num -= 1
                    self.ticks[ind] = self.tick
                    self.last_dist[ind] = smallest_dist

        if self.active_players_num == 0:
            status = 0

        return status, nn_inputs
        


        



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

    
    

