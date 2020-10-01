import os
import time
import traceback

import cassiopeia
from cassiopeia import datastores
from dotenv import load_dotenv
load_dotenv()

from lib.managers.player_finder_manager import find_ladder_player
from lib.spectator import spectate, DiskFullException, wait_seconds

cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))

while True:
    try:
        match_data = find_ladder_player()
        if match_data:
            spectate(match_data)
        else:
            print("No match found, waiting 60 seconds")
            wait_seconds(60)
    except datastores.riotapi.common.APIRequestError:
        print("Reset API Key")
        break
    except DiskFullException as e:
        print(f'Disk is full ({e.disk_space})')
        break
    except Exception as e:
        traceback.print_exc()


