import io
import json

from lib import constants


def get_videos_to_upload():
    with open(constants.VIDEOS_TO_UPLOAD, 'r') as f:
        return json.load(f)

def write_to_file(recorded_games):
    with open(constants.VIDEOS_TO_UPLOAD, 'w') as f:
        json.dump(recorded_games, f, indent=2)


def remove_to_upload(match_id):
    print(f'Deleting {match_id} from {constants.VIDEOS_TO_UPLOAD}')
    videos = get_videos_to_upload()
    videos = [game_data for game_data in videos if game_data.get('match_id') != match_id]
    write_to_file(videos)


def add_video(game):

    videos = get_videos_to_upload()
    try:
        next(g for g in videos if g.get('match_id') == game.get('match_id'))
    except StopIteration:
        videos.append(game)
        write_to_file(videos)
        return
    print('Match already recording on opgg.')



