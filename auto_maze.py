import numpy as np
import pygame_lib
import nn_lib
import node_vis
import pygame as pg
import random
import copy
import generic_game

class player(generic_game.gen_player):
    def __init__(self):
        self.start_pos = np.array([50,900])
        self.start_speed =  np.array([10,0])
        self.start_acc =  np.array([0, 0 ])
        self.max_pos = 1000
        self.y_speed = 12
        self.size = (20, 20)
        super().__init__()

    def elimination_condition(self, board):
        if self.rect.collidelist(board.rects) != -1:
            #miss_delta_y = board.get_miss_delta(self.pos[0], self.pos[1])
            self.active = False
            return True
        return False

    def apply_nn_outputs(self, nn_outputs):
        #Specific
        self.speed[1] = nn_outputs[0]/abs(nn_outputs[0]) * self.y_speed

    def calculate_score(self, board):
        miss_delta_y = board.get_miss_delta(self.pos[0], self.pos[1])
        self.score = self.ticks * 1000 - miss_delta_y

    def apply_specific_movement(self):
        if(self.pos[0] > self.max_pos):
            self.speed[0] = 0
        self.rect = pg.Rect(*self.pos,*self.size)

    def update_nn_inputs(self, board):
        input_1 = board.get_y_delta(self.pos[0], self.pos[1])/100
        input_2 = self.speed[1]/10
        return np.array([input_1])      

    def draw(self, screen):
        pg.draw.rect(screen,self.color, self.rect)

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
        self.obst_gap_height = 60
        self.player_thershold = 1000
        self.obst_delta_min_y = self.obst_gap_height*3
        self.obst_delta_max_y = self.obst_gap_height*5
    
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

    def extract_max_pos(self, player_cloud):
        max_pos = 0
        for player in player_cloud.players:
            max_pos = max(max_pos,player.pos[0])
        return max_pos

    def draw(self, player_cloud, player_speed, status):
        self.draw_border()
        max_pos = self.extract_max_pos(player_cloud)
        self.update_obstacles(max_pos, player_speed,status)

    def draw_border(self):
        for border in self.borders:
            pg.draw.rect(self.screen,pg.Color("white"), border)

    def update_obstacles(self, player_pos, player_speed, status):
        delete_flag = False

        for obstacle in self.obstacles:
            if (player_pos > self.player_thershold) and (status == True):
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

    
    

