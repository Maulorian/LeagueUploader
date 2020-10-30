import ntpath
import os
import shutil
import subprocess
import time
import traceback

import datapipelines
import requests
from cassiopeia import Side, cassiopeia, Queue, get_summoner

import lib.extractors.porofessor_extractor as porofessor_extractor
import lib.managers.programs_manager as programs_manager
from lib.builders import description_builder, tags_builder
from lib.builders.title_builder import get_title
from lib.constants import ROLE_INDEXES
from lib.extractors.league_of_graphs import get_players_data, ObserverKeyNotFoundException
from lib.extractors.opgg_extractor import get_pro_players_info
from lib.managers import replay_api_manager, league_manager, upload_manager, programs_manager, vpn_manager
from lib.managers.league_manager import start_game, enable_settings, disable_settings
from lib.managers.league_waiter_manager import wait_for_game_launched, wait_finish, \
    GameCrashedException, LaunchCrashedException, WAIT_TIME, wait_for_game_start
from lib.managers.recorded_games_manager import delete_game
from lib.managers.replay_api_manager import get_player_position, PortNotFoundException
from lib.managers.riot_api_manager import get_current_game_version, add_rank_information_to_players
from lib.managers.upload_manager import VIDEOS_PATH, empty_queue
from lib.utils import pretty_log, wait_seconds


@pretty_log
def get_video_path():
    from pathlib import Path

    video_paths = sorted(Path(VIDEOS_PATH).iterdir(), key=os.path.getmtime)

    video_path = video_paths[-1]
    head, tail = ntpath.split(video_path)
    return tail


class GameNotBeginningFromStartException(Exception):
    pass


def wait_summoners_spawned():
    print("[SPECTATOR] - Waiting for Summoners to spawn..")

    while True:
        current_time = replay_api_manager.get_current_game_time()
        if current_time > 30:
            raise GameNotBeginningFromStartException
        if current_time > 5:
            print("[SPECTATOR] - Summoners spawned")
            break


def handle_game(match_data):
    print('Handling game')
    programs_manager.open_program(programs_manager.OBS_EXE)

    enable_settings()

    time.sleep(WAIT_TIME)

    start_game(match_data)

    wait_for_game_launched()
    replay_api_manager.enable_recording_settings()

    game_time_when_started = wait_for_game_start()
    time_when_started = time.time()

    league_manager.toggle_recording()
    recording_start_time = time.time()
    time_to_toggle = recording_start_time - time_when_started
    game_time_when_started_recording = game_time_when_started + time_to_toggle

    print(
        f'took {time_to_toggle} to toggle recording, and was toggled when game was at {game_time_when_started_recording}')
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


def close_programs():
    programs_manager.close_program(programs_manager.OBS_EXE)
    programs_manager.close_program(league_manager.LEAGUE_EXE)
    programs_manager.close_program(league_manager.BUGSPLAT_EXE)
    disable_settings()
    vpn_manager.disconnect()


class DiskFullException(Exception):
    def __init__(self, disk_space):
        self.disk_space = disk_space


def handle_postgame(match_data):
    wait_seconds(WAIT_TIME * 5)
    upload_manager.add_video_to_queue(match_data)
    match_id = match_data.get('match_id')
    delete_game(match_id)


class NameChangedException(Exception):
    pass


def add_champion_to_players(players_data, match_id, region):
    players_dict_in_order = get_players_data(match_id, region)
    for player_name, champion in players_dict_in_order.items():
        try:
            player_data = next(player_data for player_data in players_data.values() if player_data.get('summoner_name') == player_name)
        except StopIteration:
            raise NameChangedException

        tier = player_data.get('tier')
        lp = player_data.get('lp')
        kills = player_data.get('kills')
        dmg = player_data.get('dmg')

        players_dict_in_order[player_name] = {
            'champion': champion,
            'tier': tier,
            'lp': lp,
            'kills': kills,
            'dmg': dmg,
        }
    return players_dict_in_order

def spectate(player_data):
    close_programs()

    mongo_game = player_data.get('mongo_game')

    region = mongo_game.get('region')
    match_id = mongo_game.get('match_id')
    summoner_id = player_data.get('summoner_id')

    summoner = get_summoner(id=summoner_id, region=region)
    summoner_name = summoner.name

    players_data = mongo_game.get('players_data')
    add_rank_information_to_players(players_data, region)
    players_data = add_champion_to_players(players_data, match_id, region)

    player_data = players_data[summoner_name]
    kills = player_data.get('kills')
    dmg = player_data.get('dmg')
    players_name_in_order = list(players_data.keys())
    player_position = players_name_in_order.index(summoner_name)
    player_champion = players_data[summoner_name].get('champion')

    enemy_position = (player_position + 5) % 10
    enemy_summoner_name = players_name_in_order[enemy_position]
    enemy_champion = players_data[enemy_summoner_name].get('champion')

    role = ROLE_INDEXES[player_position % 5]
    tier = player_data.get('tier')
    lp = player_data.get('lp')
    version = get_current_game_version()
    side = Side.blue.value if player_position < 5 else Side.red.value
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
        'side': side,
        'kills': kills,
        'dmg': dmg
    }
    pro_players_info = get_pro_players_info(region)

    if summoner_name in pro_players_info:
        pro_player_info = pro_players_info[summoner_name]

        print(f"[SPECTATOR] - Found concordance: {summoner_name} -> {pro_player_info['name']}")

        match_data['pro_player_info'] = pro_player_info

    print(f"[SPECTATOR] - Spectating {get_title(match_data)}")
    print(f"[SPECTATOR] - {description_builder.get_description(match_data)}")
    try:
        handle_game(match_data)
    except ObserverKeyNotFoundException as e:
        print(f'Observer key not found in {e.url}')
        traceback.print_exc()
        close_programs()
        delete_game(match_id)
        return
    except (GameCrashedException, GameNotBeginningFromStartException):
        traceback.print_exc()

        close_programs()
        wait_seconds(WAIT_TIME)

        if 'file_name' in match_data:
            os.remove(VIDEOS_PATH + match_data['file_name'])
            print(f"{match_data['file_name']} Removed!")
        delete_game(match_id)
        return
    except (subprocess.CalledProcessError, requests.exceptions.ConnectionError,
            LaunchCrashedException, PortNotFoundException, requests.exceptions.ReadTimeout):
        traceback.print_exc()
        close_programs()
        wait_seconds(WAIT_TIME)
        delete_game(match_id)

        if 'file_name' in match_data:
            os.remove(VIDEOS_PATH + match_data['file_name'])
            print(f"{match_data['file_name']} Removed!")

        programs_manager.open_program(programs_manager.CHROME_EXE)
        programs_manager.open_program(programs_manager.DISCORD_EXE)
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
        'match_id': match_data['match_id'],
        'kills': match_data['kills'],
        'dmg': match_data['dmg'],
    }
    print(metadata)
    handle_postgame(metadata)
    programs_manager.open_program(programs_manager.CHROME_EXE)
    programs_manager.open_program(programs_manager.DISCORD_EXE)
