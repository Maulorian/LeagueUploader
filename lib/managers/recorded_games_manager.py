import logging

from pymongo import UpdateOne, DeleteOne

from lib.mongo import mongo_manager
from lib.utils import log_name

MATCHES = 'matches'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@log_name
def get_recorded_games():
    logger.info(f'Getting games from MongoDB')
    recorded_games_collection = mongo_manager.get_recorded_games_collection()
    games = [game for game in recorded_games_collection.find({})]
    logger.info(f'Found {len(games)} games')
    return games


def delete_game(match_id):
    recorded_games_collection = mongo_manager.get_recorded_games_collection()

    recorded_games_collection.delete_one({'match_id': match_id})
    logger.info(f'Deleted {match_id}')


def delete_games(match_ids):
    print(f'Deleting {len(match_ids)} games..')
    if len(match_ids) == 0:
        return
    delete_ones = []
    for match_id in match_ids:
        delete_ones.append(DeleteOne({'match_id': match_id}))
    recorded_games_collection = mongo_manager.get_recorded_games_collection()
    recorded_games_collection.bulk_write(delete_ones)
    print(f'Deleted {len(match_ids)} games.')


def update_games(games):
    if len(games) == 0:
        return
    update_ones = []
    for game in games:
        update_ones.append(UpdateOne({'match_id': game.get('match_id')}, {'$set': game}))
    recorded_games_collection = mongo_manager.get_recorded_games_collection()
    recorded_games_collection.bulk_write(update_ones)
