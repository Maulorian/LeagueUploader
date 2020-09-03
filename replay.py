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
    print('[REPLAY-API] - Checking Game State')
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/replay/playback', verify=False)
    print(r.json())
    return r.json()['paused']


def enable_recording_settings():
    print('[REPLAY-API] - Enabling Recording Settings')
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": False,
    }
    port = get_league_port()

    requests.post(f'https://127.0.0.1:{port}/replay/render', verify=False, json=render)
    # print(r.text)


def disable_recording_settings():
    print('[REPLAY-API] - Disabling Recording Settings')
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": True,
    }
    port = get_league_port()
    r = requests.post(f'https://127.0.0.1:{port}/replay/render', verify=False, json=render)
# def check_render():
#     r = requests.get('https://127.0.0.1:2999/replay/render', verify=False)
#     print(r.text)
#
#
# def record_game():
#     recording = {
#         "codec": "webm",
#         "currentTime": 0,
#         "endTime": -1.0,
#         "enforceFrameRate": False,
#         "framesPerSecond": 60,
#         "height": 720,
#         "lossless": False,
#         "path": "C:/Users/Alex/Documents/League of Legends/Highlights/test.webm",
#         "recording": True,
#         "replaySpeed": 1.0,
#         "startTime": -1.0,
#         "width": 1344
#     }
#     r = requests.post('https://127.0.0.1:2999/replay/recording', verify=False, json=recording)
#     print(r.text)
def get_current_game_time():
    print('[REPLAY-API] - Get Current Game Time')
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/replay/playback', verify=False)
    return r.json()['time']