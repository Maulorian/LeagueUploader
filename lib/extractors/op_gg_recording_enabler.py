import os
import time
import traceback
from datetime import datetime

import datapipelines
from cassiopeia import get_summoner, get_match, cassiopeia
from dotenv import load_dotenv

from lib.extractors.opgg_extractor import request_recording
from lib.managers import player_finder_manager, recorded_games_manager
from lib.managers.player_finder_manager import SPECTATOR_DELAY
from lib.utils import pretty_print

load_dotenv()
cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))

def loop():
    while True:
        try:
            enable_challengers_games_recording()
        except Exception:
            traceback.print_exc()
            time.sleep(SPECTATOR_DELAY)

        print(f'Sleeping {SPECTATOR_DELAY} before enabling again.')
        time.sleep(SPECTATOR_DELAY)


def enable_challengers_games_recording():

    current_challenger_games = player_finder_manager.current_challenger_games()

    already_recorded_match = set()

    for game in current_challenger_games:

        match_id = game.get('match_id')
        if match_id in already_recorded_match:
            continue

        region = game.get('region')
        random_summoner_name = list(game.get('players_data').keys())[0]
        summoner = get_summoner(name=random_summoner_name, region=region)
        try:
            match = summoner.current_match

            observer_key = match.observer_key
        except datapipelines.common.NotFoundError:
            continue

        request_worked = request_recording(match_id, region)
        if request_worked:
            match = {
                "observer_key": observer_key,
                "match_id": match_id,
                "region": region,
                "duration": game.get('duration').seconds,
                "requested_recording_at": f'{datetime.now()}',
                'players_data': game.get('players_data')
            }
            recorded_games_manager.add_game(match)
            already_recorded_match.add(match_id)

if __name__ == '__main__':
    loop()