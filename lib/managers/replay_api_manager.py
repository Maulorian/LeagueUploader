import pprint
import subprocess
import sys
import time

import requests
from cassiopeia import get_items, Region
from requests.packages import urllib3
from urllib3.exceptions import InsecureRequestWarning

GAME_START = 'GameStart'

GAME_END = 'GameEnd'

urllib3.disable_warnings(InsecureRequestWarning)

PORT_COMMAND = "Get-NetTCPConnection -OwningProcess $(Get-Process 'League of Legends').Id | Where-Object { " \
               "$_.LocalAddress -EQ '127.0.0.1' -And $_.RemoteAddress -EQ '0.0.0.0' } | Select-Object LocalPort "


class PortNotFoundException(Exception):
    pass


def get_league_port():
    # print('[REPLAY-API] - Getting League Port')

    output = subprocess.check_output(["powershell.exe", PORT_COMMAND], stderr=subprocess.STDOUT, shell=True)
    for sub in output.split():
        if sub.isdigit():
            return int(sub)
    raise PortNotFoundException


def game_launched():
    return get_league_port() is not None


def get_players_data():
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/liveclientdata/playerlist', verify=False)
    champions = r.json()
    return champions


def get_player_position(champion):
    players = get_players_data()
    players = list(map(lambda player: player.get('championName'), players))
    return players.index(champion)


def get_player_data(champion):
    champions = get_players_data()
    champion = next(item for item in champions if item.get('championName') == champion)
    print(f'[REPLAY-API] - Getting player data : {champion}')
    return champion


def is_game_paused():
    port = get_league_port()
    r = requests.get(f'https://127.0.0.1:{port}/replay/playback', verify=False)
    paused = r.json()['paused']
    print(f'[REPLAY-API] - Checking if Game is paused : {{paused={paused}}}')
    return paused


def enable_recording_settings():
    retry = 3
    while retry > 0:
        retry -= 1
        try:
            print(f'[REPLAY-API] - Enabling Recording Settings {{retry={retry}}}')
            render = {
                "interfaceScoreboard": True,
                "interfaceTimeline": False,
                "interfaceChat": False,
            }
            port = get_league_port()

            requests.post(f'https://127.0.0.1:{port}/replay/render', verify=False, json=render)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(1)


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
    url = f'https://127.0.0.1:{port}/replay/playback'
    r = requests.get(url, verify=False)
    response_json = r.json()
    print(response_json)
    t = response_json['time']
    # print(f'[REPLAY-API] - Getting Current Game Time: {t}')
    return t


def get_game_render_data():
    port = get_league_port()
    url = f'https://127.0.0.1:{port}/replay/render'
    r = requests.get(url, verify=False)
    print(r.json())
    return r.json()


def get_base_url():
    port = get_league_port()
    return f'https://127.0.0.1:{port}'


def pause_game():
    data = {
        'paused': True
    }
    url = f'{get_base_url()}/replay/playback'
    r = requests.post(url, json=data, verify=False)
    print(r.json())
    return r.json()


def get_player_skin(player_data):
    skin_name = player_data.get('skinName')
    if not skin_name:
        skin_name = 'default'
    return skin_name


def get_player_runes(player_data):
    runes = player_data.get('runes')
    player_runes = {}
    player_runes['keystone'] = runes.get('keystone').get('id')
    player_runes['secondaryRuneTree'] = runes.get('secondaryRuneTree').get('id')
    return player_runes


def game_finished() -> bool:
    endpoint = '/liveclientdata/eventdata'
    url = f'{get_base_url()}{endpoint}'
    r = requests.get(url, verify=False)
    print(r.json().get('Events'))
    return r.json().get('Events')[-1].get('EventName') == GAME_END

def game_started() -> bool:
    endpoint = '/liveclientdata/eventdata'
    url = f'{get_base_url()}{endpoint}'
    r = requests.get(url, verify=False)
    events = r.json().get('Events')
    if len(events) == 0:
        return False

    return events[0].get('EventName') == GAME_START

def get_player_items(player_data):
    items = player_data.get('items')

    items_data = get_items(region=Region.europe_west)
    for item in items:
        item_data = next(item_data for item_data in items_data if item_data.id == item.get('itemID'))
        item['total_gold'] = item_data.gold.total

    items = sorted(items, key=lambda item: item.get('total_gold'), reverse=True)
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(items)
    items = list(map(lambda item: item.get('itemID'), items))

    return items


def get_player_summoner_spells(player_data):
    summoner_spells = player_data.get('summonerSpells')
    player_summoner_spells = []
    player_summoner_spells.append(summoner_spells.get('summonerSpellOne').get('displayName'))
    player_summoner_spells.append(summoner_spells.get('summonerSpellTwo').get('displayName'))
    return player_summoner_spells
