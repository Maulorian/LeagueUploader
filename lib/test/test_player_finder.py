import unittest

from dotenv import load_dotenv

load_dotenv()
from lib.managers.player_finder_manager import current_challenger_games
from lib.utils import pretty_print


class TestPlayerFinder(unittest.TestCase):
    def test_challengers_currently_in_game(self):
        pretty_print(current_challenger_games())