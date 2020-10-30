from lib.managers.highlight_creator import HighlightCreator, create_highlights

events = [

    {
        "type": "kill",
        "victim": "Kalista",
        "recording_time": 853.4270839691162,
        "event_game_time": 856.338134765625
    },
    {
        "type": "assist",
        "victim": "Lee Sin",
        "recording_time": 892.0445156097412,
        "event_game_time": 894.95556640625
    },
    {
        "type": "assist",
        "victim": "Thresh",
        "recording_time": 954.5758876800537,
        "event_game_time": 957.4869384765625
    },
    {
        "type": "assist",
        "victim": "Akali",
        "recording_time": 954.88112449646,
        "event_game_time": 957.7921752929688
    },
    {
        "type": "kill",
        "victim": "Kalista",
        "recording_time": 957.8272304534912,
        "event_game_time": 960.73828125
    },
    {
        "type": "assist",
        "victim": "Lee Sin",
        "recording_time": 961.432149887085,
        "event_game_time": 964.3432006835938
    },
    {
        "type": "kill",
        "victim": "Orianna",
        "recording_time": 969.2978115081787,
        "event_game_time": 972.2088623046875
    },
    {
        "type": "assist",
        "victim": "Thresh",
        "recording_time": 1046.4151210784912,
        "event_game_time": 1049.326171875
    },
    {
        "type": "kill",
        "victim": "Kalista",
        "recording_time": 1058.8471279144287,
        "event_game_time": 1061.7581787109375
    },

]

import os
import unittest
import cassiopeia as cass
from dotenv import load_dotenv

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)


class TestHLCreator(unittest.TestCase):
    def test_create_highlight(self):
        file_name = 'test_video.mkv'
        hl_creator = HighlightCreator(file_name, events)
        hl_creator.create_highlight()

    def test_create_highlights(self):
        create_highlights()
