import os
import subprocess

from pywinauto.application import Application
import pywinauto.keyboard as keyboard

EXE = 'League of Legends.exe'
LEAGUE_PATH = f'C:\\Riot Games\\League of Legends\\Game\\{EXE}'

keys = {100: ['1', '2', '3', '4', '5'],
        200: ['a', 'z', 'e', 'r', 't']}


def select_and_record(team, role_index):
    app = Application().connect(path=LEAGUE_PATH)
    # app_dialog = app.top_window()
    # app_dialog.set_focus()
    team_keybinds = keys[team.side.value]
    key = team_keybinds[role_index]
    select_summoner_keybind = f'{{{key} down}}{{{key} up}}' * 2
    record_keybind = '^{v down}^{v up}'
    commands = f'{select_summoner_keybind}{record_keybind}'
    print(f'Sending {commands}')
    keyboard.send_keys(commands)


def select_summoner(team, role_index):
    print("Selecting summoner")
    # app = Application().connect(path=LEAGUE_PATH)
    # app_dialog = app.top_window()
    # app_dialog.maximize()
    # app_dialog.set_focus()
    team_keybinds = keys[team.side.value]
    key = team_keybinds[role_index]
    select_summoner_keybind = f'{{{key} down}}{{{key} up}}' * 2
    commands = f'{select_summoner_keybind}'
    print(f'Sending {commands}')
    keyboard.send_keys(commands)


def maximize_game():
    print('maximize_game()')
    app = Application().connect(path=LEAGUE_PATH)
    app_dialog = app.top_window()
    app_dialog.maximize()
    # app_dialog.set_focus()


def start_recording():
    keyboard.send_keys('{F10 down}{F10 up}')


def close_game():
    close_command = f"TASKKILL /F /IM {EXE}"
    print(close_command)
    subprocess.Popen(close_command, shell=True)
