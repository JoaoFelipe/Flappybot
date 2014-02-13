import os
import time
import operator
import random
from collections import Counter
from players import QLearningPlayer as Player

# PIL
import ImageGrab, ImageOps, Image, ImageChops
# PyGame
import pygame
# OpenCv
import cv2
# Numpy
from numpy import *
# PyWin
import win32api, win32con

# Flappybot
from const import *
from utils import arg_max, flip_coin, screen_grab, plot, group, rect_collision, dilate_rect
from mouse_utils import left_click, mouse_pos, get_coords

# Globals
BACKGROUND = Image.open(os.getcwd() + '\\img\\background.png').convert('RGB')
BG_ARRAY = asarray(BACKGROUND)
BACKGROUND_GRAY = ImageOps.grayscale(BACKGROUND)
GRAY_ARRAY = asarray(BACKGROUND_GRAY)




WHITE = pygame.Color("white")
BLUE = pygame.Color("blue")
GREEN = pygame.Color("green")
RED = pygame.Color("red")
BLACK = pygame.Color("black")






def grayscale_array_to_pygame(screen, diff_array):
    non_zero_diff = diff_array > 10
    #print non_zero_diff
    for y, row in enumerate(non_zero_diff):
        for x, show in enumerate(row):
            if show:
                screen.set_at((x, y), (diff_array[y,x],diff_array[y,x],diff_array[y,x]))

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


def game_logic(screen, dt, player):
    global TRACES
    im = screen_grab(box=PLAYABLE_BOX)
    #return True
    
    #im = screen_grab(box=PLAYABLE_BOX)
    im_gray = ImageOps.grayscale(im)
    
    coords = get_coords()
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
    player = Player()
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

