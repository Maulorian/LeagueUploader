import ntpath
import os
import re
import shutil
import subprocess
import time
import traceback
from datetime import datetime

import cassiopeia as cass
import datapipelines
import requests
from cassiopeia import get_current_match

from lib.builders import description_builder, tags_builder
from lib.extractors import opgg_extractor
from lib.extractors.opgg_extractor import get_pro_players_info
from lib.managers import replay_api_manager, obs_manager, league_manager, upload_manager, programs_manager

from lib.builders.title_builder import get_title
from lib.managers.game_cfg_manager import enable_settings, disable_settings
from lib.managers.league_manager import bugsplat, kill_bugsplat, start_game
from lib.managers.player_finder_manager import get_match_data
from lib.managers.replay_api_manager import get_player_position, PortNotFoundException, game_finished, game_started, \
    get_current_game_time, game_launched
from lib.managers.upload_manager import VIDEOS_PATH
from lib.utils import pretty_log

WAIT_TIME = 2


class GameRemakeException(Exception):
    pass


def wait_finish():
    print("[SPECTATOR] - Waiting for game to finish..")
    current_time = get_current_game_time()
    while True:
        new_time = get_current_game_time()
        if new_time == current_time:
            raise GameCrashedException
        if bugsplat():
            raise GameCrashedException
        finished = game_finished()
        if finished:
            if new_time <= 4 * 60:
                raise GameRemakeException
            else:
                print("[SPECTATOR] - Game Finished")
                break
        time.sleep(1)


class GameCrashedException(Exception):
    pass


def wait_for_game_launched():
    print("[SPECTATOR] - Waiting for game to launch..")

    start = time.time()
    while True:
        time_passed = time.time() - start
        print(time_passed)
        if time_passed > (5 * 60):
            raise GameCrashedException
        try:
            if game_launched():
                print("[SPECTATOR] - Game has launched")
                break
            if bugsplat():
                raise GameCrashedException

        except (requests.exceptions.ConnectionError, subprocess.CalledProcessError):
            # print("[SPECTATOR] - Game not yet launched")
            time.sleep(1)


def wait_for_game_loaded():
    print("[SPECTATOR] - Waiting for game to load..")

    start = time.time()
    while True:
        time_passed = time.time() - start
        print(time_passed)
        if time_passed > (5 * 60):
            raise GameCrashedException
        if game_started():
            print("[SPECTATOR] - Game has loaded")
            break
        if bugsplat():
            raise GameCrashedException
        wait_seconds(WAIT_TIME)


def wait_for_game_start():
    print("[SPECTATOR] - Waiting for game to start..")

    start = time.time()
    start_time = get_current_game_time()

    while True:
        time_passed = time.time() - start
        print(time_passed)
        if time_passed > (5 * 60):
            raise GameCrashedException
        game_time = get_current_game_time()
        if game_time > start_time:
            print("[SPECTATOR] - Game has started")
            break
        if bugsplat():
            raise GameCrashedException
        wait_seconds(WAIT_TIME)

def get_current_game_version():
    r = requests.get('https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json')
    version = r.json()['patches'][-1]['name']
    return version


def wait_seconds(WAIT_TIME):
    # print(f"[SPECTATOR] - Waiting {WAIT_TIME}")
    time.sleep(WAIT_TIME)


def find_and_launch_game(match_data):
    match_id = match_data.get('match_id')
    region = match_data.get('region')
    encryption_key = match_data.get('encryption_key')
    start_game(region, match_id, encryption_key)


@pretty_log
def get_video_path():
    from pathlib import Path

    video_paths = sorted(Path(VIDEOS_PATH).iterdir(), key=os.path.getmtime)

    video_path = video_paths[-1]
    head, tail = ntpath.split(video_path)
    return tail


def wait_summoners_spawned():
    print("[SPECTATOR] - Waiting for Summoners to spawn..")

    while True:
        current_time = replay_api_manager.get_current_game_time()
        if current_time > 5:
            print("[SPECTATOR] - Summoners spawned")
            break


def handle_game(match_data):
    obs_manager.start()

    enable_settings()

    time.sleep(WAIT_TIME)

    find_and_launch_game(match_data)
    wait_for_game_launched()
    time.sleep(WAIT_TIME)

    wait_seconds(WAIT_TIME)

    wait_for_game_loaded()
    replay_api_manager.enable_recording_settings()

    wait_for_game_start()

    league_manager.toggle_recording()

    wait_summoners_spawned()

    player_champion = match_data.get('player_champion')
    player_position = get_player_position(player_champion)

    league_manager.select_summoner(player_position)
    league_manager.enable_runes()
    side = match_data.get('side')
    league_manager.adjust_fog(side)

    wait_seconds(WAIT_TIME)
    match_data['path'] = get_video_path()
    print(f'Saving game to {match_data["path"]}')
    wait_finish()
    league_manager.toggle_recording()

    player_data = replay_api_manager.get_player_data(player_champion)
    match_data['items'] = replay_api_manager.get_player_items(player_data)
    match_data['skin_name'] = replay_api_manager.get_player_skin(player_data)
    match_data['runes'] = replay_api_manager.get_player_runes(player_data)
    match_data['summonerSpells'] = replay_api_manager.get_player_summoner_spells(player_data)
    summoner_name = match_data.get('summoner_name')
    match_data['player_kill_timestamps'] = replay_api_manager.get_player_kill_timestamps(summoner_name)

    close_programs()
    open_programs()

def open_programs():
    programs_manager.open_program(programs_manager.CHROME_EXE)
    programs_manager.open_program(programs_manager.DISCORD_EXE)


def close_programs():
    programs_manager.close_program(obs_manager.OBS_EXE)
    programs_manager.close_program(league_manager.LEAGUE_EXE)
    programs_manager.close_program(league_manager.BUGSPLAT_EXE)
    programs_manager.close_program(programs_manager.CHROME_EXE)
    programs_manager.close_program(programs_manager.DISCORD_EXE)
    disable_settings()


class DiskFullException(Exception):
    def __init__(self, disk_space):
        self.disk_space = disk_space


def handle_postgame(match_data):
    wait_seconds(WAIT_TIME * 5)
    upload_manager.add_video_to_queue(match_data)
    total_space, used_space, free_space = shutil.disk_usage("D:")
    total_space, used_space, free_space = (total_space // (2 ** 30)), (used_space // (2 ** 30)), (free_space // (2 ** 30))
    if free_space < 1:
        raise DiskFullException(free_space)


def get_summoner_current_match(summoner):
    try:
        match = summoner.current_match
        return match
    except datapipelines.common.NotFoundError:
        return






def spectate(match_data):

    close_programs()

    region = match_data.get('region')
    summoner_name = match_data.get('summoner_name')

    summoner = cass.get_summoner(region=region, name=summoner_name)
    match = get_summoner_current_match(summoner)

    if match is None:
        print(f'"{summoner_name}" is not in game')
        return
    match_id = match.id
    encryption_key = match.observer_key

    players_data = match_data.get('players_data')

    player_data = players_data[summoner_name]
    player_position = list(players_data.keys()).index(summoner_name)
    player_champion = player_data['champion']

    enemy_position = (player_position + 5) % 10
    enemy_summoner_name = list(players_data.keys())[enemy_position]
    enemy_champion = players_data[enemy_summoner_name].get('champion')

    role = player_data.get('role')
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
        'encryption_key': encryption_key,
        'side': side
    }
    pro_players_info = get_pro_players_info(region)

    if summoner_name in pro_players_info:
        pro_player_info = pro_players_info[summoner_name]

        print(f"[SPECTATOR] - Found concordance: {summoner_name} -> {pro_player_info['name']}")

        match_data['pro_player_info'] = pro_player_info

    print(f"[SPECTATOR] - Spectating {get_title(match_data)}")

    try:
        handle_game(match_data)
    except (subprocess.CalledProcessError, requests.exceptions.ConnectionError, GameCrashedException,
            PortNotFoundException, GameRemakeException) as exception:

        print(f'{exception} was raised during the process')
        close_programs()
        open_programs()
        wait_seconds(WAIT_TIME)

        if 'path' in match_data:
            os.remove(VIDEOS_PATH + match_data['path'])
            print(f"{match_data['path']} Removed!")
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
        'path': match_data['path'],
        'region': region,
        'tier': tier,
        'lp': lp,
        'role': role,

    }
    handle_postgame(metadata)
