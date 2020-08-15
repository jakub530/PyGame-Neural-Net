import numpy as np
import pygame_lib
import nn_lib
import node_vis
import pygame as pg
import random

class player:
    def __init__(self, screen):
        self.start_pos = np.array([50,900])
        self.start_speed =  np.array([10,0])
        self.start_acc =  np.array([0, 0 ])
        self.screen = screen
        self.max_pos = 1000
        self.size = (50, 50)
        
        self.pos = self.start_pos
        self.speed = self.start_speed
        self.acc = self.start_acc

    def update(self):
        if(self.pos[0] > self.max_pos):
            self.pos[1] += self.speed[1]
        else:
            self.pos += self.speed
        self.speed += self.acc
        self.draw()

    def draw(self):
        pg.draw.rect(self.screen,pg.Color("red"), pg.Rect(*self.pos,*self.size))


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
        if player_pos > 1000:
            self.move_obstacles(player_speed)
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
        self.start_x_pos = 100
        self.start_y_pos = 400
        self.obst_dist_x = 200
        self.obst_gap_height = 100
        self.obst_gap_min_y = self.obst_gap_height
        self.obst_gap_max_y = self.obst_gap_height*2

        tmp_x_pos = self.start_x_pos
        tmp_y_pos = self.start_y_pos
        while(tmp_x_pos < self.box.width):
            tmp_y_pos = self.gen_y_pos(tmp_y_pos)
            self.gen_obstacle(tmp_x_pos,tmp_y_pos)
            tmp_x_pos = self.gen_x_pos(tmp_x_pos)

    






#def generate_rects(rect, p_position):

    #y_0 = int((top+height)/2)
    #x_0 = 150
    #d_x = 200
    #while(x_0 < 2500):
    #    x_0 += d_x

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

    
    

