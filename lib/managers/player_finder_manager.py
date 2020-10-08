import datetime
import queue
import threading
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import datapipelines
from cassiopeia import Region, Queue, get_summoner, get_current_match, cassiopeia

from lib.extractors import opgg_extractor, porofessor_extractor
from lib.extractors.porofessor_extractor import PorofessorNoResponseException, request_recording
from lib.managers import recorded_games_manager
from lib.managers.recorded_games_manager import delete_game, get_recorded_games
from lib.managers.riot_api_manager import get_all_challenger_players, get_match
from lib.utils import pretty_print

# REGIONS_TO_SEARCH = [Region.korea.value, Region.europe_west.value]





def get_finished_recorded_games():
    finished_games = []
    games = get_recorded_games()
    for i, game in enumerate(games):
        match_id = game.get('match_id')
        region = game.get('region')
        # match = get_match(match_id, region)

        try:
            match = cassiopeia.get_match(match_id, region=region)

            if match.is_remake:
                continue
        except datapipelines.common.NotFoundError:
            continue
        print(f'[{i}/{len(games)}] Game {match_id} is finished')
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
    player_with_most_kills = players_kills_sorted[0]

    keep_top_games(players_kills_sorted)

    return player_with_most_kills.get('summoner_name'), player_with_most_kills.get('game_data')


def keep_top_games(players_kills_sorted):
    best_games = {}
    for player_data in players_kills_sorted:
        print(player_data.get('summoner_name'), player_data.get('kills'))
        game_data = player_data.get('game_data')
        match_id = game_data.get('match_id')
        best_games[match_id] = game_data
    match_ids_delete = list(best_games.keys())[20:]
    for match_id in match_ids_delete:
        delete_game(match_id)
