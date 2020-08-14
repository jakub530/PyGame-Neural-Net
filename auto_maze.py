import numpy as np

class player:
    def __init__(self):
        self.start_pos = np.array([50,900])
        self.start_speed =  np.array([2,0])
        self.start_acc =  np.array([0,-0.1])
        
        self.pos = start_pos
        self.speed = start_speed
        self.acc = start_acc

    def update(self):
        self.pos += self.speed
        self.speed += self.acc

def generate_rects(left,top,width,height):
    y_0 = int((top+height)/2)
    x_0 = 150
    d_x = 200
    while(x_0 < 2500):
        x_0 += d_x
    

