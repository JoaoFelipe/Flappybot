# PyWin
import win32api, win32con

# Flappybot
from const import *

def left_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    #time.sleep(.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    print "Click."          #completely optional. But nice for debugging purposes

def mouse_pos(x, y):
    win32api.SetCursorPos((X_PAD + x, Y_PAD + y))
     
def get_coords():
    x,y = win32api.GetCursorPos()
    x = x - X_PAD
    y = y - Y_PAD
    return x, y
