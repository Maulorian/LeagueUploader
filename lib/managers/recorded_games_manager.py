import io
import json

from lib import constants


def get_recorded_games():
    with open(constants.RECORDED_GAMES, 'r') as f:
        return json.load(f)


def write_to_file(recorded_games):
    with open(constants.RECORDED_GAMES, 'w') as f:
        json.dump(recorded_games, f, indent=2)

def already_enabled(match_id):
    recorded_games = get_recorded_games()
    return any(g.get('match_id') == match_id for g in recorded_games)

def delete_game(match_id):
    print(f'Deleting {match_id} from the file')
    recorded_games = get_recorded_games()
    recorded_games = [game_data for game_data in recorded_games if game_data.get('match_id') != match_id]
    write_to_file(recorded_games)


def add_game(game):
    print(f'Adding {game}')
    recorded_games = get_recorded_games()
    if not any(g.get('match_id') == game.get('match_id') for g in recorded_games):
        recorded_games.append(game)
        write_to_file(recorded_games)
        return

    print('Match already recording on opgg.')
