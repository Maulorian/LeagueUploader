import queue
import threading
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import datapipelines
from cassiopeia import Region, Queue, get_summoner, get_current_match, cassiopeia

from lib.extractors import opgg_extractor, porofessor_extractor
from lib.extractors.porofessor_extractor import PorofessorNoResponseException
from lib.managers import recorded_games_manager
from lib.managers.recorded_games_manager import delete_game, get_recorded_games
from lib.managers.riot_api_manager import get_all_challenger_players, get_match
from lib.utils import pretty_print

# REGIONS_TO_SEARCH = [Region.korea.value, Region.europe_west.value]
REGIONS_TO_SEARCH = [Region.korea.value]
SPECTATOR_DELAY = 5 * 60

ROLE_INDEXES = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
NB_WORKERS = 5
interests = ['Samira', 'Vayne', 'Irelia', 'Yasuo', 'Pyke', 'Ashe', 'Ezreal']


def get_final_players_data(porofessor_players, opgg_players_data):
    players_data = {}
    for player_name in porofessor_players:
        if player_name not in opgg_players_data.keys():
            print(f'{player_name} not in {pretty_print(opgg_players_data)}')
            return
        players_data[player_name] = opgg_players_data[player_name]

    return players_data


def current_challenger_games():
    games = []

    for region in REGIONS_TO_SEARCH:
        challengers = get_all_challenger_players(region)
        challengers_queue = queue.Queue()
        for challenger in challengers:
            challengers_queue.put(challenger)

        with ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
            futures = [executor.submit(check_in_game, challengers_queue, region) for index in range(NB_WORKERS)]
            for future in as_completed(futures):
                games_from_thread = future.result()
                games.extend(games_from_thread)

    return games


def check_in_game(challengers_queue, region):
    games = []
    while not challengers_queue.empty():
        challenger = challengers_queue.get()
        summoner_name = challenger.get('summoner_name')
        summoner_id = challenger.get('summoner_id')

        print(f'[{challengers_queue.qsize()}] - Checking {summoner_name}')
        summoner = get_summoner(id=summoner_id, region=region)
        # try:
        #     current_match = get_current_match(summoner, region)
        #
        #     duration = current_match.duration
        # except datapipelines.common.NotFoundError:
        #     print(f'{summoner_name} not in game')
        #     continue
        opgg_match_data = opgg_extractor.get_match_data(summoner_name, region)
        if not opgg_match_data:
            continue
        match_id = opgg_match_data.get('match_id')
        if not opgg_match_data.get('is_ranked'):
            print(f"{match_id} is not a ranked")
            continue
        try:
            porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)
        except PorofessorNoResponseException:
            return

        if not porofessor_match_data:
            continue

        duration = porofessor_match_data.get('duration')
        if duration.seconds - SPECTATOR_DELAY > 0:
            print(f'{match_id} is already {duration.seconds} seconds long')
            continue

        porofessor_players = porofessor_match_data.get('players')
        opgg_players_data = opgg_match_data.get('players_data')

        players_data = get_final_players_data(porofessor_players, opgg_players_data)
        if not players_data:
            continue
        games.append({
            'players_data': players_data,
            'match_id': match_id,
            'region': region,
            'duration': duration,
        })
    return games


def get_finished_recorded_games():
    finished_games = []
    games = get_recorded_games()
    for i, game in enumerate(games):
        match_id = game.get('match_id')
        region = game.get('region')
        match = get_match(match_id, region)
        if match is None:
            continue
        print(f'[{i}/{len(games)}]Game {match_id} is finished')
        finished_games.append(game)
    return finished_games


def get_player_with_most_kills(finished_games_data):
    players_kills = []
    for game_data in finished_games_data:
        match_id = game_data.get('match_id')
        region = game_data.get('region')
        match = cassiopeia.get_match(match_id, region=region)
        participants = match.participants

        for participant in participants:
            players_kills.append({
                'summoner_name': participant.summoner.name,
                'kills': participant.stats.kills,
                'game_data': game_data
            })
    players_kills_sorted = [player for player in sorted(players_kills, key=lambda player: player.get('kills'), reverse=True)]
    player_with_most_kills = players_kills_sorted[1]

    keep_top_games(players_kills_sorted)

    return player_with_most_kills.get('summoner_name'), player_with_most_kills.get('game_data')


def keep_top_games(players_kills_sorted):
    best_games = {}
    for player_data in players_kills_sorted:
        print(player_data.get('summoner_name'), player_data.get('kills'))
        game_data = player_data.get('game_data')
        match_id = game_data.get('match_id')
        best_games[match_id] = game_data
    match_ids_delete = list(best_games.keys())[10:]
    for match_id in match_ids_delete:
        delete_game(match_id)
