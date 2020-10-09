# import os
# import queue
# import time
# import traceback
# from asyncio import as_completed
# from concurrent.futures.thread import ThreadPoolExecutor
# from datetime import datetime
#
# import datapipelines
# from cassiopeia import get_summoner, get_match, cassiopeia, Region
# from dotenv import load_dotenv
#
# from lib.extractors import opgg_extractor, porofessor_extractor
# from lib.extractors.porofessor_extractor import PorofessorNoResponseException, request_recording
# from lib.managers import player_finder_manager, recorded_games_manager
# from lib.managers.riot_api_manager import get_all_challenger_players
# from lib.utils import pretty_print
#
# load_dotenv()
# cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))
#
# REGIONS_TO_SEARCH = ['KR']
# SPECTATOR_DELAY = 3 * 60
# NB_WORKERS = 5
#
#
# def loop():
#     while True:
#         try:
#             enable_challengers_games_recording()
#         except Exception:
#             traceback.print_exc()
#             time.sleep(SPECTATOR_DELAY)
#
#         print(f'Sleeping {SPECTATOR_DELAY} before enabling again.')
#         time.sleep(SPECTATOR_DELAY)
#
#
# def get_final_players_data(porofessor_players, opgg_players_data):
#     players_data = {}
#     for player_name in porofessor_players:
#         if player_name not in opgg_players_data.keys():
#             print(f'{player_name} not in {pretty_print(opgg_players_data)}')
#             return
#         players_data[player_name] = opgg_players_data[player_name]
#
#     return players_data
#
#
# def enable_challengers_games_recording():
#     for region in REGIONS_TO_SEARCH:
#         challengers = get_all_challenger_players(region)
#         challengers_queue = queue.Queue()
#         for challenger in challengers:
#             challengers_queue.put(challenger)
#
#         with ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
#             for i in range(NB_WORKERS):
#                 executor.submit(check_in_game, challengers_queue, region)
#
#
#
# def check_in_game(challengers_queue, region):
#     while not challengers_queue.empty():
#         challenger = challengers_queue.get()
#         summoner_name = challenger.get('summoner_name')
#         summoner_id = challenger.get('summoner_id')
#
#         summoner = get_summoner(id=summoner_id, region=region)
#         # try:
#         #     current_match = get_current_match(summoner, region)
#         #
#         #     duration = current_match.duration
#         # except datapipelines.common.NotFoundError:
#         #     print(f'{summoner_name} not in game')
#         #     continue
#         opgg_match_data = opgg_extractor.get_match_data(summoner_name, region)
#         if not opgg_match_data:
#             print(f'[{challengers_queue.qsize()}] - "{summoner_name}" : Not in Game')
#
#             continue
#         match_id = opgg_match_data.get('match_id')
#         if not opgg_match_data.get('is_ranked'):
#             print(f'{match_id} is not a ranked')
#             continue
#         try:
#             porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)
#         except PorofessorNoResponseException:
#             return
#
#         if not porofessor_match_data:
#             continue
#
#         duration = porofessor_match_data.get('duration')
#         if duration.seconds - SPECTATOR_DELAY > 0:
#             print(f'{match_id} is already {duration.seconds} seconds long')
#             continue
#
#         porofessor_players = porofessor_match_data.get('players')
#         opgg_players_data = opgg_match_data.get('players_data')
#
#         players_data = get_final_players_data(porofessor_players, opgg_players_data)
#         if not players_data:
#             continue
#         if already_enabled(match_id):
#             print(f'{match_id} Already enabled.')
#
#         request_worked = request_recording(summoner_name, region)
#         if request_worked:
#             match = {
#                 'match_id': match_id,
#                 'region': region,
#                 'duration': duration.seconds,
#                 'players_data': players_data
#             }
#             recorded_games_manager.add_game(match)
#
#
# if __name__ == '__main__':
#     loop()
