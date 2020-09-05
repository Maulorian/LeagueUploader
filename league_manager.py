import os
import subprocess

from pywinauto.application import Application
import pywinauto.keyboard as keyboard

EXE = 'League of Legends.exe'
LEAGUE_PATH = f'C:\\Riot Games\\League of Legends\\Game\\{EXE}'

KEYBINDS = ['1', '2', '3', '4', '5', 'a', 'z', 'e', 'r', 't']

# def open_replay():
#     obs_dir_path = '\"C:\\Program Files\\obs-studio\\bin\\64bit\"'
#     start_recording_command = f'cd {obs_dir_path} & {OBS_EXE_STRING}'
#     subprocess.Popen(start_recording_command, shell=True, stdout=subprocess.DEVNULL)


def select_summoner(position):
    keybind = KEYBINDS[position]
    print(f"[LEAGUE MANAGER] - Selecting summoner in position {position} with keybind {keybind}")

    select_summoner_keybind = f'{{{keybind} down}}{{{keybind} up}}' * 2
    commands = f'{select_summoner_keybind}'
    keyboard.send_keys(commands)


def start_recording():
    print('[LEAGUE MANAGER] - Start Recording')
    keyboard.send_keys('{F10 down}{F10 up}')


def close_game():
    print('[LEAGUE MANAGER] - Closing')
    close_command = f'TASKKILL /F /IM \"{EXE}\"'
    print(close_command)
    subprocess.Popen(close_command, shell=True)
