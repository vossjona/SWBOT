# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 13:48:17 2023

@author: Jonas
"""
import pyautogui as pg
import time
from PIL import ImageGrab
import cv2
import win32api
import win32.lib.win32con as win32con
import win32gui
import numpy as np
import random
import os
import sys
import pytesseract
import re

#%%
if __name__ == "__main__":
    print("This only contains functions")
    
    
#%% Handling the emulator
def bringWindowToFront(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
    win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)


def minimizeWindow(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    
    
def list_windows():
    def callback(hwnd, windows):
        windows.append((hwnd, win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd)))
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows


def findEmulator():
    for hwnd, title, cls in list_windows():
        if ("BLUESTACKS APP PLAYER" in title.upper()):
            bringWindowToFront(hwnd)
            # print(f"{hwnd}: {title} ({cls})")
            emulator = get_window_rect(hwnd)
            handle = hwnd
            return emulator, handle, title
        elif ("NOXPLAYER" in title.upper()):
            bringWindowToFront(hwnd)
            # print(f"{hwnd}: {title} ({cls})")
            emulator = get_window_rect(hwnd)
            handle = hwnd
            return emulator, handle, title

    print("Can't find either Bluestacks nor Nox")




def get_window_rect(hwnd):
    """
    Can find the origin and dimensions of a window client.
    Excludes the title bar and borders.

    Parameters
    ----------
    hwnd : int
        Window handle.

    Returns
    -------
    x : int
        x position of client origin.
    y : int
        y position of client origin.
    w : int
        width of window.
    h : int
        height of window.

    """
    """
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return (x, y, w, h)
    """
    rect = win32gui.GetClientRect(hwnd)
    x, y = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    return (x, y, w, h)


def takeScreenshotOfEmulator():
    emulator, _, _ = findEmulator()
    frame = (emulator[0], emulator[1], emulator[0] + emulator[2], emulator[1] + emulator[3])
    screenshot = ImageGrab.grab(bbox=(frame), all_screens=True)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    return screenshot


#%% Handling Buttons
def calcScale(): 
    emulator, _, title = findEmulator()
    original_resolution = (1280, 720)
    if title.upper() == "BLUESTACKS APP PLAYER":
        scale = ((emulator[2]-33) / original_resolution[0], # x
                 (emulator[3]-33) / original_resolution[1], # y
                 (emulator[2]-33) / original_resolution[0], # w
                 (emulator[3]-33) / original_resolution[1]) # h
    elif title.upper() == "NOXPLAYER":
        scale = ((emulator[2]-44) / original_resolution[0], # x
                 (emulator[3]-34) / original_resolution[1], # y
                 (emulator[2]-44) / original_resolution[0], # w
                 (emulator[3]-34) / original_resolution[1]) # h
    return scale


def resizeAndGreyscale(name):
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.join(getattr(sys, '_MEIPASS'), os.path.dirname(os.path.abspath(__file__)))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    path = base_path + f"/buttons/{name}.png"
    button_image = cv2.imread(path)
    button_image = cv2.cvtColor(button_image, cv2.COLOR_BGR2GRAY) 
    scale = calcScale()
    
    dim = (round(button_image.shape[1] * scale[0]), round(button_image.shape[0] * scale[1]))
    button_image = cv2.resize(button_image, dim)
    return button_image


def findButton(name):
    button_image = resizeAndGreyscale(name)
    screenshot = takeScreenshotOfEmulator()
    
    result = cv2.matchTemplate(screenshot, button_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val > 0.75:
        button_x, button_y = max_loc
        button_h, button_w = button_image.shape
    
        
        button = button_x, button_y, button_w, button_h
        return button
    
    else:
        # print("Cannot find button: ", name)
        return


#%% Clicking and dragging
def break_screen_save():
    if findButton("RunBeendet") is not None:
        Drag()
        time.sleep(1)


def Click(button, random_click = True):
    emulator, _, _ = findEmulator()
    
    if isinstance(button, str):
        button = findButton(button)
    
    if random_click == False:
        button_x, button_y = button[0], button[1]
        win32api.SetCursorPos((button_x, button_y))
        click_time = 30 / 1000
    else:
        button_x = int(button[0] + random.random() * button[2] + emulator[0])
        button_y = int(button[1] + random.random() * button[3] + emulator[1])
        click_time = 20 / 1000 + 10 / 1000 * random.random()
        # print(click_time)
        win32api.SetCursorPos((button_x, button_y))
        
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, button_x, button_y, 0, 0)
    time.sleep(click_time)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, button_x, button_y, 0, 0)


def Drag(random_drag = True):
    emulator, _, _ = findEmulator()
    scale = calcScale()
    if random_drag == False:
        win32api.SetCursorPos(())
        pg.drag(50, -240, 0.4, button='left')
    else:
        drag_time = 0.25 + 0.2 * random.random()
        drag_start_position = (int(emulator[0] + 0.2 * emulator[2] + random.random() * 0.6 * emulator[2]),
                               int(emulator[1] + 0.4 * emulator[3] + random.random() * 0.5 * emulator[3]))
        drag_vector = (int(scale[0] * random.random() * 120 + scale[0] * -60), int(scale[1] * random.random() * 50 + scale[0] * -250))
        win32api.SetCursorPos((drag_start_position))
        pg.drag(drag_vector[0], drag_vector[1], drag_time, button='left')


#%% Energy Checks
def filterStringForNumbers(string):
    number = ''.join(char for char in string if char.isdigit() or char == '.')
    return int(number)


def checkEnergyStatus():
    emulator, _, _ = findEmulator()
    scale = calcScale()
    energy_symbol = findButton("Energy_Status")
    frame = (energy_symbol[0] + 30*scale[0] + emulator[0],
             energy_symbol[1] + 5*scale[1] + emulator[1],
             energy_symbol[0] + 109*scale[2] + emulator[0], 
             energy_symbol[1] + 45*scale[3] + emulator[1])

    screenshot = ImageGrab.grab(bbox=(frame), all_screens=True)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    cv2.imwrite("Energy.png", screenshot)
    
    text = pytesseract.image_to_string(screenshot)
    print(text)
    energy = filterStringForNumbers(text)
    return energy


def fillEnergy():
    while checkEnergyStatus() < 150:
        Click("Plus")
        time.sleep(0.5)
        Click("Truhe")
        time.sleep(0.5)
        try:
            Click("Annehmen")
            time.sleep(0.5)
            Click("Schliessen")   
        except:
            print("Truhe ist leer")
            time.sleep(0.5)
            Click("Schliessen")                
            break


#%% TOA specific functions
def switchTeam(team_no):
    scale = calcScale()
    Click("Toa_Team")
    time.sleep(1)
    team_bearbeiten = findButton("Toa_Team_Bearbeiten")
    
    team_1 = np.array(team_bearbeiten)
    team_1[1] = team_1[1] + 90*scale[1]
    
    team_2 = np.array(team_bearbeiten)
    team_2[1] = team_2[1] + 180*scale[1]
    
    team_3 = np.array(team_bearbeiten)
    team_3[1] = team_3[1] + 270*scale[1]
    
    teams = np.concatenate((team_1, team_2, team_3), axis=0).reshape(3,4)   
    
    Click(teams[team_no])
    time.sleep(0.5)


def checkEnergyStatusToa():
    emulator, _, _ = findEmulator()
    scale = calcScale()
    energy_symbol = findButton("Energy_Status")
    frame = (energy_symbol[0] + 35*scale[0] + emulator[0],
             energy_symbol[1] + 5*scale[1] + emulator[1],
             energy_symbol[0] + 132*scale[2] + emulator[0], 
             energy_symbol[1] + 45*scale[3] + emulator[1])

    screenshot = ImageGrab.grab(bbox=(frame), all_screens=True)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # cv2.imwrite("Energy.png", screenshot)
    
    text = pytesseract.image_to_string(screenshot)
    print(text)
    energy = filterStringForNumbers(text[0:3])
    return energy


#%% Rune Efficiency
def extract_stats(text, keywords):
    content = {}
    for keyword in keywords:
        content[keyword] = []
        start_indices = [m.start() for m in re.finditer(keyword, text)]
        for start_index in start_indices:
            end_index = text.find("\n", start_index)
            if "%"  in text[start_index+len(keyword):end_index]:
                content[keyword + "_percent"] = text[start_index+len(keyword):end_index]
            else:
                content[keyword] = text[start_index+len(keyword):end_index]
    
    for key, value in content.items():
        # check if value is empty or contains only non-numeric characters
        if not value or not any(char.isdigit() for char in value):
            content[key] = 0
        else:
            # keep only digits in value
            content[key] = ''.join(filter(str.isdigit, value))
            content[key] = int(content[key])
    return content


def readRune():
    emulator, _, _ = findEmulator()
    scale = calcScale()
    rune_anchor = findButton("Rune_Schliessen")
    frame = (rune_anchor[0] + emulator[0] - 480*scale[0],
             rune_anchor[1] + emulator[1] + 90*scale[1], # 60 for main stat, 90 for sub-stats only
             rune_anchor[0] + emulator[0] - 140*scale[0], 
             rune_anchor[1] + emulator[1] + 270*scale[1])

    screenshot = ImageGrab.grab(bbox=(frame), all_screens=True)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    _, screenshot= cv2.threshold(screenshot, 95, 255, cv2.THRESH_BINARY)
    screenshot = cv2.bitwise_not(screenshot)
    # Inverted screenshot in black and white
    
    cv2.imwrite("Rune.png", screenshot)
    
    text = pytesseract.image_to_string(screenshot)
    print(text)
    keywords =  ["HP", "ATK", "DEF", "SPD", "Krit. Rate", "Krit. Schdn", "RES", "ACC"]
    stats = extract_stats(text, keywords)
    return stats


class Rune:
    def __init__(self, HP_percent=0, DEF_percent=0, ATK_percent=0, SPD=0, CR=0, CD=0,
                 ACC=0, RES=0, HP=0, DEF=0, ATK=0, level=0):
        self.HP_percent = HP_percent
        self.DEF_percent = DEF_percent
        self.ATK_percent = ATK_percent
        self.SPD = SPD
        self.CR = CR
        self.CD = CD
        self.ACC = ACC
        self.RES = RES
        self.HP = HP
        self.DEF = DEF
        self.ATK = ATK
        self.level = level
        
    
        
    def efficiency(self):
        relative_stats = [self.HP_percent/40, self.DEF_percent/40, self.ATK_percent/40,
                          self.SPD/30, self.CR/30, self.CD/30, self.ACC/40,
                          self.RES/40, self.HP/1875, self.DEF/100, self.ATK/100]
        efficiency = 0
        for i in range(len(relative_stats)):
            efficiency += relative_stats[i]
        efficiency = (1 + efficiency) / 2.8 
        return efficiency
        
    
def initRune():
    rune = readRune()
    HP_percent = rune.get("HP_percent", 0)
    DEF_percent = rune.get("DEF_percent", 0)
    ATK_percent = rune.get("ATK_percent", 0)
    SPD = rune.get("SPD", 0)
    CR = rune.get("Krit. Rate_percent", 0)
    CD = rune.get("Krit. Schdn_percent", 0)
    ACC = rune.get("ACC_percent", 0)
    RES = rune.get("RES_percent", 0)
    HP = rune.get("HP", 0)
    DEF = rune.get("DEF", 0)
    ATK = rune.get("ATK", 0)
    rune = Rune(HP_percent=HP_percent, DEF_percent=DEF_percent, ATK_percent=ATK_percent, SPD=SPD, CR=CR, CD=CD,
                 ACC=ACC, RES=RES, HP=HP, DEF=DEF, ATK=ATK, level=0)
    return rune