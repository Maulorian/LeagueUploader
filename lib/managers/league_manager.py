import os
import subprocess

import pywinauto
from pywinauto.application import Application
import pywinauto.keyboard as keyboard

from lib.utils import pretty_log

EXE = 'League of Legends.exe'
LEAGUE_PATH = f'C:\\Riot Games\\League of Legends\\Game\\{EXE}'
BUGSPLAT_EXE = 'BsSndRpt.exe'
KEYBINDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


def select_summoner(position):
    app = Application().connect(path=LEAGUE_PATH)
    app_dialog = app.top_window()
    from pywinauto import mouse
    import win32api
    x, y = win32api.GetCursorPos()
    print(x, y)

    app_dialog.set_focus()

    keybind = KEYBINDS[position]
    print(f"[LEAGUE MANAGER] - Selecting summoner in position {position} with keybind {keybind}")

    command = f'{{{keybind} down}}{{{keybind} up}}' * 2
    mouse.move(coords=(x, y))

    app_dialog.type_keys(command)

    # keyboard.send_keys(command)


def toggle_recording():
    print('[LEAGUE MANAGER] - Toggling Recording')
    keyboard.send_keys('{F10 down}{F10 up}')


import psutil


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def bugsplat_exists():
    return checkIfProcessRunning(BUGSPLAT_EXE)


@pretty_log
def kill_bugsplat():
    close_command = f'TASKKILL /F /IM \"{BUGSPLAT_EXE}\"'
    subprocess.Popen(close_command, shell=True)


def close_game():
    print('[LEAGUE MANAGER] - Closing')
    close_command = f'TASKKILL /F /IM \"{EXE}\"'
    print(close_command)
    subprocess.Popen(close_command, shell=True)


def enable_runes():
    print('[LEAGUE MANAGER] - Enabling Runes')

    keyboard.send_keys('{c down}{c up}')
