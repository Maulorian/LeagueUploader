import subprocess
import time

import cassiopeia as cass
import requests
from cassiopeia import GameType, Queue

import upload_manager
import porofessor_manager
import obs_manager
import replay_api_manager
import league_manager
from builders import tags_builder, description_builder

from dotenv import load_dotenv

from builders.title_builder import get_title
from opgg_extractor import OPGGExtractor

load_dotenv()

WAIT_TIME = 1
SURREND_TIME = 15 * 60
ROLE_INDEXES = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
BAT_PATH = 'replay.bat'



def get_challenger_in_ranked_match(challengers):
    print(f'[OPGG MANAGER] - Getting Player in Ranked Game')

    for summoner_name in challengers:
        print(f'[{__name__.upper()}] - Checking if "{summoner_name}" is in game')
        summoner = cass.get_summoner(name=summoner_name)
        match = summoner.current_match
        print(f'[{__name__.upper()}] - Riot API Duration={match.duration}')

        if match is None:
            continue
        if match.type != GameType.matched:
            continue

        if match.queue != Queue.ranked_solo_fives:
            print(f'[{__name__.upper()}] - Match Queue is not ranked: {match.queue.value}')
            continue

        duration = porofessor_manager.get_current_match_duration(summoner.name)
        if not duration:
            continue

        print(f'[{__name__.upper()}] - Duration={duration}')

        just_started = duration.seconds - 2 * 60 < 0
        if not just_started:
            continue

        return summoner_name

def wait_finish():
    current_time = replay_api_manager.get_current_game_time()
    while True:
        new_time = replay_api_manager.get_current_game_time()
        paused = replay_api_manager.is_game_paused()
        # if not paused and new_time == current_time and new_time >= SURREND_TIME:
        if new_time == current_time:
            print("[SPECTATOR] - Game ended")
            return
        current_time = new_time
        print("[SPECTATOR] - Still in game")
        time.sleep(0.5)


def wait_for_game_launched():
    while True:
        try:
            if replay_api_manager.game_launched():
                print("[SPECTATOR] - Game has launched")
                break
        except (requests.exceptions.ConnectionError, subprocess.CalledProcessError):
            print("[SPECTATOR] - Game not yet launched")
            time.sleep(1)


def wait_for_game_start():
    while True:
        current_time = replay_api_manager.get_current_game_time()
        if current_time <= 5:
            print("[SPECTATOR] - Match is still paused")
            wait_seconds(WAIT_TIME)
            continue
        print("[SPECTATOR] - Match has started")
        break


def get_current_game_version():
    r = requests.get('https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json')
    version = r.json()['patches'][-1]['name']
    return version


# def handle(summoner_name):
#     pass


def wait_seconds(WAIT_TIME):
    print(f"[SPECTATOR] - Waiting {WAIT_TIME}")
    time.sleep(WAIT_TIME)


def find_and_launch_game(match):
    match_id = match.get('id')
    region = match.get('region')

    opgg_extractor = OPGGExtractor(region)
    replay_command = opgg_extractor.get_game_bat(match_id)
    # replay_command = r.text

    with open(BAT_PATH, 'w') as f:
        f.write(replay_command)

    subprocess.call([BAT_PATH], stdout=subprocess.DEVNULL)


def handle_game(match, player_position):
    obs_manager.start()

    find_and_launch_game(match)
    wait_for_game_launched()

    time.sleep(WAIT_TIME)
    replay_api_manager.enable_recording_settings()
    wait_seconds(WAIT_TIME)

    wait_for_game_start()
    league_manager.select_summoner(player_position)
    wait_seconds(WAIT_TIME)

    league_manager.toggle_recording()

    wait_finish()

    league_manager.toggle_recording()

    obs_manager.close_obs()
    league_manager.close_game()


def handle_postgame(match_info):
    wait_seconds(WAIT_TIME*5)
    description = description_builder.get_description(match_info)
    tags = tags_builder.get_tags(match_info)
    title = match_info.get('title')
    metadata = {
        'title': title,
        'description': description,
        'tags': tags,
    }
    upload_manager.add_video_to_queue(metadata)

def spectate(match_data):
    region = match_data.get('region')
    summoner_name = match_data.get('summoner_name')

    summoner = cass.get_summoner(region=region, name=summoner_name)
    match = summoner.current_match
    if match is None:
        print(f'"{summoner_name}" is not in game')
        return
    match_id = match.id
    # participants = match.participants

    players_data = match_data.get('players_data')

    player_data = players_data[summoner_name]
    player_position = list(players_data.keys()).index(summoner_name)
    player_champion = player_data['champion']

    enemy_position = (player_position + 5) % 10
    enemy_summoner_name = list(players_data.keys())[enemy_position]
    enemy_champion = players_data[enemy_summoner_name].get('champion')

    role = ROLE_INDEXES[player_position % 5]
    rank = player_data.get('rank')

    version = get_current_game_version()


    match_info = {
        'players_data': players_data,
        'player_champion': player_champion,
        'role': role,
        'summoner_name': summoner_name,
        'enemy_champion': enemy_champion,
        'region': region,
        'rank': rank,
        'version': version,
        'id': match_id
    }
    title = get_title(match_info)
    match_info['title'] = title
    print(f'[SPECTATOR] - Spectating {title}')

    try:
        handle_game(match_info, player_position)
    except subprocess.CalledProcessError:
        return
    handle_postgame(match_info)

