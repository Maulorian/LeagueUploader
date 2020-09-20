import json

import cassiopeia
from cassiopeia import Region

from lib.managers.league_manager import close_game
from lib.managers.replay_api_manager import get_player_data, get_player_skin, get_players_data, get_player_position
from lib.managers.thumbnail_manager import save_champion_splashart, add_details_to_splashart, get_tree_image, get_rune_image
from lib.managers.upload_manager import add_video_to_queue
from lib.spectator import get_tier_lp_from_rank

match_info =  {
    "description": "Players opgg's:\n\nSion Challenger (889 LP) :  http://www.op.gg/summoner/userName=URGOLD\nHecarim Challenger (1019 LP) :  http://www.op.gg/summoner/userName=can+see+you\nIrelia Challenger (717 LP) :  http://www.op.gg/summoner/userName=ShanksT+T\nSenna Master (41 LP) :  http://www.op.gg/summoner/userName=YukiJudaii\nCassiopeia Challenger (1326 LP) :  http://www.op.gg/summoner/userName=HuyaTvJincanyi\nWukong Master (3 LP) :  http://www.op.gg/summoner/userName=Worth+1t\nLillia Challenger (1203 LP) :  http://www.op.gg/summoner/userName=I+still+remember\nTalon Challenger (1275 LP) :  http://www.op.gg/summoner/userName=FPXzhaoAP4506303\nJhin Grandmaster (590 LP) :  http://www.op.gg/summoner/userName=Gen+G+Ruler\nPantheon Grandmaster (623 LP) :  http://www.op.gg/summoner/userName=HUYATV+Osu\n",
    "tags": [
      "irelia challenger",
      "irelia mid ",
      "irelia challenger KR",
      "irelia mid KR",
      "irelia vs talon",
      "shankst t irelia",
      "shankst t"
    ],
    "title": "Irelia Mid vs Talon - ShanksT T KR Challenger (717 LP) Patch 10.19",
    "player_champion": "Irelia",
    "skin_name": "Infiltrator Irelia",
    "items": [
      3802,
      3802,
      3802,
      3802
    ],
    "runes": {
      "keystone": 8010,
      "secondaryRuneTree": 8300
    },
    "summonerSpells": [
      "Flash",
      "Ignite"
    ],
    "path": "D:\\LeagueReplays\\20_September_2020____18_18_41____2560x1440.mkv",
    "region": "KR",
    "tier": "Challenger",
    "lp": "717",
    "role": "Mid"
  }
add_details_to_splashart(match_info)
# get_tree_image(8000)
