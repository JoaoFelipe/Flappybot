import os


# Numpy
from numpy import *
# PIL
import Image
# PyWin
import win32gui, win32ui, win32con

# Flappybot
from const import *

def arg_max(counter):
    return max(counter.items() or [(None, None)], key=lambda x: x[1])[0]

def flip_coin(p):
    return random.random() < p

def screen_grab(box=None):
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
    Image.fromarray(uint8(arr)).save(os.getcwd() + '\\screenshots\\plot_snap__' + str(int(time.time())) + '.png', 'PNG')

def group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i+n]
        if len(val) == n:
            yield tuple(val)

def rect_collision(rect1, rect2):
    return not (
        (rect1[0] > rect2[0] + rect2[2] - 1) or
        (rect1[1] > rect2[1] + rect2[3] - 1) or
        (rect2[0] > rect1[0] + rect1[2] - 1) or
        (rect2[1] > rect1[1] + rect1[3] - 1)
    )

def dilate_rect(rect, d):
    return (rect[0] - d, rect[1] - d, rect[2] + 2*d, rect[3] + 2*d)