import os
import unittest

import cassiopeia as cass
from dotenv import load_dotenv

from lib.extractors.league_of_graphs import get_match_recording_settings
from lib.managers.league_manager import start_game

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)

class TestLeagueManager(unittest.TestCase):
    def test_start_game(self):
        match_data = {
            "match_id": 4702923813,
            "region": "KR",
            "duration": 63,
            "players_data": {
                "LaP1s": {}
            }
        }
        start_game(match_data)

    def test_get_match_recording_settings(self):
        match_id = 4702923813
        region = "KR"
        host, observer_key = get_match_recording_settings(match_id, region, "LaP1s")
        print(host, observer_key)
