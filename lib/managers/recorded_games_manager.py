import logging

from lib.mongo import mongo_manager

MATCHES = 'matches'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def update_game(match_id, mongo_game):
    recorded_games_collection = mongo_manager.get_recorded_games_collection()
    to_update = {"$set": mongo_game}
    recorded_games_collection.update_one({'match_id': match_id}, to_update)
    logger.info(f'Update {match_id}')

