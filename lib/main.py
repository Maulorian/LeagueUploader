from dotenv import load_dotenv

from lib.utils import pretty, pretty_print

load_dotenv()
import os
import sys

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')

import traceback
import cassiopeia

from lib.managers.player_finder_manager import get_finished_recorded_games, get_player_with_most_kills
from lib.spectator import spectate, DiskFullException, wait_seconds

config = cassiopeia.get_default_config()
config['pipeline']['RiotAPI']['limiting_share'] = 0.5
config['pipeline']['RiotAPI']['api_key'] = os.getenv("RIOT_KEY")

cassiopeia.apply_settings(config)
while True:
    try:
        finished_games = get_finished_recorded_games()
        if not len(finished_games):
            print(f'{len(finished_games)} finished games, waiting.')
            wait_seconds(30)
            continue
        player_data = get_player_with_most_kills(finished_games)
        spectate(player_data)

    except DiskFullException as e:
        print(f'Disk is full ({e.disk_space})')
        break
    except Exception as e:
        traceback.print_exc()
        break
