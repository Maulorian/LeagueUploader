import subprocess
import time

import cassiopeia as cass
import requests
from roleidentification import pull_data
from roleidentification.utilities import get_team_roles

import league_interactions
import obs

ROLE_INDEXES = ['top', 'jungle', 'middle', 'bottom', 'utility']

champion_roles = pull_data()
random_match = False
summoner_index = -1
summoner_name = "MRS bëansu"

cass.set_riot_api_key("RGAPI-664087f0-53b1-4c6c-b469-49d887d216d5")
cass.set_default_region("EUW")


def get_role(summoner_team, champion):
    roles = get_team_roles(summoner_team, champion_roles)
    champion_names = {c.name: summoner_role.name for summoner_role, c in roles.items()}
    return champion_names[champion.name]


def get_summoner_champion(participants):
    for p in participants:
        if p.summoner.name == summoner_name:
            return p.champion


def get_summoner_team(summoner_champion, participants):
    for p in participants:
        if p.champion.id == summoner_champion.id:
            return p.team

obs.open()
summoner = cass.get_summoner(name=summoner_name)
match = summoner.current_match
match_id = match.id
participants = match.participants

champion = get_summoner_champion(participants)
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

# in_game = False
# while not in_game:
#     try:
#         playback = replay.check_playback()
#         if playback['paused']:
#             print('match is still paused')
#             time.sleep(3)
#             continue
#         print("Match has started")
#         in_game = True
#     except requests.exceptions.ConnectionError:
#         print("Match not started, waiting 1s.")
#         time.sleep(3)

def countdown(sec):
    for s in range(sec):
        print(sec - s)
        time.sleep(1)
countdown(30)
league_interactions.select_summoner(team, role_index)
countdown(2)
# replay.enable_recording_settings()
countdown(2)
league_interactions.start_recording()

# while in_game:
#     try:
#         replay.check_playback()
#         print("Still in game, waiting.")
#         time.sleep(5)
#     except requests.exceptions.ConnectionError:
#         in_game = False
#         print("Game ended.")

# replay.disable_recording_settings()
# obs.close()
# league_interactions.close_game()
#
# title = f'{summoner_name} - {champion}'
# description = ''
# upload_manager.upload_video(title, description)