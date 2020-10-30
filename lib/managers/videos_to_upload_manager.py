import io
import json
import logging

from lib import constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_match_data_to_upload():
    with open(constants.VIDEOS_TO_UPLOAD, 'r') as f:
        return json.load(f)


def write_to_file(recorded_games):
    with open(constants.VIDEOS_TO_UPLOAD, 'w') as f:
        json.dump(recorded_games, f, indent=2)


def remove_match_data(match_id):
    logger.info(f'Deleting {match_id} from {constants.VIDEOS_TO_UPLOAD}')
    videos = get_match_data_to_upload()
    videos = [game_data for game_data in videos if game_data.get('match_id') != match_id]
    write_to_file(videos)


def add_match_data(match_data):
    videos = get_match_data_to_upload()
    try:
        next(g for g in videos if g.get('match_id') == match_data.get('match_id'))
    except StopIteration:
        videos.append(match_data)
        write_to_file(videos)
