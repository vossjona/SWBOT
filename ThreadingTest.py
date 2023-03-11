# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 12:52:06 2023
Used for basic threading tests.

@author: Jonas
"""

import tkinter as tk
from threading import Thread, Event

auto_run_thread = None
stop_event = Event()
 
def start_sleep():
    """
    Checks if a auto run thread is running. If not, it starts one
    that executes the sleep function.

    """
    global thread
    if thread is not None and thread.is_alive():
        print("A thread is already running.")
        return
    auto_run_thread = Thread(target=sleep)
    auto_run_thread.start()
    
def sleep():
    """
    Executes all the actual commands 
    until it is stopped by a stop event.
    Prints a status update after every cycle.

    """
    global stop_event
    stop_event.clear()
    
    while True:
        status_label.config(text="Waiting for Auto-run to be over...")
        stop_event.wait(150)
        if stop_event.is_set():
            print("Aborted")
            break
        print("Sleep finished")

def stop():
    """
    Sets the stop event in case a auto run thread is running 
    and prints a confirmation.
    Nothing happens otherwise.

    """
    global stop_event
    try:
        if auto_run_thread.is_alive(): 
            stop_event.set()
            auto_run_thread.join()
            print("Sleep stopped")
            status_label.config(text="Ready to go!")
    except:
        pass





#%% GUI

root = tk.Tk()
root.title("Waiting test")
root.geometry("250x100")

start_button = tk.Button(root, text="Start", command=start_sleep)
start_button.grid()

stop_button = tk.Button(root, text="Stop", command=stop)
stop_button.grid()

status_label = tk.Label(root, text="Ready to go!")
status_label.grid(row=2, column=0)

root.mainloop()
