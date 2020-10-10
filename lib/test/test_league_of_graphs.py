import os
import unittest

import cassiopeia as cass
from cassiopeia import Region
from dotenv import load_dotenv

from lib.extractors import porofessor_extractor
from lib.extractors.league_of_graphs import get_players_data
from lib.utils import pretty_print

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)

class TestLeagueOfGraphs(unittest.TestCase):

    def test_get_match_data(self):
        match_id = 4706529099
        region = 'KR'
        pretty_print(get_players_data(match_id, region))

    def test_request_recording(self):
        name = '한국산호랑이'
        region = 'KR'
        porofessor_extractor.request_recording(name, region)