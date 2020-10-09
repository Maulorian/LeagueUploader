import os
import unittest

import datapipelines
from cassiopeia import cassiopeia, Queue
from dotenv import load_dotenv

load_dotenv()

from lib.managers.recorded_games_manager import get_recorded_games
from lib.managers.player_finder_manager import get_player_with_most_kills, get_finished_recorded_games
from lib.utils import pretty

cassiopeia.set_riot_api_key(os.getenv("RIOT_KEY"))


class TestPlayerFinder(unittest.TestCase):

    def testaze(self):
        finished_games = get_finished_recorded_games()

        player_data = get_player_with_most_kills(finished_games)

    def test_get_player_with_most_kills(self):
        game_data = {
            'match_id': 4703926887,
            'region': 'KR'
        }
        match_id = game_data.get('match_id')
        region = game_data.get('region')
        match = cassiopeia.get_match(match_id, region=region)
        participants = match.participants
        players_data = {}
        game_data['players_data'] = players_data
        for participant in participants:
            summoner = participant.summoner
            summoner_name = summoner.name
            kills = participant.stats.kills
            # ranked_league = summoner.league_entries[Queue.ranked_solo_fives]
            # tier = ranked_league.tier
            # lp = ranked_league.league_points

            tier = 'a'
            lp = 'z'
            players_data[summoner_name] = {
                'tier': tier,
                'lp': lp,
                'kills': kills
            }
        pretty(game_data)
