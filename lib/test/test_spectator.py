import os
import subprocess
import sys
import time
import unittest

import cassiopeia as cass
import requests
from dotenv import load_dotenv

from lib.builders import description_builder, tags_builder
from lib.builders.title_builder import get_title
from lib.extractors.opgg_extractor import get_pro_players_info
from lib.managers import programs_manager, replay_api_manager, league_manager
from lib.managers.game_cfg_manager import enable_settings
from lib.managers.league_manager import start_game
from lib.managers.league_waiter_manager import wait_finish, wait_for_game_start
from lib.managers.player_finder_manager import ROLE_INDEXES, \
    get_finished_recorded_games, get_player_with_most_kills
from lib.managers.replay_api_manager import PortNotFoundException, get_player_position
from lib.managers.upload_manager import VIDEOS_PATH
from lib.spectator import get_current_game_version, LaunchCrashedException, wait_seconds, WAIT_TIME, \
    close_programs, \
    wait_for_game_launched, wait_summoners_spawned, get_video_path

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')
load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)


class TestThumbnail(unittest.TestCase):

    def test_spectate(self):
        finished_games = get_finished_recorded_games()

        summoner_name, game_data = get_player_with_most_kills(finished_games)
        close_programs()

        region = game_data.get('region')
        match_id = game_data.get('match_id')
        observer_key = game_data.get('observer_key')
        players_data = game_data.get('players_data')

        player_data = players_data[summoner_name]
        player_position = list(players_data.keys()).index(summoner_name)
        player_champion = player_data['champion']

        enemy_position = (player_position + 5) % 10
        enemy_summoner_name = list(players_data.keys())[enemy_position]
        enemy_champion = players_data[enemy_summoner_name].get('champion')

        role = ROLE_INDEXES[player_position % 5]
        tier = player_data.get('tier')
        lp = player_data.get('lp')
        version = get_current_game_version()
        side = player_data.get('side')
        match_data = {
            'players_data': players_data,
            'player_champion': player_champion,
            'role': role,
            'summoner_name': summoner_name,
            'enemy_champion': enemy_champion,
            'region': region,
            'tier': tier,
            'lp': lp,
            'version': version,
            'match_id': match_id,
            'observer_key': observer_key,
            'side': side
        }
        pro_players_info = get_pro_players_info(region)

        if summoner_name in pro_players_info:
            pro_player_info = pro_players_info[summoner_name]

            print(f"[SPECTATOR] - Found concordance: {summoner_name} -> {pro_player_info['name']}")

            match_data['pro_player_info'] = pro_player_info

        print(f"[SPECTATOR] - Spectating {get_title(match_data)}")
        try:
            match_id = match_data.get('match_id')
            region = match_data.get('region')
            programs_manager.open_program(programs_manager.OBS_EXE)

            enable_settings()

            time.sleep(WAIT_TIME)

            start_game(match_data)

            wait_for_game_launched()
            replay_api_manager.enable_recording_settings()

            # wait_for_game_loaded()
            wait_for_game_start()
            start = time.time()

            league_manager.toggle_recording()
            recording_start_time = time.time()

            game_time_when_started_recording = time.time() - start
            print(f'took {game_time_when_started_recording} to toggle recording')
            recording_times = dict([(0, game_time_when_started_recording)])

            wait_summoners_spawned()

            player_champion = match_data.get('player_champion')
            player_position = get_player_position(player_champion)

            league_manager.select_summoner(player_position)
            league_manager.enable_runes()
            side = match_data.get('side')
            league_manager.adjust_fog(side)

            wait_seconds(WAIT_TIME)
            match_data['file_name'] = get_video_path()
            print(f'Saving game to {match_data["file_name"]}')
            wait_finish(recording_times, game_time_when_started_recording, recording_start_time)
            league_manager.toggle_recording()

            player_data = replay_api_manager.get_player_data(player_champion)
            match_data['items'] = replay_api_manager.get_player_items(player_data)
            match_data['skin_name'] = replay_api_manager.get_player_skin(player_data)
            match_data['runes'] = replay_api_manager.get_player_runes(player_data)
            match_data['summonerSpells'] = replay_api_manager.get_player_summoner_spells(player_data)
            summoner_name = match_data.get('summoner_name')
            match_data['events'] = replay_api_manager.get_player_events(summoner_name, recording_times)
            print(match_data['events'])
            close_programs()
        except (subprocess.CalledProcessError, requests.exceptions.ConnectionError,
                LaunchCrashedException, PortNotFoundException) as exception:

            print(f'{exception} was raised during the process')
            close_programs()
            wait_seconds(WAIT_TIME)

            if 'file_name' in match_data:
                os.remove(VIDEOS_PATH + match_data['file_name'])
                print(f"{match_data['file_name']} Removed!")
            return

        metadata = {
            'description': description_builder.get_description(match_data),
            'tags': tags_builder.get_tags(match_data),
            'title': get_title(match_data),
            'player_champion': player_champion,
            'skin_name': match_data['skin_name'],
            'items': match_data['items'],
            'runes': match_data['runes'],
            'summonerSpells': match_data['summonerSpells'],
            'file_name': match_data['file_name'],
            'region': region,
            'tier': tier,
            'lp': lp,
            'role': role,
            'events': match_data['events'],
            'match_id': match_data['match_id']
        }
        # handle_postgame(metadata)
