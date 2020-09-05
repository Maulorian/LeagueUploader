import subprocess
import sys
import time

import requests
from requests.packages import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

PORT_COMMAND = "Get-NetTCPConnection -OwningProcess $(Get-Process 'League of Legends').Id | Where-Object { " \
               "$_.LocalAddress -EQ '127.0.0.1' -And $_.RemoteAddress -EQ '0.0.0.0' } | Select-Object LocalPort "


def get_league_port():
    # print('[REPLAY-API] - Getting League Port')

    output = subprocess.check_output(["powershell.exe", PORT_COMMAND], stderr=subprocess.STDOUT, shell=True)
    for sub in output.split():
        if sub.isdigit():
            return int(sub)
    return None


def game_launched():
    return get_league_port() is not None


def is_game_paused():
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/replay/playback', verify=False)
    paused = r.json()['paused']
    print(f'[REPLAY-API] - Checking Game State: [paused={paused}]')
    print(r.json())
    return paused


def enable_recording_settings():
    print('[REPLAY-API] - Enabling Recording Settings')
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": False,
    }
    port = get_league_port()

    requests.post(f'https://127.0.0.1:{port}/replay/render', verify=False, json=render)


def disable_recording_settings():
    print('[REPLAY-API] - Disabling Recording Settings')
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": True,
    }
    port = get_league_port()
    r = requests.post(f'https://127.0.0.1:{port}/replay/render', verify=False, json=render)


def get_current_game_time():
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/replay/playback', verify=False)
    t = r.json()['time']
    print(f'[REPLAY-API] - Getting Current Game Time: {t}')
    return t


def get_game_info():
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/replay/playback', verify=False)
    print(r.json())
    return r.json()


def pause_game():
    port = get_league_port()
    data = {
        'paused': True
    }
    r = requests.post(f'https://127.0.0.1:{port}/replay/playback', json=data, verify=False)
    print(r.json())
    return r.json()
