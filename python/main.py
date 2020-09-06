import time

from python import spectator

WAITING_TIME = 10

running = True
while running:
    challenger = spectator.get_challenger_player(from_ladder=False)
    if challenger:
        spectator.spectate(challenger)
    else:
        print(f'Nothing found, waiting {WAITING_TIME}s')
        time.sleep(WAITING_TIME)