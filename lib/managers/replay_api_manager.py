import datetime
import pprint
import subprocess
import sys
import time

import requests
from cassiopeia import get_items, Region
from requests.packages import urllib3
from urllib3.exceptions import InsecureRequestWarning

from lib.utils import pretty_print

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
    r = requests.get(f'{get_base_url()}/liveclientdata/playerlist', verify=False)
    champions = r.json()
    return champions


def get_active_player_data():
    r = requests.get(f'{get_base_url()}/liveclientdata/activeplayer', verify=False)
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


def game_paused():
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

        requests.post(f'{get_base_url()}/replay/render', verify=False, json=render, timeout=60)
    except requests.exceptions.ConnectionError:
        time.sleep(1)


def disable_recording_settings():
    print('[REPLAY-API] - Disabling Recording Settings')
    render = {
        "interfaceScoreboard": True,
        "interfaceTimeline": False,
        "interfaceChat": True,
    }
    r = requests.post(f'{get_base_url()}/replay/render', verify=False, json=render, timeout=60)


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
    r = requests.get(url, verify=False, timeout=60)
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
    r = requests.post(url, json=data, verify=False, timeout=60)
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
    r = requests.get(url, verify=False, timeout=60)

    return r.json().get('Events')


def game_finished() -> bool:
    events = get_events()
    last_event = events[-1]
    print(last_event)

    return last_event.get('EventName') == GAME_END


def game_started() -> bool:
    events = get_events()
    if events is None:
        return False

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
    # pp.pprint(items)
    items = list(map(lambda item: item.get('itemID'), items))

    return items


def get_player_summoner_spells(player_data):
    summoner_spells = player_data.get('summonerSpells')
    player_summoner_spells = []
    player_summoner_spells.append(summoner_spells.get('summonerSpellOne').get('displayName'))
    player_summoner_spells.append(summoner_spells.get('summonerSpellTwo').get('displayName'))
    for i, spell in enumerate(player_summoner_spells):
        if 'Smite' in spell:
            player_summoner_spells[i] = 'Smite'
    return player_summoner_spells


def get_formated_timestamp(total_seconds):
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f'{str(round(minutes)).zfill(2)}:{str(round(seconds)).zfill(2)}'


def get_recording_time(recording_times, event_game_time):
    for i, recording_time in enumerate(sorted(list(recording_times.keys()), key=lambda k: k, reverse=True)):
        game_time = recording_times[recording_time]
        if event_game_time <= game_time:
            delta_game_time = game_time - event_game_time
            adjusted_recording_time = recording_time - delta_game_time
            return adjusted_recording_time


def get_player_events(summoner_name, recording_times):
    events = get_events()
    print(summoner_name)

    champions = get_players_data()
    final_events = []
    for event in events:

        formatted_event = get_formated_event(event, summoner_name, champions)

        if not formatted_event:
            continue
        event_game_time = event.get('EventTime')

        recording_time = get_recording_time(recording_times, event_game_time)
        formatted_event['time'] = recording_time
        formatted_event['event_game_time'] = event_game_time

        final_events.append(formatted_event)

    return final_events


def get_formated_event(event, summoner_name, champions):
    if event.get('EventName') == GAME_END:
        return {
            'type': 'game_end'
        }
    if event.get('EventName') == 'ChampionKill':
        if event.get('KillerName') == summoner_name:
            return {
                'type': 'kill',
                'victim': next(item.get("championName") for item in champions if item.get('summonerName') == event.get('VictimName')),
            }
        if summoner_name in event.get('Assisters'):
            return {
                'type': 'assist',
                'victim': next(item.get("championName") for item in champions if item.get('summonerName') == event.get('VictimName')),
            }
        if event.get('VictimName') == summoner_name:
            if 'Turret' in event.get('KillerName'):
                return {
                    'type': 'death',
                    'killer': 'Turret',
                }
            return {
                'type': 'death',
                'killer': event.get("KillerName"),
            }
    if event.get('EventName') == 'TurretKilled':
        if summoner_name in event.get('Assisters'):
            return {
                    'type': 'turret_kill',
            }

    if event.get('EventName') == 'InhibKilled':
        if summoner_name in event.get('Assisters'):
            return {
                    'type': 'inhibitor_kill',
            }
    if event.get('EventName') == 'BaronKill':
        if summoner_name in event.get('Assisters') or summoner_name in event.get('Assisters'):
            return {
                    'type': 'baron_kill',
            }
    return None

