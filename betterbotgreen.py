import keyboard
import time
import ctypes
#import win32api
import mss
import os
import colorama
import winsound
import cv2
import numpy as np
import PIL
import mouse
import PIL.ImageGrab
from colorama import Fore, Style, init

# Get dimensions of monitor
SCREEN_HEIGHT, SCREEN_WIDTH = (PIL.ImageGrab.grab().size)

PURPLE_R, PURPLE_G, PURPLE_B = (152, 20, 37)  # dark red, works better
#upper_red = np.uint8([[[115,47,170]]]) # upper limit on red 
#lower_red = np.uint8([[[108,30,160]]]) # lower limit on red 
upper_red = np.array([65, 255, 255])
lower_red = np.array([55, 230, 195])

TOLERANCE = 60
GRABZONE = 2
TRIGGER_KEY = "ctrl + alt"
SWITCH_KEY = "ctrl + tab"
GRABZONE_KEY_UP = "ctrl + up"
GRABZONE_KEY_DOWN = "ctrl + down"
mods = ["automatic", "semi-auto"]
modes = np.array([.1, 0])

def get_bbox():
    return (int(SCREEN_HEIGHT / 2 - GRABZONE), int(SCREEN_WIDTH / 2 - GRABZONE), \
            int(SCREEN_HEIGHT / 2 + GRABZONE), int(SCREEN_WIDTH / 2 + GRABZONE))

class TriggerBot:
    def __init__(self):
        self.toggled = False
        self.mode = 1
        self.last_reac = 0
        self.count_reac = 0
        self.sum_reac = 0
        self.avg_reac = 0
        self.found_target = False
        self.center_hsv = 0
    
    def toggle(self):
        self.toggled = not self.toggled
    
    def switch(self):
        self.mode = (self.mode + 1) % 2
        for _ in range(self.mode + 1):
            winsound.Beep(200,200)

    def click(self):
        if self.mode == 0: 
            if self.found_target:
                mouse.press(button="left")
            else:
                mouse.release(button="left")
        else:
            if self.found_target:
                mouse.click(button="left")
    
    def grab(self):
        with mss.mss() as sct:
           img = np.array(sct.grab(get_bbox()))
        return img

    def scan(self):
        start_time = time.time()
        img = self.grab()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_red, upper_red)
        self.center_hsv = hsv[GRABZONE//2,GRABZONE//2,:]
        if np.any(mask > 0):
            self.last_reac = int((time.time() - start_time) * 1000)
            self.sum_reac += self.last_reac
            self.count_reac += 1
            self.avg_reac = self.sum_reac / self.count_reac
            self.found_target = True
            self.click()
            print_banner(self)
        else:
            self.found_target = False
            self.click()



    


def print_banner(bot: TriggerBot):
    os.system("cls")
    print("""
…………………...„„-~^^~„-„„_
………………„-^*'' : : „'' : : : : *-„
…………..„-* : : :„„--/ : : : : : : : '
…………./ : : „-* . .| : : : : : : : : '|
……….../ : „-* . . . | : : : : : : : : |
………...\„-* . . . . .| : : : : : : : :'|
……….../ . . . . . . '| : : : : : : : :|
……..../ . . . . . . . .'\ : : : : : : : |
……../ . . . . . . . . . .\ : : : : : : :|
……./ . . . . . . . . . . . '\ : : : : : /
….../ . . . . . . . . . . . . . *-„„„„-*'
….'/ . . . . . . . . . . . . . . '|
…/ . . . . . . . ./ . . . . . . .|
../ . . . . . . . .'/ . . . . . . .'|
./ . . . . . . . . / . . . . . . .'|
'/ . . . . . . . . . . . . . . . .'|
'| . . . . . \ . . . . . . . . . .|
'| . . . . . . \„_^- „ . . . . .'|
'| . . . . . . . . .'\ .\ ./ '/ . |
| .\ . . . . . . . . . \ .'' / . '|
| . . . . . . . . . . / .'/ . . .|
| . . . . . . .| . . / ./ ./ """)
    print("====== Controls ======")
    print("Activate Trigger Bot :", Fore.YELLOW + TRIGGER_KEY + Style.RESET_ALL)
    print("Switch fire mode     :", Fore.YELLOW + SWITCH_KEY + Style.RESET_ALL)
    print("Change Grabzone      :", Fore.YELLOW + GRABZONE_KEY_UP + "/" + GRABZONE_KEY_DOWN + Style.RESET_ALL)
    print("==== Information =====")
    print("Mode                 :", Fore.CYAN + mods[bot.mode] + Style.RESET_ALL)
    print("Grabzone             :", Fore.CYAN + str(GRABZONE) + "x" + str(GRABZONE) + Style.RESET_ALL)
    print("Activated            :", (Fore.GREEN if bot.toggled else Fore.RED) + str(bot.toggled) + Style.RESET_ALL)
    print("Last reaction time   :", Fore.CYAN + str(bot.last_reac) + Style.RESET_ALL + " ms (" + str(
        (bot.last_reac) / (GRABZONE * GRABZONE)) + "ms/pix)")
    print("Avg reaction time    :", Fore.MAGENTA + str(bot.avg_reac) + Style.RESET_ALL)
    print("HSV LOWER: ", lower_red)
    print("HSV Upper: ", upper_red)
    print("CENTER_HSV: ", bot.center_hsv)
        
        
if __name__ == "__main__":
    bot = TriggerBot()
    print_banner(bot)
    while True:
        if keyboard.is_pressed(SWITCH_KEY):
            bot.switch()
            print_banner(bot)
            while keyboard.is_pressed(SWITCH_KEY):
                pass
        if keyboard.is_pressed(GRABZONE_KEY_UP):
            GRABZONE += 5
            print_banner(bot)
            winsound.Beep(400, 200)
            while keyboard.is_pressed(GRABZONE_KEY_UP):
                pass
        if keyboard.is_pressed(GRABZONE_KEY_DOWN):
            GRABZONE -= 5
            print_banner(bot)
            winsound.Beep(300, 200)
            while keyboard.is_pressed(GRABZONE_KEY_DOWN):
                pass
        if keyboard.is_pressed(TRIGGER_KEY):
            bot.toggle()
            print_banner(bot)
            if bot.toggled:
                winsound.Beep(440, 75)
                winsound.Beep(700, 100)
            else:
                winsound.Beep(440, 75)
                winsound.Beep(200, 100)
            while keyboard.is_pressed(TRIGGER_KEY):
                pass
        if keyboard.is_pressed("4"):
            bot.mode = 0
        if keyboard.is_pressed("3"):
            bot.mode = 1
        if bot.toggled:
 
            ##
 
            #a = win32api.GetKeyState(0x02)
            #if a < 0:
            bot.scan()
            #time.sleep(0.01)
 
            # change this to
            """
            bot.scan()
            time.sleep(0.01)
            """
            # if you dont want to hold right click to active it
