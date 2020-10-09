import os

from dotenv import load_dotenv
import unittest
load_dotenv()

from cassiopeia import Region, get_summoner, set_riot_api_key, get_match
from lib.managers.riot_api_manager import get_all_challenger_players, add_rank_information_to_player
from lib.utils import pretty_print

set_riot_api_key(os.getenv("RIOT_KEY"))


class TestRiotApi(unittest.TestCase):
    def test_get_all_challenger_players(self):
        region = Region.europe_west
        pretty_print(get_all_challenger_players(region))

    def test_get_summoner_current_match(self):
        region = Region.europe_west
        challengers = get_all_challenger_players(region)
        summoner_id = challengers[0].get('summoner_id')
        summoner = get_summoner(id=summoner_id, region=region)
        print(summoner.current_match)
        # pretty_print(get_summoner_current_match(summoner_id, region))

    def test_match_history(self):
        region = Region.korea

        # challengers = get_all_challenger_players(region)
        # summoner_id = challengers[0].get('summoner_id')
        summoner = get_summoner(name='오드아이 베리', region=region)
        matches = summoner.match_history[:10]
        print(len(matches))
        for match in matches:
            print(match.id)
            for part in match.participants:
                print(part.summoner.name, part.champion.name)


    def test_get_match(self):
        match_id = 4703064818
        region = Region.korea
        match = get_match(id=match_id, region=region)
        for p in match.participants:
            print(p.summoner.name)

    def test_add_rank_information_to_player(self):
        region = Region.europe_west
        players_data = {
            'AeQ+Valkyrie': {}
        }
        print(add_rank_information_to_player(players_data, region=region))
