import logging
import os
import shutil
import sys
import time

import cassiopeia

from dotenv import load_dotenv

from lib.extractors.league_of_graphs import ObserverKeyNotFoundException, ReplaysDownException
from lib.managers.highlight_creator import create_highlights
from lib.managers.upload_manager import empty_queue

load_dotenv()

from lib.managers.recorded_games_manager import delete_game

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')

import traceback

from lib.managers.player_finder_manager import get_finished_recorded_games, get_player_with_most_kills
from lib.spectator import spectate, DiskFullException, wait_seconds, NameChangedException

config = cassiopeia.get_default_config()
config['pipeline']['RiotAPI']['limiting_share'] = 0.5
config['pipeline']['RiotAPI']['api_key'] = os.getenv("RIOT_KEY")

cassiopeia.apply_settings(config)


def check_enough_memory():
    total_space, used_space, free_space = shutil.disk_usage("D:")
    total_space, used_space, free_space = (total_space // (2 ** 30)), (used_space // (2 ** 30)), (
            free_space // (2 ** 30))
    if free_space < 15:
        create_highlights()
    else:
        print(f'{free_space}GB is enough memory')

def main():
    while True:

        try:
            check_enough_memory()
            finished_games = get_finished_recorded_games()
            if not len(finished_games):
                print(f'{len(finished_games)} finished games, waiting.')
                wait_seconds(30)
                continue
            player_data = get_player_with_most_kills(finished_games)
            try:
                spectate(player_data)
            except ReplaysDownException:
                print('Replays are down.')
                time.sleep(60 * 60)
                break
            except NameChangedException:
                print('Name changed, deleting game.')
                match_id = player_data.get('mongo_game').get('match_id')
                delete_game(match_id)
                continue

        except DiskFullException as e:
            print(f'Disk is full ({e.disk_space})')
            break
        except Exception as e:
            print(traceback.format_exc())
            time.sleep(60)


if __name__ == '__main__':
    main()
