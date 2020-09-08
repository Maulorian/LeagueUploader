import subprocess
import time

import cassiopeia as cass
import requests

from lib.externals_sites.opgg_extractor import OPGGExtractor
from lib.managers import replay_api_manager, obs_manager, league_manager, upload_manager

from lib.builders import description_builder, tags_builder

from dotenv import load_dotenv

from lib.builders.title_builder import get_title
from lib.managers.game_cfg_manager import enable_settings, disable_settings

load_dotenv()

WAIT_TIME = 1
SURREND_TIME = 15 * 60
ROLE_INDEXES = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
BAT_PATH = 'replay.bat'


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


def handle_game(match_info, player_position):
    obs_manager.start()
    enable_settings()

    time.sleep(WAIT_TIME)

    find_and_launch_game(match_info)
    wait_for_game_launched()
    time.sleep(WAIT_TIME)



    replay_api_manager.enable_recording_settings()
    wait_seconds(WAIT_TIME)

    wait_for_game_start()
    player_champion = match_info.get('player_champion')
    match_info['skin_id'] = replay_api_manager.get_player_data(player_champion)
    league_manager.select_summoner(player_position)
    wait_seconds(WAIT_TIME)


    league_manager.toggle_recording()

    wait_finish()

    league_manager.toggle_recording()

    obs_manager.close_obs()
    league_manager.close_game()
    wait_seconds(WAIT_TIME)

    disable_settings()


def handle_postgame(match_info):
    wait_seconds(WAIT_TIME * 5)
    description = description_builder.get_description(match_info)
    tags = tags_builder.get_tags(match_info)
    title = match_info.get('title')
    thumbnail_url = match_info.get('thumbnail_url')
    metadata = {
        'title': title,
        'description': description,
        'tags': tags,
        'thumbnail_url': thumbnail_url
    }
    upload_manager.add_video_to_queue(metadata)


# def get_thumbnail_url(player_champion):
#     player_data = replay_api_manager.get_player_data(player_champion)
#     skin_id = player_data.get('skinID')
#     with open('splashart_urls.json', 'r') as file:
#         champions = json.load(file)
#         champion_splash_arts = champions[player_champion]
#         splash_art = champion_splash_arts.get(skin_id)
#         return splash_art


def spectate(match_data):
    region = match_data.get('region')
    summoner_name = match_data.get('summoner_name')

    summoner = cass.get_summoner(region=region, name=summoner_name)
    match = summoner.current_match
    for p in match.participants:
        print(p.champion)
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
        'id': match_id,
    }
    title = get_title(match_info)
    match_info['title'] = title
    print(f'[SPECTATOR] - Spectating {title}')

    try:
        handle_game(match_info, player_position)
    except subprocess.CalledProcessError:
        return
    handle_postgame(match_info)
