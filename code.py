import ImageGrab, ImageOps, Image, ImageChops
import os
import time
import win32api, win32con
import pygame
import cv2
import operator
from numpy import *
import win32gui
import win32ui 
# Globals
X_PAD = 1060
Y_PAD = 309

WIDTH = 500
HEIGHT = 700


GET_READY = (245, 224)
START_BUTTON = (147, 572)
END_GAME_OK = (169, 502)
FLOOR_Y = 616
FLOOR_SECURITY = 80
BIRD_X = 119
BIRD_FRONT_X = 155
DILATE_COLLISION = 10

PLAYABLE_BOX = (X_PAD+1, Y_PAD+1, X_PAD+WIDTH, Y_PAD+FLOOR_Y)
GAME_OVER_BOX = (X_PAD+55, Y_PAD+268, X_PAD+444, Y_PAD+461)

BACKGROUND = Image.open(os.getcwd() + '\\background.png').convert('RGB')
BG_ARRAY = asarray(BACKGROUND)
BACKGROUND_GRAY = ImageOps.grayscale(BACKGROUND)
GRAY_ARRAY = asarray(BACKGROUND_GRAY)


WHITE = pygame.Color("white")
BLUE = pygame.Color("blue")
GREEN = pygame.Color("green")
RED = pygame.Color("red")
BLACK = pygame.Color("black")

def grab2(box=None):
    if not box:
        box = (X_PAD+1, Y_PAD+1, X_PAD+WIDTH, Y_PAD+HEIGHT)
    w, h = box[2] - box[0], box[3] - box[1]
    hwnd = win32gui.GetDesktopWindow()
    #print hwnd
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w, h) , dcObj, (box[0], box[1]), win32con.SRCCOPY)
    #import pdb; pdb.set_trace()
    bmpinfo = dataBitMap.GetInfo()
    bmpstr = dataBitMap.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    #dataBitMap.SaveBitmapFile(cDC, os.getcwd() + '\\plot_snap__' + str(int(time.time())) + '.bmp')
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    return im

def plot(arr):
    Image.fromarray(uint8(arr)).save(os.getcwd() + '\\plot_snap__' + str(int(time.time())) + '.png', 'PNG')

def group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i+n]
        if len(val) == n:
            yield tuple(val)

def grayscale_array_to_pygame(screen, diff_array):
    non_zero_diff = diff_array > 10
    #print non_zero_diff
    for y, row in enumerate(non_zero_diff):
        for x, show in enumerate(row):
            if show:
                screen.set_at((x, y), (diff_array[y,x],diff_array[y,x],diff_array[y,x]))


# Mouse
def left_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    #time.sleep(.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    print "Click."          #completely optional. But nice for debugging purposes

def mouse_pos(x, y):
    win32api.SetCursorPos((X_PAD + x, Y_PAD + y))
     
def get_cords():
    x,y = win32api.GetCursorPos()
    x = x - X_PAD
    y = y - Y_PAD
    return x, y

# Screen
def screen_grab(box=None):
    if not box:
        box = (X_PAD+1, Y_PAD+1, X_PAD+WIDTH, Y_PAD+HEIGHT)
    im = ImageGrab.grab(box)
    #im.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) + '.png', 'PNG')
    return im

# Game
def start_game():
    im = screen_grab()
    if im.getpixel(END_GAME_OK) == (232, 97, 1):
        mouse_pos(*END_GAME_OK)
        left_click()
        time.sleep(.1)
    mouse_pos(*START_BUTTON)
    left_click()
    time.sleep(.1)
    left_click()
    time.sleep(.1)
    time.sleep(.5) 

TOTAL_DELTA = 0

def keep_flying(dt):
    global TOTAL_DELTA
    TOTAL_DELTA += dt
    if TOTAL_DELTA >= 0.55:
        TOTAL_DELTA = 0
        left_click()


def find_elements(diff_array):
    diff_array.flags.writeable = True
    diff_array[22:92,160:320] = zeros((70,160))
    contours,hierarchy = cv2.findContours(diff_array, 1, 2)

    bird = None
    raw_pipes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        rect = cv2.boundingRect(cnt)
        if 1400 < area < 1700 and 90 < rect[0] < 170:
            bird = rect
        elif area > 1500:
            raw_pipes.append(rect)
            
    pipes = []
    for pipe in group(sorted(raw_pipes, key=lambda x:x[0]), 2):
        x = min(pipe[0][0], pipe[1][0])
        y_values = [pipe[0][1], pipe[1][1]]
        min_y_index, min_y_value = min(enumerate(y_values), key=operator.itemgetter(1))
        y = min_y_value + [pipe[0][3], pipe[1][3]][min_y_index]
        size_x = min(pipe[0][2], pipe[1][2])
        size_y = y_values[min_y_index-1] - y_values[min_y_index] - y + min_y_value
        p = [x, y, size_x, size_y]
        pipes.append(p)

    return bird, pipes

def draw_game(screen, bird, pipes):
    if bird:
        pygame.draw.rect(screen, BLUE, bird, 2)
        pygame.draw.rect(screen, WHITE, dilate_rect(bird, DILATE_COLLISION), 2 )

    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, pipe, 2)
        pygame.draw.rect(screen, RED, [pipe[0], 1, pipe[2], pipe[1] - 1], 2)
        pygame.draw.rect(screen, RED, [pipe[0], pipe[1] + pipe[3], pipe[2], FLOOR_Y - pipe[1] - pipe[3]], 2)
    
    pygame.draw.line(screen, RED, (0, FLOOR_Y), (WIDTH - 1, FLOOR_Y))
    pygame.draw.line(screen, WHITE, (0, FLOOR_Y - FLOOR_SECURITY), (WIDTH - 1, FLOOR_Y - FLOOR_SECURITY))

def rect_collision(rect1, rect2):
    return not (
        (rect1[0] > rect2[0] + rect2[2] - 1) or
        (rect1[1] > rect2[1] + rect2[3] - 1) or
        (rect2[0] > rect1[0] + rect1[2] - 1) or
        (rect2[1] > rect1[1] + rect1[3] - 1)
    )

def dilate_rect(rect, d):
    return (rect[0] - d, rect[1] - d, rect[2] + 2*d, rect[3] + 2*d)


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

            


    def fly(self):
        left_click()

class PIDPlayer(Player):
    
    def __init__(self):
        super(PIDPlayer, self).__init__()
    

def game_logic(screen, dt, player):
    global TRACES
    im = grab2(box=PLAYABLE_BOX)
    #return True
    
    #im = screen_grab(box=PLAYABLE_BOX)
    im_gray = ImageOps.grayscale(im)
    
    coords = get_cords()
    if coords[0] < 0 or coords[1] < 0:
        print "Mouse out"
        return False
    
    if im.getpixel(END_GAME_OK) == (232, 97, 1):
        return True
    if im.getpixel(GET_READY) == (244, 198, 0) or im.getpixel(START_BUTTON) == (217, 83, 14):
        return True
    


    diff_array = asarray(ImageChops.difference(im_gray,BACKGROUND_GRAY))
    #grayscale_array_to_pygame(screen, diff_array)

    bird, pipes = find_elements(diff_array)
    draw_game(screen, bird, pipes)
    player.see(dt, bird, pipes)
    pygame.draw.rect(screen, BLUE, [player.x - 3, player.y - 3, 6, 6])
    font = pygame.font.SysFont("monospace", 15)
    label = font.render("%d %d"%(player.speed_y, player.accel_y), 1, (255,255,0))
    screen.blit(label, (10, FLOOR_Y + 26))
    player.play()
    

    return True

def game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    start_game()
    running = True
    last_frame_time = 0
    font = pygame.font.SysFont("monospace", 15)
    player = PIDPlayer()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)
        current_time = time.time()
        dt = current_time - last_frame_time
        last_frame_time = current_time
        running = running and game_logic(screen, dt, player)
        label = font.render(str(dt), 1, (255,255,0))
        screen.blit(label, (10, FLOOR_Y + 10))
        pygame.display.flip()


def main():
    game()
 
if __name__ == '__main__':
    main()

