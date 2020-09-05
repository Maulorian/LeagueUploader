import os
import subprocess
import time

import cassiopeia as cass
import datapipelines
import requests

import league_manager
import obs_manager
import opgg_manager
import replay
import upload_manager

from dotenv import load_dotenv
load_dotenv()

WAIT_TIME = 1
SURREND_TIME = 15*60
ROLE_INDEXES = ['Top', 'Jungle', 'Middle', 'Bottom', 'Support']
cass.set_riot_api_key(os.getenv("RIOT_KEY"))
cass.set_default_region("EUW")

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
    current_time = replay.get_current_game_time()
    while True:
        new_time = replay.get_current_game_time()
        paused = replay.is_game_paused()
        # if not paused and new_time == current_time:
        if new_time == current_time and new_time >= SURREND_TIME:
            print("[SPECTATOR] - Game ended")
            return
        current_time = new_time
        print("[SPECTATOR] - Still in game")
        time.sleep(1)


def wait_for_game_launched():
    while True:
        try:
            if replay.game_launched():
                print("[SPECTATOR] - Game has launched")
                break
        except (requests.exceptions.ConnectionError, subprocess.CalledProcessError):
            print("[SPECTATOR] - Game not yet launched")
            time.sleep(1)


def wait_for_game_start():
    while True:
        current_time = replay.get_current_game_time()
        if current_time <= 5:
            print("[SPECTATOR] - Match is still paused")
            wait_seconds(WAIT_TIME)
            continue
        print("[SPECTATOR] - Match has started")
        break


def handle(summoner_name):
    pass


def wait_seconds(WAIT_TIME):
    print(f"[SPECTATOR] - Waiting {WAIT_TIME}")
    time.sleep(WAIT_TIME)


def spectate(summoner_name):

    obs_manager.start()
    summoner = cass.get_summoner(name=summoner_name)
    match = get_current_match(summoner)
    match_id = match.id
    print(f'[SPECTATOR] - Spectating {summoner_name}({summoner.id}) in match {match_id}')
    participants = match.participants

    champion = get_summoner_champion(participants, summoner_name)

    position = opgg_manager.get_player_position(summoner)
    role = ROLE_INDEXES[position % 5]

    print(f'{summoner_name} is {role} in position {position}')
    r = requests.get(f'https://euw.op.gg/match/new/batch/id={match_id}')

    replay_command = r.text

    with open('replay.bat', 'w') as f:
        f.write(replay_command)

    subprocess.call(['replay.bat'])

    wait_for_game_launched()
    time.sleep(WAIT_TIME)

    replay.enable_recording_settings()
    wait_seconds(WAIT_TIME)

    wait_for_game_start()
    league_manager.select_summoner(position)
    wait_seconds(WAIT_TIME)

    league_manager.start_recording()

    wait_finish()

    # replay.disable_recording_settings()
    obs_manager.close()
    league_manager.close_game()

    title = f'{champion.name} {role} ({summoner_name}) - {champion.region.value} Challenger Patch {10.18}'
    description = ''
    video_id = upload_manager.upload_video()
    metadata = {
        'title': title,
        'description': description,
        'tags': [champion.name],
    }
    upload_manager.update_video(video_id, metadata)
