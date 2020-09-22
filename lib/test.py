
import json

import cassiopeia
from cassiopeia import Region

from lib.managers.league_manager import close_game, bugsplat_exists, kill_bugsplat
from lib.managers.replay_api_manager import get_player_data, get_player_skin, get_players_data, get_player_position
from lib.managers.thumbnail_manager import save_champion_splashart, add_details_to_splashart, get_tree_image, get_rune_image
from lib.managers.upload_manager import add_video_to_queue

# logging.getLogger("imported_module").setLevel(logging.WARNING)
from lib.spectator import get_video_path

match_info = {
    "description": "Players opgg's:\n\nCamille Challenger (882 LP) :  http://euw.op.gg/summoner/userName=SALUT+A+TOUS\nNunu & Willump Grandmaster (364 LP) :  http://euw.op.gg/summoner/userName=Kesha\nTwisted Fate Grandmaster (440 LP) :  http://euw.op.gg/summoner/userName=indimandi\nAshe Grandmaster (657 LP) :  http://euw.op.gg/summoner/userName=Tazaku\nPantheon Challenger (903 LP) :  http://euw.op.gg/summoner/userName=bBeeBohpBbuullii\nJax Grandmaster (531 LP) :  http://euw.op.gg/summoner/userName=Quadrakill+OY\nEkko Challenger (803 LP) :  http://euw.op.gg/summoner/userName=ArribaSBuyakote\nVladimir Grandmaster (616 LP) :  http://euw.op.gg/summoner/userName=Elite500\nJhin Challenger (739 LP) :  http://euw.op.gg/summoner/userName=MASTERCASTERKEKW\nBlitzcrank Grandmaster (640 LP) :  http://euw.op.gg/summoner/userName=Dydoouw\n",
    "tags": [
      "pantheon challenger",
      "pantheon support ",
      "pantheon challenger EUW",
      "pantheon support EUW",
      "pantheon vs blitzcrank",
      "bbeebohpbbuullii pantheon",
      "bbeebohpbbuullii"
    ],
    "title": "Pantheon Support vs Blitzcrank - BBeeBohpBbuullii EUW Challenger (903 LP) Patch 10.19",
    "player_champion": "Pantheon",
    "skin_name": "Full Metal Pantheon",
    "items": [
      3364,
      2055,
      3111,
      3857,
      3123,
      3814,
      3179
    ],
    "runes": {
      "keystone": 8005,
      "secondaryRuneTree": 8100
    },
    "summonerSpells": [
      "Ignite",
      "Flash"
    ],
    "path": "D:\\LeagueReplays\\20_September_2020____20_05_37____2560x1440.mkv",
    "region": "EUW",
    "tier": "Challenger",
    "lp": "903",
    "role": "Sup"
  }
# add_details_to_splashart(match_info)
# get_tree_image(8000)
bugsplat_exists()
kill_bugsplat()
bugsplat_exists()
get_video_path()
