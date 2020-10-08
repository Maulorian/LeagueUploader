import logging

from lib.mongo import mongo_manager

MATCHES = 'matches'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_recorded_games():
    recorded_games_collection = mongo_manager.get_recorded_games_collection()
    games = [game for game in recorded_games_collection.find({})]
    logger.info(f'Found {len(games)} games')
    return games