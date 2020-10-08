import os
import unittest
from datetime import datetime

import cassiopeia as cass
from cassiopeia import Region, get_summoner
from dotenv import load_dotenv

from lib import utils
from lib.extractors.recording_enabler import enable_challengers_games_recording
from lib.extractors.opgg_extractor import get_pro_players_info, request_recording, get_match_data, \
    get_match_recording_settings
from lib.managers import recorded_games_manager
from lib.utils import pretty_print

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)

class TestOPGGExtractor(unittest.TestCase):
    def test_get_pro_players_names(self):
        players = get_pro_players_info(Region.korea.value)
        utils.pretty_print(players)

    def test_request_recording(self):
        region = Region.korea
        request_recording(4697636742, region)

    def testaze(self):
        region = Region.korea
        region = Region.europe_west
        summoner_name = 'Sαcre'
        summoner = get_summoner(name=summoner_name, region=region)
        match = summoner.current_match
        match_id = match.id
        duration = match.duration

        request_worked = request_recording(match_id, region)
        if request_worked:
            observer_key = match.observer_key
            match = {
                "observer_key": observer_key,
                "match_id": match_id,
                "region": region.value,
                "duration": duration.seconds,
                "requested_recording_at": f'{datetime.now()}',
                "summoner_name": summoner_name
            }
            # recorded_games_manager.add_game(match)

    def test_enable_challengers_games_recording(self):
        enable_challengers_games_recording()


    def test_get_observer_key(self):
        match_id = 4699722020
        region = 'KR'
        print(get_match_recording_settings(match_id, region))

    def test_get_match_data(self):
        summoner_name = 'Agurin'
        region = 'EUW'
        get_match_data(summoner_name, region)
