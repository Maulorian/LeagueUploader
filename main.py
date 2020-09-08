import os
import time
import cassiopeia

from challenger_finder import find_player
import spectator

settings = {
    "pipeline": {
        # "Cache": {
        #     'expirations':{
        #         "CurrentMatch": 0,
        #     }
        # },
        "RiotAPI": {
            "api_key": os.getenv("RIOT_KEY")
        },
    },

}
cassiopeia.apply_settings(settings)
WAITING_TIME = 10

running = True
while running:
    match_data = find_player()
    if match_data:
        spectator.spectate(match_data)
    else:
        print(f'Nothing found, waiting {WAITING_TIME}s')
        time.sleep(WAITING_TIME)
