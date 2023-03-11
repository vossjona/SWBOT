# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 19:55:42 2023

@author: Jonas
"""

import tkinter as tk
import time
from threading import Thread,Event
import WorkingFunctions as fun

#%% Threading

autoRun_thread = None
toa_thread = None
stop_event = Event()

def _start():
    """
    Checks if a auto run thread is running. If not, it starts one
    that executes the auto_run function.
    
    """    
    global autoRun_thread
    global toa_thread

    if (autoRun_thread is not None and autoRun_thread.is_alive()):
        print("A thread is already running.")
        return
    try:
        standby_time = int(standby_entry.get())
    except:
        standby_time = 60
        error_label.config(text="This is not a valid time. Using 60 s instead.")
    autoRun_thread = Thread(target=autoRun, args= (standby_time,))
    autoRun_thread.start()


def start(): # ?? findet mode nicht
    """
    Checks if a auto run thread is running. If not, it starts one
    that executes the auto_run function.
    
    """    
    global autoRun_thread
    global toa_thread
    run_mode = mode_option.get()
    
    
    if (autoRun_thread is not None and autoRun_thread.is_alive()):
        print("A thread is already running.")
        return
    elif (toa_thread is not None and toa_thread.is_alive()):
        print("A thread is already running.")
        return
    try:
        standby_time = int(standby_entry.get())
    except:
        standby_time = 60
        error_label.config(text="This is not a valid time. Using 60 s instead.")
        
    if run_mode == "Auto-Run":
        autoRun_thread = Thread(target=autoRun, args= (standby_time,))
        autoRun_thread.start()
    elif run_mode == "TOA":
        toa_thread = Thread(target=toaProcedure, args= (standby_time,))
        toa_thread.start()
    else:
        print("Mode?")


def stop():
    """
    Sets the stop event in case a auto run thread is running 
    and prints a confirmation.
    Nothing happens otherwise.

    """
    global stop_event, autoRun_thread
    if autoRun_thread is not None and autoRun_thread.is_alive():  
        stop_event.set()
        autoRun_thread.join()
        print("Stopped")
        status_label.config(text="Ready to go!")
        stop_event.clear()
    elif (toa_thread is not None and toa_thread.is_alive()):
        stop_event.set()
        toa_thread.join()
        print("Stopped")
        status_label.config(text="Ready to go!")
        stop_event.clear()
    else:
        print("No threat alive")
        status_label.config(text="Ready to go!")
        stop_event.clear()
        pass

    
def autoRun(standby_time):
    """
    Repeats executing the auto run procedure until it is stopped by a stop event.

    Parameters
    ----------
    standby_time : int
        Time in seconds to wait before the next run.
        
    """
    global stop_event
    stop_event.clear()
    run_counter = 0
    
    
    while True:
        print("Checking...")
        _, handle, _ = fun.findEmulator()
        if (fun.findButton("RunBeendet") is not None) or (fun.findButton("Wiederholen") is not None):
            autoRunProcedure()
            run_counter += 1
            print(f"{run_counter} runs completed")
            
        if minimize.get():
            fun.minimizeWindow(handle)

        status_label.config(text="Waiting for run to be over...")
        stop_event.wait(standby_time) # Wait for the next run, but be responsive to GUI
        if stop_event.is_set():
           break
       

def autoRunProcedure():
    """
    Executes all the actual commands 

    """
    status_label.config(text="Starting new Auto Run...")
    print(".........Starting new run.........")
    fun.break_screen_save()
    try:
        fun.fillEnergy()
        if fun.checkEnergyStatus() < 20:
           stop()
    except:
        pass
    try:
        fun.Click("Verkaufen")
        time.sleep(1)
        fun.Click("Verkauf_Bestaetigen")
        time.sleep(2)
        
        # Try to sell runes
        items_available = fun.findButton("Ja")
        if items_available is not None:
            fun.Click("Ja")
            time.sleep(2)
            if fun.findButton("Ja"):
                fun.Click("Ja")
                time.sleep(2)
        else:
            fun.Click("Ok")
            time.sleep(1)
            fun.Click("Verkauf_Abbrechen")
            time.sleep(1)
        
        fun.Click("Wiederholen")
        time.sleep(1)
        fun.Click("Auto-Kampf")
        time.sleep(3)
        fun.Click("Screensaver")
        time.sleep(0.5)
    except:
        status_label.config(text="Cannot find the right button")
        print("Could not find a button.")
        stop()
        
        

def toaProcedure(standby_time):
    loss_counter = 0
    while loss_counter < 2:
        print("Checking...")
        _, handle, _ = fun.findEmulator()
        
        if fun.findButton("Toa_Victory") is not None:
            time.sleep(5)
            try: 
                fun.Click("Toa_Victory")
                time.sleep(1)
                fun.Click("Toa_Victory")
                time.sleep(1)
                try:
                    fun.Click("Toa_Okay")
                except:
                    fun.Click("Toa_Boss_Okay")
                time.sleep(1)
                try:
                    e = fun.checkEnergyStatusToa()
                    print(e)
                except:
                    e = 61
                fun.Click("Toa_Next")
                time.sleep(1)
                if not loss_counter == 0:
                    loss_counter = 0
                    fun.switchTeam(loss_counter)
                if e > 60:
                    try:
                        fun.Click("Toa_AutoRun")
                    except:
                        fun.Click("Toa_Bosskampf")
                    print("..........Next Run..........")
                else:
                    print("Out of energy")
                    status_label.config(text="Ready to go!")
                    break
            except:
                pass
        elif fun.findButton("Toa_Defeat") is not None:
            loss_counter =+ 1
            if loss_counter == 3:
                print("..........Failed with all teams..........")
                break
            time.sleep(5)
            fun.Click("Toa_Defeat")
            time.sleep(1)
            try:
                fun.Click("Toa_Defeat")
                time.sleep(2)
            except:
                pass

            try:
                okay = fun.findButton("Toa_Okay")
                fun.Click(okay)
                time.sleep(1)
            except:
                pass
            try:
                e = fun.checkEnergyStatusToa()
            except:
                e = 61
            fun.Click("Toa_Vorbereitung")
            time.sleep(1) 
            fun.switchTeam(loss_counter)
            if e > 60:
                try:
                    fun.Click("Toa_AutoRun")
                except:
                    fun.Click("Toa_Bosskampf")
                print(f"..........Failed {loss_counter} times. Try with next team..........")
            else:
                print("Out of energy")
                status_label.config(text="Ready to go!")
                break
        
        if minimize.get():
            fun.minimizeWindow(handle)
        status_label.config(text="Waiting for run to be over...")
        stop_event.wait(standby_time)
        if stop_event.is_set():
           break
     



#%% Main
if __name__ == "__main__":
    
    
    
        # Creating the GUI
    root = tk.Tk()
    root.title("SW Auto Run")
    root.geometry("450x100")
    
        # Components to input standby time
    standby_label = tk.Label(root, text="Check-up time [s]")
    standby_label.grid(row=0, column=0)
    standby_entry = tk.Entry(root)
    standby_entry.grid(row=0, column=1)
    error_label = tk.Label(root, text = "")
    error_label.grid(row=1, column=0)
    
    
        # Start/Stop Buttons
    start_button = tk.Button(root, text="Start", command=start)
    start_button.grid(row=2, column=0)
    
    stop_button = tk.Button(root, text="Stop", command=stop)
    stop_button.grid(row=2, column=1)
    
    status_label = tk.Label(root, text="Ready to go!")
    status_label.grid(row=2, column=2)
    
        # Checkbox
    minimize = tk.BooleanVar()
    minimize_checkbox = tk.Checkbutton(root, text="Minimize", variable=minimize)
    minimize_checkbox.grid(row=0, column=3)
    
        # Run counter
    # run_counter_label = tk.Label(root, text="run_counter")
    # run_counter_label.grid(row=2, column=3)
    
    
        # Create menu
    # Define options and their corresponding actions
    options = {"Auto-Run": lambda: "Auto-Run", 
               "TOA": lambda: "TOA"}
    default_option = "Auto-Run"

    # Create and pack the OptionMenu
    mode_option = tk.StringVar(root)
    mode_option.set(default_option)
    option_menu = tk.OptionMenu(root, mode_option, *options.keys(), command=lambda option: mode_option.set(options[option]()))
    option_menu.grid(row=0, column=2)

    
    run_mode = mode_option.get()
    
    root.mainloop() # Keeps the GUI running
    
    
    
    
    
    
    






