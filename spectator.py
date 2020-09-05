import json
import os
import subprocess
import time

import cassiopeia as cass
import datapipelines
import requests
from cassiopeia import GameType, Queue

import league_manager
import obs_manager
import opgg_manager
import porofessor_manager
import replay_api_manager
import upload_manager

from dotenv import load_dotenv
load_dotenv()

WAIT_TIME = 1
SURREND_TIME = 15*60
ROLE_INDEXES = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
cass.set_riot_api_key(os.getenv("RIOT_KEY"))
cass.set_default_region("EUW")

def get_challenger_in_ranked_match(challengers):
    print(f'[OPGG MANAGER] - Getting Player in Ranked Game')

    for summoner_name in challengers:
        summoner = cass.get_summoner(name=summoner_name)
        match = get_current_match(summoner)
        duration = porofessor_manager.get_current_match_duration(summoner)

        time.sleep(0.2)
        if match is None:
            continue
        if match.type != GameType.matched:
            continue
        print(f'[OPGG MANAGER] - Duration={duration}')
        if duration is not None:
            just_started = duration.seconds-2*60 < 0
            if not just_started:
                continue

        if match.queue != Queue.ranked_solo_fives:
            continue

        return summoner_name

def get_challenger_player(from_ladder=False):
    print(f'[OPGG MANAGER] - Getting Challenger Player {{from_ladder={from_ladder}}}')
    if from_ladder:
        challengers = opgg_manager.get_top100_challengers()
    else:
        challengers = opgg_manager.get_spectate_tab_players()

    challenger = get_challenger_in_ranked_match(challengers)
    return challenger


def get_summoner_champion(participants, summoner_name):
    for p in participants:
        if p.summoner.name == summoner_name:
            return p.champion


def get_current_match(summoner):
    try:
        match = summoner.current_match
        print(f'[SPECTATOR] - Getting current match: {match.id}')
        return match
    except datapipelines.common.NotFoundError:
        return None


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
        time.sleep(1)


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


def get_game_current_version():
    r = requests.get('https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json')
    version = r.json()['patches'][-1]['name']
    return version


def handle(summoner_name):
    pass


def wait_seconds(WAIT_TIME):
    print(f"[SPECTATOR] - Waiting {WAIT_TIME}")
    time.sleep(WAIT_TIME)


def find_and_launch_game(match_id):
    r = requests.get(f'https://euw.op.gg/match/new/batch/id={match_id}')

    replay_command = r.text

    with open('replay.bat', 'w') as f:
        f.write(replay_command)

    subprocess.call(['replay.bat'], stdout=subprocess.DEVNULL)


def spectate(summoner_name):
    obs_manager.start()

    summoner = cass.get_summoner(name=summoner_name)
    match = get_current_match(summoner)
    match_id = match.id
    participants = match.participants

    player_champion = get_summoner_champion(participants, summoner_name)
    players = porofessor_manager.get_player_positions(summoner)
    player_position = players.index(summoner_name)

    enemy_position = (player_position + 5) % 10
    enemy_summoner_name = players[enemy_position]
    enemy_champion = get_summoner_champion(participants, enemy_summoner_name)
    print(f'enemy_champion: {enemy_champion}')
    role = ROLE_INDEXES[player_position % 5]
    ranked_stats = summoner.league_entries.fives
    tier = ranked_stats.tier
    league_points = ranked_stats.league_points

    version = get_game_current_version()
    champion_name = player_champion.name
    enemy_champion_name = enemy_champion.name
    champion_region_value = player_champion.region.value
    title = f'{champion_name} {role} "{summoner_name}" vs {enemy_champion_name} - {champion_region_value} {tier} {league_points} LP Patch {version}'
    print(f'[SPECTATOR] - Spectating {title}')

    find_and_launch_game(match_id)
    wait_for_game_launched()

    time.sleep(WAIT_TIME)

    replay_api_manager.enable_recording_settings()
    wait_seconds(WAIT_TIME)

    wait_for_game_start()
    league_manager.select_summoner(player_position)
    wait_seconds(WAIT_TIME)

    league_manager.start_recording()

    wait_finish()

    obs_manager.close_obs()
    league_manager.close_game()

    description = ''
    metadata = {
        'title': title,
        'description': description,
        'tags': [champion_name, enemy_champion_name],
    }

    upload_manager.add_video_to_queue(metadata)
