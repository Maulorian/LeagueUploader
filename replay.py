import requests
from requests.packages import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)


# r = requests.get('https://127.0.0.1:2999/replay/playback', verify=False)
# print(r.text)
# playback = {
#     "paused": True,
# }

def check_playback():
    print('check_playback()')
    r = requests.get('https://127.0.0.1:2999/replay/playback', verify=False)
    return r.json()


# render = {
#     "cameraAttached": True,
# }
# r = requests.get('https://127.0.0.1:2999/replay/render', verify=False)
# print(r.text)


# r = requests.post('https://127.0.0.1:2999/replay/render', verify=False, json=render)
# print(r.text)
# r = requests.get('https://127.0.0.1:2999/replay/recording', verify=False)
# print(r.text)
def check_render():
    r = requests.get('https://127.0.0.1:2999/replay/render', verify=False)
    print(r.text)


def record_game():
    recording = {
        "codec": "webm",
        "currentTime": 0,
        "endTime": -1.0,
        "enforceFrameRate": False,
        "framesPerSecond": 60,
        "height": 720,
        "lossless": False,
        "path": "C:/Users/Alex/Documents/League of Legends/Highlights/test.webm",
        "recording": True,
        "replaySpeed": 1.0,
        "startTime": -1.0,
        "width": 1344
    }
    r = requests.post('https://127.0.0.1:2999/replay/recording', verify=False, json=recording)
    print(r.text)


def enable_recording_settings():
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": False,
    }
    r = requests.post('https://127.0.0.1:2999/replay/render', verify=False, json=render)
    # print(r.text)

def disable_recording_settings():
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": True,
    }
    r = requests.post('https://127.0.0.1:2999/replay/render', verify=False, json=render)