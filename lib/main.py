import os
import time
import cassiopeia

from lib.managers.player_finder_manager import find_ladder_player
from lib.spectator import spectate

cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))
WAITING_TIME = 10

while True:
    match_data = find_ladder_player()
    if match_data:
        spectate(match_data)
    else:
        print(f'Nothing found, waiting {WAITING_TIME}s')
        time.sleep(WAITING_TIME)
