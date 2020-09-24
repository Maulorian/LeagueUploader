import os
import time
import traceback

import cassiopeia
from dotenv import load_dotenv
load_dotenv()

from lib.managers.player_finder_manager import find_ladder_player
from lib.spectator import spectate

cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))
WAITING_TIME = 10

while True:
    try:
        match_data = find_ladder_player()
        if match_data:
            spectate(match_data)
    except Exception as e:
        traceback.print_exc()

