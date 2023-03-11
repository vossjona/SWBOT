# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 17:45:00 2023

@author: Jonas
"""

import pyautogui as pg
import tkinter as tk
import time
from threading import Thread,Event
from PIL import ImageGrab, Image
import cv2
import win32api
import win32.lib.win32con as win32con
import win32gui
import numpy as np
import json
import random
import pytesseract
import re
import WorkingFunctions as fun


window_list = fun.list_windows()

BS = fun.findEmulator()
fun.Click("Verkaufen") 




#%% Functions

def findWindow(name):
    for hwnd, title, cls in fun.list_windows():
        if name.upper() in title.upper():
            fun.bringWindowToFront(hwnd)
            # print(f"{hwnd}: {title} ({cls})")
            window = fun.get_window_rect(hwnd)
            handle = hwnd
            return window, handle, title
    print(f"Can't find the window with the title: {name}")
    
def takeScreenshotOfWindow(name):
    window, _, _ = findWindow(name)
    frame = (window[0], window[1], window[0] + window[2], window[1] + window[3])
    screenshot = ImageGrab.grab(bbox=(frame), all_screens=True)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    return screenshot