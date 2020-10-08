import os
import threading
import traceback

import cassiopeia
from dotenv import load_dotenv

load_dotenv()

from lib.extractors import recording_enabler
from lib.managers.player_finder_manager import get_finished_recorded_games, get_player_with_most_kills


from lib.spectator import spectate, DiskFullException, wait_seconds

cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))
op_gg_recording_enabler_thread = threading.Thread(target=recording_enabler.loop)
# op_gg_recording_enabler_thread.start()

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


