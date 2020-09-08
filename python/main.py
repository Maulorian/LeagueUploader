import os
import time
import cassiopeia

from challenger_finder import find_ladder_player
import spectator

cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))
WAITING_TIME = 10

running = True
while running:
    match_data = find_ladder_player()
    if match_data:
        spectator.spectate(match_data)
    else:
        print(f'Nothing found, waiting {WAITING_TIME}s')
        time.sleep(WAITING_TIME)
