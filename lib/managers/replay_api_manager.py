import datetime
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
    r = requests.get(f'{get_base_url()}/liveclientdata/playerlist', verify=False)
    champions = r.json()
    return champions

def get_active_player_data():
    port = get_league_port()
    r = requests.get(f'{get_base_url()}/liveclientdata/activeplayername', verify=False)
    player_data = r.json()
    print(player_data)



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
    r = requests.get(f'{get_base_url()}/replay/playback', verify=False)
    paused = r.json()['paused']
    print(f'[REPLAY-API] - Checking if Game is paused : {{paused={paused}}}')
    return paused


def enable_recording_settings():
    try:
        print(f'[REPLAY-API] - Enabling Recording Settings')
        render = {
            "interfaceScoreboard": True,
            "interfaceTimeline": False,
            "interfaceChat": False,
        }
        port = get_league_port()

        requests.post(f'{get_base_url()}/replay/render', verify=False, json=render)
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
    r = requests.post(f'{get_base_url()}/replay/render', verify=False, json=render)


def get_current_game_time():
    url = f'{get_base_url()}/replay/playback'
    r = requests.get(url, verify=False)
    response_json = r.json()
    print(response_json)
    t = response_json['time']
    # print(f'[REPLAY-API] - Getting Current Game Time: {t}')
    return t


def get_game_render_data():
    url = f'{get_base_url()}/replay/render'
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


def get_events():
    endpoint = '/liveclientdata/eventdata'
    url = f'{get_base_url()}{endpoint}'
    r = requests.get(url, verify=False)
    return r.json().get('Events')


def game_finished() -> bool:
    events = get_events()
    return events[-1].get('EventName') == GAME_END


def game_started() -> bool:
    events = get_events()
    if len(events) == 0:
        return False

    return events[0].get('EventName') == GAME_START


def get_player_items(player_data):
    items = player_data.get('items')

    items_data = get_items(region=Region.europe_west)
    for item in items:
        item_data = next(item_data for item_data in items_data if item_data.id == item.get('itemID'))
        item['total_gold'] = item_data.gold.total

    items.sort(key=lambda item: item.get('total_gold'), reverse=True)
    items = [item for item in items if item.get('total_gold') >= 1100]
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(items)
    items = list(map(lambda item: item.get('itemID'), items))

    return items


def get_player_summoner_spells(player_data):
    summoner_spells = player_data.get('summonerSpells')
    player_summoner_spells = []
    player_summoner_spells.append(summoner_spells.get('summonerSpellOne').get('displayName'))
    player_summoner_spells.append(summoner_spells.get('summonerSpellTwo').get('displayName'))
    for i, spell in enumerate(player_summoner_spells):
        if spell == 'Challenging Smite':
            player_summoner_spells[i] = 'Smite'
    return player_summoner_spells


def get_formated_timestamp(total_seconds):
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f'{str(round(minutes)).zfill(2)}:{str(round(seconds)).zfill(2)}'

def get_player_kill_timestamps(summoner_name):
    events = get_events()
    events = [event for event in events if (event.get('EventName') == 'ChampionKill' and event.get('KillerName') == summoner_name)]
    champions = get_players_data()
    times_stamps = [{'victim': next(item.get("championName") for item in champions if item.get('summonerName') == event.get('VictimName')), 'time': get_formated_timestamp(event.get('EventTime') - 10)} for event in events]

    return times_stamps