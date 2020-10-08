import sys
import unittest

from lib.managers import replay_api_manager
from lib.managers.replay_api_manager import get_formated_timestamp, get_player_summoner_spells, get_active_player_data, \
    get_players_data, get_player_events, get_events, get_recording_time
from lib.utils import pretty_print

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')


class TestReplayAPIManager(unittest.TestCase):

    def test_get_timestamp(self):
        timestamp = get_formated_timestamp(70)
        assert timestamp == '01:10'
        timestamp = get_formated_timestamp(1000)
        print(timestamp)
        assert timestamp == '16:40'

    def test_get_player_kills(self):
        pretty_print(get_events())
        players_data = get_players_data()
        for player_data in players_data:
            pretty_print(get_player_events(player_data.get('summonerName'), 0))

    def test_get_player_summoner_spells(self):
        player_data = replay_api_manager.get_player_data('Xin Zhao')
        print(player_data.get('summonerSpells'))
        summoners_spells = get_player_summoner_spells(player_data)
        print(summoners_spells)

    def test_get_active_player_data(self):
        print(get_active_player_data())

    def test_game(self):
        game_finished = replay_api_manager.game_finished()

    def test_get_lateness(self):
        recording_times = {
            1773.3340301513672: 1776.59326171875,
            1776.59326171875: 1773.3340301513672
        }
        event_game_time = 1778.310302734375
        print(get_recording_time(recording_times, event_game_time))
