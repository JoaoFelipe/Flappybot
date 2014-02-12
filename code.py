import ImageGrab, ImageOps, Image, ImageChops
import os
import time
import win32api, win32con
import pygame
import cv2
import operator
from numpy import *
# Globals
X_PAD = 1060
Y_PAD = 309

WIDTH = 500
HEIGHT = 700


GET_READY = (245, 224)
START_BUTTON = (147, 572)
END_GAME_OK = (169, 502)
FLOOR_Y = 616
FLOOR_SECURITY = 200
BIRD_X = 119
BIRD_FRONT_X = 155

PLAYABLE_BOX = (X_PAD+1, Y_PAD+1, X_PAD+WIDTH, Y_PAD+FLOOR_Y)
GAME_OVER_BOX = (X_PAD+55, Y_PAD+268, X_PAD+444, Y_PAD+461)

BACKGROUND = Image.open(os.getcwd() + '\\background.png').convert('RGB')
BG_ARRAY = asarray(BACKGROUND)
BACKGROUND_GRAY = ImageOps.grayscale(BACKGROUND)
GRAY_ARRAY = asarray(BACKGROUND_GRAY)

#SURF = cv2.SURF(1)

#QUERY = asarray(ImageOps.grayscale(Image.open(os.getcwd() + '\\query.png')))
#KP_QUERY, DES_QUERY = SURF.detectAndCompute(QUERY,None)



def plot(arr):
    Image.fromarray(uint8(arr)).save(os.getcwd() + '\\plot_snap__' + str(int(time.time())) + '.png', 'PNG')

def group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i+n]
        if len(val) == n:
            yield tuple(val)

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

def biggest_opening(lis):
    if len(lis) < 2:
        return [0,0]
    first = lis[0]
    last = first - 1
    openings = []
    for x in lis:
        if x == last + 1:
            last = x
        else:
            openings.append((first, last))
            first = x
            last = first - 1
    openings.append((first, last))
    return max(openings, key=lambda opening: opening[1] - opening[0])




def find_next_pipe(img):
    for x in xrange(BIRD_FRONT_X, WIDTH - 1):
        for y in xrange(0, 616, 30):
            pixel = img.getpixel((x,y))
            if pixel:
                blanks = [y2 for y2 in xrange(0, 616) if not img.getpixel((x+5,y2))]
                opening = biggest_opening(blanks)
                return x, opening, opening[1]-opening[0]

def find_bird(non_zero_diff):
    bird_array = non_zero_diff[:,90:170]
    min_x = 500
    min_y = 1500
    max_x = -1
    max_y = -1
    for y, row in enumerate(bird_array):
        
        for x, show in enumerate(row):
           if show: 
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if min_y == 1500:
        min_y = 0
    if min_x == 500:
        min_x = 0
        max_x = 60
    return [min_x + 90, min_y, max_x - min_x, max_y - min_y]


TOTAL_DELTA = 0

def keep_flying(dt):
    global TOTAL_DELTA
    TOTAL_DELTA += dt
    if TOTAL_DELTA >= 0.55:
        TOTAL_DELTA = 0
        left_click()


LAST_DIFF = None

def game_logic(screen, dt):
    global LAST_DIFF
    im = screen_grab(box=PLAYABLE_BOX)
    
    coords = get_cords()
    if coords[0] < 0 or coords[1] < 0:
        print "Mouse out"
        return False
        #print "Mouse out"diff_rgb
        pass
    #    import pdb; pdb.set_trace()

    if im.getpixel(END_GAME_OK) == (232, 97, 1):
        return True
    if im.getpixel(GET_READY) == (244, 198, 0) or im.getpixel(START_BUTTON) == (217, 83, 14):
        return True
    #print t
    im_gray = ImageOps.grayscale(im)
    #diff_array = asarray(im_gray) - GRAY_ARRAY
    #diff_rgb = ImageChops.subtract(im,BACKGROUND)
    #diff_rgb.save(os.getcwd() + '\\diffrgb_snap__' + str(int(time.time())) + '.png', 'PNG')
    #import pdb; pdb.set_trace()
    diff = ImageChops.difference(im_gray,BACKGROUND_GRAY)
    #diff.save(os.getcwd() + '\\diff_snap__' + str(int(time.time())) + '.png', 'PNG')
    white = pygame.Color("white")
    blue = pygame.Color("blue")
    green = pygame.Color("green")
    red = pygame.Color("red")
    #print diff
    diff_array = asarray(diff)
    #temp = diff_array
    #if LAST_DIFF != None:
    #    diff_array = diff_array - LAST_DIFF
    #LAST_DIFF = temp

    
    #Image.fromarray(uint8(non_zero_diff)).save(os.getcwd() + '\\diff_snap__' + str(int(time.time())) + '.png', 'PNG')
    
    #print non_zero_diff
    #non_zero_diff = diff_array > 10
    #for y, row in enumerate(non_zero_diff):
    #    for x, show in enumerate(row):
    #        if show:
    #            screen.set_at((x, y), (diff_array[y,x],diff_array[y,x],diff_array[y,x]))

    
    #import pdb; pdb.set_trace()
    
    diff_array.flags.writeable = True
    diff_array[22:92,160:320] = zeros((70,160))
    contours,hierarchy = cv2.findContours(diff_array, 1, 2)

    raw_pipes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        rect = cv2.boundingRect(cnt)
        if 1400 < area < 1700 and 90 < rect[0] < 170:
            bird = rect
            pygame.draw.rect(screen, blue, rect, 2)
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
        pygame.draw.rect(screen, green, p, 2)
        pygame.draw.rect(screen, red, [x, 1, size_x, y - 1], 2)
        pygame.draw.rect(screen, red, [x, y + size_y, size_x, FLOOR_Y - y - size_y], 2)
        
        pipes.append(p)

    pygame.draw.line(screen, red, (0, FLOOR_Y), (WIDTH - 1, FLOOR_Y))
    #print M
    #kp2, des2 = SURF.detectAndCompute(diff_array,None)

    #FLANN_INDEX_KDTREE = 0
    #index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 1)
    #search_params = dict(checks = 1)

    #flann = cv2.FlannBasedMatcher(index_params, search_params)

    #matches = flann.knnMatch(DES_QUERY,des2,k=2)

    #good = []
    #for m,n in matches:
    #    if m.distance < 0.7*n.distance:
    #        good.append(m)
    #        kp = kp2[m.trainIdx].pt
    #        pygame.draw.rect(screen, blue, [int(kp[0]),int(kp[1]), 10, 10])
            #import pdb; pdb.set_trace()
    #print good

    #kernel = ones((3,3), 'int')
    #dilated = cv2.dilate(diff_array, kernel)
    #corners = cv2.goodFeaturesToTrack(diff_array, 5, 0.1, 55)
    #corners = int0(corners)
    #for i in corners:
    #    x, y = i.ravel()
    #    pygame.draw.rect(screen, blue, [x,y, 10, 10])

    #bird = find_bird(non_zero_diff)
    #import pdb;pdb.set_trace()
    #LAST_DIFF.flags.writeable = True
    #LAST_DIFF[bird[1]:bird[1]+80,bird[0]:bird[0]+80] = zeros((80,80))
  #print bird_array
    
    #pygame.draw.rect(screen, blue, bird, 2)
                #screen.set_at((x, y), blue)
    #print non_zero_diff
    #a = array(diff.getdata())
    #non_zero = a > 10
    #for position, value in enumerate(non_zero):
    #    x = position % (WIDTH - 1)
    #    y = (position - x) / (WIDTH - 1)
    #    if value:
    #        screen.set_at((x, y), white)

    #for x in xrange(WIDTH-1):
    #    for y in xrange(HEIGHT-1):
    #        pixel = diff.getpixel((x,y)) 
    #        print pixel
    #next_pipe = find_next_pipe(diff)
    

    
    #    return False
    
    #    final = time.time()
    #    mouse_pos(*END_GAME_OK)
    #    return False

    
    #keep_flying(dt)
    return True



def game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    start_game()
    running = True
    last_frame_time = 0
    black = pygame.Color("black")
    myfont = pygame.font.SysFont("monospace", 15)
        
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color("black"))
        current_time = time.time()
        dt = current_time - last_frame_time
        last_frame_time = current_time
        running = running and game_logic(screen, dt)
        label = myfont.render(str(dt), 1, (255,255,0))
        screen.blit(label, (100, 616))
        pygame.display.flip()

        
        """
        bird_y = find_bird(im, None)
        if bird_y > 500 and bird_y != 616:
            left_click()
        if next_pipe:
            diff.save(os.getcwd() + '\\gray_snap__' + str(int(time.time())) + '.png', 'PNG')
            if bird_y > next_pipe[1][1] and bird_y != 616:
                print 'abaixo'
                left_click()
            
            print bird_y, next_pipe
        else:
            if bird_y != 616:
                keep_flying()
        """
        #mouse_pos(BIRD_X, first_y)
        #last_t = t
        #last_y = bird_y
        #last_vm = vm




def main():
    game()
 
if __name__ == '__main__':
    #print "bla"
    main()

