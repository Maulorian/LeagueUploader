import unittest
from dotenv import load_dotenv

load_dotenv()
from lib.managers.recorded_games_manager import get_recorded_games, delete_game
from lib.utils import pretty_print


class TestRecordedGames(unittest.TestCase):
    def test_get_recorded_games(self):
        pretty_print(len(get_recorded_games()))

    def test_delete_game(self):
        delete_game(4706529099)
