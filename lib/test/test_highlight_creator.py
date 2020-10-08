from lib.managers.highlight_creator import HighlightCreator

events =  [
      {
        "type": "kill",
        "victim": "Akali",
        "time": 238.76060724258423
      },
      {
        "type": "kill",
        "victim": "Akali",
        "time": 345.4773919582367
      },
      {
        "type": "death",
        "killer": "reekerzz",
        "time": 347.1614739894867
      },
      {
        "type": "kill",
        "victim": "Akali",
        "time": 449.15594482421875
      },
      {
        "type": "death",
        "killer": "D\u00e9adly",
        "time": 512.6180024147034
      },
      {
        "type": "death",
        "killer": "WhiteKnight108",
        "time": 708.6006181240082
      },
      {
        "type": "kill",
        "victim": "Senna",
        "time": 756.190395116806
      },
      {
        "type": "kill",
        "victim": "Leona",
        "time": 759.0617225170135
      },
      {
        "type": "kill",
        "victim": "Ryze",
        "time": 770.6645932197571
      },
      {
        "type": "kill",
        "victim": "Akali",
        "time": 789.4919936656952
      },
      {
        "type": "death",
        "killer": "D\u00e9adly",
        "time": 803.2751166820526
      },
      {
        "type": "assist",
        "victim": "Skarner",
        "time": 803.3085639476776
      },
      {
        "type": "turret_kill",
        "time": 807.0815603733063
      },
      {
        "type": "death",
        "killer": "D\u00e9adly",
        "time": 907.7870388031006
      },
      {
        "type": "assist",
        "victim": "Ryze",
        "time": 1004.979020357132
      },
      {
        "type": "kill",
        "victim": "Skarner",
        "time": 1023.7059869766235
      },
      {
        "type": "turret_kill",
        "time": 1041.7280659675598
      },
      {
        "type": "death",
        "killer": "WhiteKnight108",
        "time": 1077.0331292152405
      },
      {
        "type": "assist",
        "victim": "Skarner",
        "time": 1234.506926059723
      },
      {
        "type": "kill",
        "victim": "Leona",
        "time": 1246.388867855072
      },
      {
        "type": "game_end",
        "time": 1380.7230682373047
      }
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
        file_name = '04_October_2020____23_13_57____2560x1440.mkv'
        hl_creator = HighlightCreator(file_name, events)
        hl_creator.create_highlight()
