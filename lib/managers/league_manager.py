import configparser
import os
import random
import subprocess

import pywinauto.keyboard as keyboard
from cassiopeia import Side
from pywinauto.application import Application

from lib.constants import GAME_CFG_PATH
from lib.extractors.league_of_graphs import get_match_recording_settings
from lib.managers import vpn_manager
from lib.managers.programs_manager import running
from lib.utils import cd

RECORDING_COMMAND = '{F10 down}{F10 up}'
FOG_KEYBINDS = {
    Side.blue.value: 'F1',
    Side.red.value: 'F2',
}
LEAGUE_EXE = 'League of Legends.exe'
LEAGUE_PATH = 'C:\Riot Games\League of Legends\\'
GAME = 'Game\\'
BUGSPLAT_EXE = 'BsSndRpt.exe'
KEYBINDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
LOCALE = 'en_GB'


# HOSTS = {
#     Region.korea.value: 'kr3.spectator.op.gg:80',
#     Region.europe_west.value: 'f2.spectator.op.gg:80'
# }


def start_game(match_data):
    vpn_manager.connect()

    region = match_data.get('region')
    match_id = match_data.get('match_id')
    players = list(match_data.get('players_data').keys())
    random_player = players[0]
    host, observer_key, platform = get_match_recording_settings(match_id, region, random_player)

    game_arguments = f"spectator {host} {observer_key} {match_id} {platform}-{random.randint(0, 32767)}{random.randint(0, 32767)}"
    print(game_arguments)
    with cd(LEAGUE_PATH + GAME):
        fnull = open(os.devnull, 'w')
        subprocess.Popen([LEAGUE_EXE, game_arguments, "-GameBaseDir=..", f"-Locale={LOCALE}"], stdout=fnull,
                         stderr=subprocess.STDOUT)


#
# def start_game(region, match_id):
#     with cd('C:\Riot Games\League of Legends\Game'):
#         subprocess.Popen(['League of Legends.exe', f"spectator replays.leagueofgraphs.com:80 mtZKAWeCefBPj7H4EhgqxtArIRYh35J1 4701642062 KR-{random.randint(0, 32767)}{random.randint(0, 32767)}", "-GameBaseDir=..", "-Locale=en_GB"])


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




def enable_settings():
    config = configparser.ConfigParser()
    config.read(GAME_CFG_PATH)
    config['Performance']['ShadowQuality'] = "4"
    config['General']['windowmode'] = "2"
    # config['General']['EnableReplayApi'] = "1"
    with open(GAME_CFG_PATH, 'w') as configfile:
        config.write(configfile)


def disable_settings():
    config = configparser.ConfigParser()
    config.read(GAME_CFG_PATH)
    config['Performance']['ShadowQuality'] = "0"
    config['General']['windowmode'] = "0"

    with open(GAME_CFG_PATH, 'w') as configfile:
        config.write(configfile)
