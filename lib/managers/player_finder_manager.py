import queue
import threading
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import datapipelines
from cassiopeia import Region, Queue, get_summoner, get_current_match

from lib.extractors import opgg_extractor, porofessor_extractor
from lib.extractors.porofessor_extractor import PorofessorNoResponseException
from lib.utils import pretty_print

REGIONS_TO_SEARCH = [Region.korea.value, Region.europe_west.value]
# REGIONS_TO_SEARCH = [Region.europe_west.value, Region.korea.value]

ROLE_INDEXES = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
NB_WORKERS = 10
interests = ['Samira', 'Vayne', 'Irelia', 'Yasuo', 'Pyke']


def get_final_players_data(porofessor_players, opgg_players_data):
    players_data = {}
    for player_name in porofessor_players:
        if player_name not in opgg_players_data.keys():
            print(f'{player_name} not in {pretty_print(opgg_players_data)}')
            return
        players_data[player_name] = opgg_players_data[player_name]
    return players_data


def find_ladder_player(check_start=True):
    already_searched_players = set()
    for region in REGIONS_TO_SEARCH:
        print(region)
        # while in_challenger_league:
        summoners_name = opgg_extractor.get_ladder(region)
        summoners_info_queue = queue.Queue()
        for summoner_name in summoners_name:
            summoner_info = {
                'region': region,
                'summoner_name': summoner_name
            }
            summoners_info_queue.put(summoner_info)
        player_found_event = threading.Event()

        with ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
            futures = [executor.submit(handle_player, summoners_info_queue, player_found_event, already_searched_players, check_start) for index in range(NB_WORKERS)]
            for future in as_completed(futures):
                match_data = future.result()
                # print(match_data)
                if match_data is not None:
                    player_found_event.set()
                    return match_data

def handle_player(summoners_info_queue, player_found_event, already_searched_players, check_start):
    while not player_found_event.is_set() and not summoners_info_queue.empty():
        summoner_info = summoners_info_queue.get()
        # print(f'{summoners_info_queue.empty()=}')
        # print(f'{player_found_event.is_set()=}')
        summoner_name = summoner_info['summoner_name']
        region = summoner_info['region']
        print(f'[{summoners_info_queue.qsize()}] - Checking {summoner_name}')
        if summoner_name in already_searched_players:
            continue
        opgg_match_data = opgg_extractor.get_match_data(summoner_name, region)

        if not opgg_match_data:
            continue

        opgg_players_data = opgg_match_data.get('players_data')
        for player in opgg_players_data:
            already_searched_players.add(player)

        player_data = opgg_players_data.get(summoner_name)
        tier = player_data.get('tier')
        if tier != 'Challenger':
            print(f'{summoner_name} is only {tier}')
            continue

        if not opgg_match_data.get('is_ranked'):
            print(f"Not a ranked")
            continue
        try:
            porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)
        except PorofessorNoResponseException:
            return

        if not porofessor_match_data:
            continue

        already_started = porofessor_match_data.get('already_started')
        if check_start and already_started:
            continue

        porofessor_players = porofessor_match_data.get('players')

        players_data = get_final_players_data(porofessor_players, opgg_players_data)
        if not players_data:
            continue

        for player_name, player_data in players_data.items():
            print(player_name, player_data)
            player_position = list(players_data.keys()).index(player_name)
            role = ROLE_INDEXES[player_position % 5]
            player_data['player_position'] = player_position
            player_data['role'] = role

        for champion_skill in interests:
            for player_name, player_data in players_data.items():
                if player_data['champion'] == champion_skill:
                    match_data = {'summoner_name': player_name, 'players_data': players_data, 'region': region}
                    return match_data

        match_data = {'summoner_name': summoner_name, 'players_data': players_data, 'region': region}
        return match_data
    if player_found_event.is_set():
        print("breaking")
    return None

def get_match_data(summoner_name, region):
    opgg_match_data = opgg_extractor.get_match_data(summoner_name, region)

    if not opgg_match_data:
        return
    opgg_players_data = opgg_match_data.get('players_data')

    try:
        porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)
    except PorofessorNoResponseException:
        return

    if not porofessor_match_data:
        return
    porofessor_players = porofessor_match_data.get('players')



    players_data = get_final_players_data(porofessor_players, opgg_players_data)

    for player_name, player_data in players_data.items():
        print(player_name, player_data)
        player_position = list(players_data.keys()).index(player_name)
        role = ROLE_INDEXES[player_position % 5]
        player_data['player_position'] = player_position
        player_data['role'] = role

    return {'summoner_name': summoner_name, 'players_data': players_data, 'region': region}