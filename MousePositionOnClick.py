# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 13:34:46 2023

@author: Jonas
"""

import win32api
import win32.lib.win32con as win32con
import time


positions = []

def get_mouse_pos():
    x, y = win32api.GetCursorPos()
    return (x, y)

while True:
    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON):
        positions.append(get_mouse_pos())
        print(positions[-1])
        time.sleep(.5)

    
print(positions)