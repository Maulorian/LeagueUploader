import os
import subprocess
import time

import cassiopeia as cass
import datapipelines
import requests
from roleidentification import pull_data
from roleidentification.utilities import get_team_roles

import lol_input_sender
import obs
import replay
import upload_manager

from dotenv import load_dotenv
load_dotenv()

ROLE_INDEXES = ['top', 'jungle', 'middle', 'bottom', 'utility']
cass.set_riot_api_key(os.getenv("RIOT_KEY"))
cass.set_default_region("EUW")
champion_roles = pull_data()


def get_role(summoner_team, champion):
    roles = get_team_roles(summoner_team, champion_roles)
    champion_names = {c.name: summoner_role.name for summoner_role, c in roles.items()}
    return champion_names[champion.name]


def get_summoner_champion(participants, summoner_name):
    for p in participants:
        if p.summoner.name == summoner_name:
            return p.champion


def get_summoner_team(summoner_champion, participants):
    for p in participants:
        if p.champion.id == summoner_champion.id:
            return p.team


def get_current_match(summoner):
    try:
        match = summoner.current_match
        return match
    except datapipelines.common.NotFoundError:
        return None


def wait_finish():
    current_time = replay.get_current_game_time()
    while True:
        new_time = replay.get_current_game_time()
        print(new_time)
        print(current_time)
        if new_time == current_time:
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
        is_paused = replay.is_game_paused()
        if is_paused:
            print("[SPECTATOR] - Match is still paused")
            time.sleep(1)
            continue
        print("[SPECTATOR] - Match has started")
        break


def countdown(sec):
    for s in range(sec):
        print(sec - s)
        time.sleep(1)


def spectate(summoner_name):

    obs.start()
    summoner = cass.get_summoner(name=summoner_name)
    match = get_current_match(summoner)

    match_id = match.id
    participants = match.participants

    champion = get_summoner_champion(participants, summoner_name)
    team = get_summoner_team(champion, participants)
    role = get_role(team, champion)
    role_index = ROLE_INDEXES.index(role)

    print(f'{summoner_name} is playing {role} on {team.side}')
    r = requests.get(f'https://euw.op.gg/match/new/batch/id={match_id}')
    # print(summoner.current_match)
    replay_command = r.text

    with open('replay.bat', 'w') as f:
        f.write(replay_command)

    subprocess.call(['replay.bat'])
    wait_for_game_launched()
    countdown(5)
    lol_input_sender.start_recording()

    wait_for_game_start()
    countdown(2)
    lol_input_sender.select_summoner(team, role_index)
    replay.enable_recording_settings()
    countdown(2)

    wait_finish()

    # replay.disable_recording_settings()
    obs.close()
    lol_input_sender.close_game()

    title = f'{summoner_name} - {champion}'
    description = ''
    upload_manager.upload_video(title, description)
