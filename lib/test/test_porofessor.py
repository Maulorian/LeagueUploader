import os
import unittest

import cassiopeia as cass
from cassiopeia import Region
from dotenv import load_dotenv

from lib.extractors import porofessor_extractor
from lib.utils import pretty_print

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)

class TestPorofessor(unittest.TestCase):

    def test_get_match_data(self):
        player_name = 'ping xiba'
        region = 'KR'
        pretty_print(porofessor_extractor.get_match_data(player_name, region))

    def test_request_recording(self):
        name = '한국산호랑이'
        region = 'KR'
        porofessor_extractor.request_recording(name, region)