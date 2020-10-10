import unittest
from dotenv import load_dotenv

load_dotenv()
from lib.managers import recorded_games_manager
from lib.managers.recorded_games_manager import get_recorded_games, delete_game
from lib.utils import pretty_print


class TestRecordedGames(unittest.TestCase):
    def test_add_game(self):
        game = {
            'match_id': 'match_id',
            'observer_key': 'observer_key',
            'region': 'region',
        }
        recorded_games_manager.add_game(game)

    def test_get_recorded_games(self):
        pretty_print(get_recorded_games())


    def test_delete_game(self):
        delete_game(4706529099)
