# Flappybot
from const import *
from utils import rect_collision, dilate_rect
from mouse_utils import left_click

class Player(object):

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.last_x, self.x = 0, 0
        self.last_y, self.y = 0, 0
        self.last_speed_x, self.last_speed_y = 0.0, 0.0
        self.speed_x, self.speed_y = 0.0, 0.0
        self.accel_x, self.accel_y = 0.0, 0.0
        self.pipes = 0
        self.bird = None
        self.dt = 1.0


    def see(self, dt, bird, pipes):
        if bird:
            self.last_x, self.x = self.x, bird[0] + (bird[2] / 2)
            self.last_y, self.y = self.y, bird[1] + (bird[3] / 2)
            self.last_speed_x, self.speed_x = self.speed_x, (self.x - self.last_x) / dt
            self.last_speed_y, self.speed_y = self.speed_y, (self.y - self.last_y) / dt
            self.accel_x = (self.speed_x - self.last_speed_x) / dt
            self.accel_y = (self.speed_y - self.last_speed_y) / dt

        self.pipes = pipes
        self.bird = bird
        self.dt = dt


    def next_pipe(self):
        for pipe in self.pipes:
            if pipe[0] + pipe[2] > self.x:
                return pipe
        return None

    def play(self):
        bird = self.bird if self.bird else (self.x - 30, self.y - 30, 60, 60)
        if self.y > (FLOOR_Y - FLOOR_SECURITY):
            self.fly()
        pipe = self.next_pipe()
        if pipe:
            if pipe[1] + pipe[3] < bird[1] + bird[3] - 5: #and self.speed_y >= 0:
                self.fly()
            if rect_collision([pipe[0], pipe[1] + pipe[3], pipe[2], FLOOR_Y - pipe[1] - pipe[3]], dilate_rect(bird, DILATE_COLLISION)):
                self.fly()


    def wait(self):
        pass

    def get_legal_actions(self, state):
        return [self.wait, self.play]
            


    def fly(self):
        left_click()
