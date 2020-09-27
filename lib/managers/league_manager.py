import os
import subprocess

import pywinauto
from cassiopeia import Region, Side
from pywinauto.application import Application
import pywinauto.keyboard as keyboard

from lib.managers.programs_manager import running
from lib.utils import pretty_log


RECORDING_COMMAND = '{F10 down}{F10 up}'
FOG_KEYBINDS = {
    Side.blue: 'F1',
    Side.red: 'F2',
}
LEAGUE_EXE = 'League of Legends.exe'
LEAGUE_PATH = 'C:\\Riot Games\\League of Legends\\'
GAME = 'Game\\'
BUGSPLAT_EXE = 'BsSndRpt.exe'
KEYBINDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
LOCALE = 'en_GB'
# LOCALE = 'ko_KR'
import os


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


REGION_IDS = {
    Region.korea.value: 'KR',
    Region.europe_west.value: 'EUW1'
}

@pretty_log
def start_game(region, match_id, encryption_key):
    region_id = REGION_IDS[region]
    game_arguments = f'spectator spectator.{region_id.lower()}.lol.riotgames.com:80 {encryption_key} {match_id} {region_id}'
    # print(game_arguments)
    with cd(LEAGUE_PATH + GAME):
        FNULL = open(os.devnull, 'w')
        subprocess.Popen([LEAGUE_EXE, game_arguments, f"-Locale={LOCALE}", "-GameBaseDir=.."], stdout=FNULL,
                         stderr=subprocess.STDOUT)


def select_summoner(position):
    app = Application().connect(path=LEAGUE_PATH + GAME + LEAGUE_EXE)
    app_dialog = app.top_window()
    from pywinauto import mouse
    import win32api
    x, y = win32api.GetCursorPos()
    print(x, y)

    app_dialog.set_focus()

    keybind = KEYBINDS[position]
    select_summoner_command = f'{{{keybind} down}}{{{keybind} up}}' * 2

    print(f"[LEAGUE MANAGER] - Selecting summoner in position {position} with keybind {keybind}")

    mouse.move(coords=(x, y))

    app_dialog.type_keys(select_summoner_command)

def adjust_fog(side):
    keybind = FOG_KEYBINDS[side]
    select_fog_command = f'{{{keybind} down}}{{{keybind} up}}'

    keyboard.send_keys(select_fog_command)

def toggle_recording():
    print('[LEAGUE MANAGER] - Toggling Recording')
    keyboard.send_keys(RECORDING_COMMAND)





def bugsplat():
    return running(BUGSPLAT_EXE)


@pretty_log
def kill_bugsplat():
    close_command = f'TASKKILL /F /IM \"{BUGSPLAT_EXE}\"'
    subprocess.Popen(close_command, shell=True)


def enable_runes():
    print('[LEAGUE MANAGER] - Enabling Runes')

    keyboard.send_keys('{c down}{c up}')
