import ImageGrab
import os
import time

# Globals
# ------------------
X_PAD = 1060
Y_PAD = 309

def screenGrab():
    box = (X_PAD+1, Y_PAD+1, X_PAD+500, Y_PAD+700)
    im = ImageGrab.grab(box)
    #im = ImageGrab.grab()
    
    im.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) +
'.png', 'PNG')
 
def main():
    screenGrab()
 
if __name__ == '__main__':
    main()

