import os
import subprocess
import pywinauto.keyboard as keyboard

from cassiopeia import Region, Side
from pywinauto.application import Application
from lib.managers.programs_manager import running
from lib.utils import pretty_log, cd

RECORDING_COMMAND = '{F10 down}{F10 up}'
FOG_KEYBINDS = {
    Side.blue.value: 'F1',
    Side.red.value: 'F2',
}
LEAGUE_EXE = 'League of Legends.exe'
LEAGUE_PATH = 'C:\\Riot Games\\League of Legends\\'
GAME = 'Game\\'
BUGSPLAT_EXE = 'BsSndRpt.exe'
KEYBINDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
LOCALE = 'en_GB'

REGION_IDS = {
    Region.korea.value: 'KR',
    Region.europe_west.value: 'EUW1'
}

HOSTS = {
    Region.korea.value: 'kr3.spectator.op.gg:80',
    Region.europe_west.value: 'f2.spectator.op.gg:80'
}


@pretty_log
def start_game(region, match_id, encryption_key):
    region_id = REGION_IDS[region]
    # host_string = f'spectator.{region_id.lower()}.lol.riotgames.com:80'
    host_string = HOSTS[region]
    game_arguments = f'spectator {host_string} {encryption_key} {match_id} {region_id}'
    # print(game_arguments)
    with cd(LEAGUE_PATH + GAME):
        fnull = open(os.devnull, 'w')
        subprocess.Popen([LEAGUE_EXE, game_arguments, f"-Locale={LOCALE}", "-GameBaseDir=.."], stdout=fnull,
                         stderr=subprocess.STDOUT)


def select_summoner(position):
    app = Application().connect(path=LEAGUE_PATH + GAME + LEAGUE_EXE)
    app_dialog = app.top_window()
    from pywinauto import mouse
    import win32api
    x, y = win32api.GetCursorPos()

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
    app = Application().connect(path=LEAGUE_PATH + GAME + LEAGUE_EXE)
    app_dialog = app.top_window()
    app_dialog.set_focus()
    from pywinauto import mouse
    import win32api
    x, y = win32api.GetCursorPos()
    mouse.move(coords=(x, y))

    keyboard.send_keys(RECORDING_COMMAND)


def bugsplat():
    return running(BUGSPLAT_EXE)


def enable_runes():
    print('[LEAGUE MANAGER] - Enabling Runes')

    keyboard.send_keys('{c down}{c up}')
