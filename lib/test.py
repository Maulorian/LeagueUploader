import os
from dotenv import load_dotenv

from lib.managers import replay_api_manager
from lib.managers.replay_api_manager import game_finished, game_started

load_dotenv()
import pprint
import cassiopeia as cass
from cassiopeia import Region, get_current_match, get_summoner, set_riot_api_key
from lib.extractors.porofessor_extractor import get_match_data

from lib.managers.league_manager import start_game
cass.set_riot_api_key(os.getenv("RIOT_KEY"))
from lib.spectator import get_summoner_current_match, close_programs

# pp = pprint.PrettyPrinter(indent=2)
# cass.set_riot_api_key(os.getenv("RIOT_KEY"))
print(game_started())