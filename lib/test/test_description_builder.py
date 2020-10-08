import random

from cassiopeia import Region

from lib.builders.description_builder import get_description, get_players_opgg

import sys
import unittest

from lib.extractors import opgg_extractor
from lib.extractors.opgg_extractor import spectate_tab
from lib.managers.player_finder_manager import find_ladder_player, get_match_data
from lib.managers.replay_api_manager import get_formated_timestamp

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')


class TestDescription(unittest.TestCase):

    def test_get_players_opgg(self):
        region = Region.korea.value
        players = spectate_tab(region)

        summoner_name = random.choice(players)

        match_data = get_match_data(summoner_name, region)
        print(get_players_opgg(match_data))