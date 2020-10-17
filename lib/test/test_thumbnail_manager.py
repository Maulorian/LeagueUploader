import json
import ntpath
import os
import sys
import unittest
import cassiopeia as cass
from dotenv import load_dotenv

from lib.managers import thumbnail_manager
from lib.managers.replay_api_manager import get_formated_timestamp
from lib.managers.thumbnail_manager import get_summoner_spell
from lib.managers.upload_manager import VIDEOS_PATH, upload_video_file, update_video, TO_UPLOAD_PATH
from lib.spectator import get_video_path

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')
load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)


class TestThumbnail(unittest.TestCase):
    def test_get_summoner_spell(self):
        summoner_name = ''
        image = get_summoner_spell(summoner_name)

    def test_create_thumbnail(self):
        match_data = {
            "description": "Players Profiles:\n\nCamille - Grandmaster 531 LP :  http://euw.op.gg/summoner/userName=QloTrGeSdV\nKindred - Grandmaster 368 LP :  http://euw.op.gg/summoner/userName=Strike\nOrianna - Grandmaster 479 LP :  http://euw.op.gg/summoner/userName=JBS\nAphelios - Grandmaster 578 LP :  http://euw.op.gg/summoner/userName=Kobbe\nNautilus - Grandmaster 596 LP :  http://euw.op.gg/summoner/userName=BIG+SUP\n\nMalphite - Challenger 792 LP :  http://euw.op.gg/summoner/userName=Quinncidence\nGraves - Challenger 700 LP :  http://euw.op.gg/summoner/userName=Cedeiix\nSyndra - Challenger 986 LP :  http://euw.op.gg/summoner/userName=Ploxy\nMiss Fortune - Grandmaster 570 LP :  http://euw.op.gg/summoner/userName=FP\u03a7+Lwx\nLeona - Grandmaster 367 LP :  http://euw.op.gg/summoner/userName=GO+Honor\n\n",
            "tags": [
                "miss fortune challenger",
                "miss fortune bot ",
                "miss fortune challenger highlights",
                "miss fortune EUW",
                "miss fortune vs aphelios",
                "fp\u03c7 lwx miss fortune",
                "fp\u03c7 lwx highlights"
            ],
            "title": "Miss Fortune Bot vs Aphelios - 18 kills - Fp\u03c7 Lwx - EUW Grandmaster (570 LP) Patch 10.21",
            "player_champion": "Miss Fortune",
            "skin_name": "Gun Goddess Miss Fortune",
            "items": [
                3031,
                3508,
                3094,
                3046,
                3009
            ],
            "runes": {
                "keystone": 8005,
                "secondaryRuneTree": 8200
            },
            "summonerSpells": [
                "Flash",
                "Heal"
            ],
            "file_name": "17_October_2020____08_20_45____2560x1440.mkv",
            "region": "EUW",
            "tier": "Grandmaster",
            "lp": 570,
            "role": "Bot",
            "events": [
                {
                    "type": "game_start",
                    "recording_time": -1.7668023109436035,
                    "event_game_time": 0.0
                },
                {
                    "type": "kill",
                    "victim": "Nautilus",
                    "recording_time": 298.54334783554077,
                    "event_game_time": 300.3101501464844
                },
                {
                    "type": "death",
                    "killer": "Kobbe",
                    "recording_time": 498.727246761322,
                    "event_game_time": 500.4940490722656
                },
                {
                    "type": "death",
                    "killer": "BIG SUP",
                    "recording_time": 541.3587470054626,
                    "event_game_time": 543.1255493164062
                },
                {
                    "type": "kill",
                    "victim": "Aphelios",
                    "recording_time": 670.3948798179626,
                    "event_game_time": 672.1616821289062
                },
                {
                    "type": "kill",
                    "victim": "Kindred",
                    "recording_time": 672.7450385093689,
                    "event_game_time": 674.5118408203125
                },
                {
                    "type": "kill",
                    "victim": "Orianna",
                    "recording_time": 852.6407294273376,
                    "event_game_time": 854.4075317382812
                },
                {
                    "type": "assist",
                    "victim": "Camille",
                    "recording_time": 933.3086371421814,
                    "event_game_time": 935.075439453125
                },
                {
                    "type": "assist",
                    "victim": "Nautilus",
                    "recording_time": 960.2346014976501,
                    "event_game_time": 962.0014038085938
                },
                {
                    "type": "kill",
                    "victim": "Orianna",
                    "recording_time": 1056.4582953453064,
                    "event_game_time": 1058.22509765625
                },
                {
                    "type": "kill",
                    "victim": "Aphelios",
                    "recording_time": 1080.7109808921814,
                    "event_game_time": 1082.477783203125
                },
                {
                    "type": "kill",
                    "victim": "Nautilus",
                    "recording_time": 1190.961591243744,
                    "event_game_time": 1192.7283935546875
                },
                {
                    "type": "assist",
                    "victim": "Camille",
                    "recording_time": 1242.794599056244,
                    "event_game_time": 1244.5614013671875
                },
                {
                    "type": "kill",
                    "victim": "Orianna",
                    "recording_time": 1274.616864681244,
                    "event_game_time": 1276.3836669921875
                },
                {
                    "type": "assist",
                    "victim": "Kindred",
                    "recording_time": 1284.1929144859314,
                    "event_game_time": 1285.959716796875
                },
                {
                    "type": "kill",
                    "victim": "Camille",
                    "recording_time": 1374.3760199546814,
                    "event_game_time": 1376.142822265625
                },
                {
                    "type": "kill",
                    "victim": "Nautilus",
                    "recording_time": 1379.4712347984314,
                    "event_game_time": 1381.238037109375
                },
                {
                    "type": "kill",
                    "victim": "Kindred",
                    "recording_time": 1385.086591243744,
                    "event_game_time": 1386.8533935546875
                },
                {
                    "type": "assist",
                    "victim": "Orianna",
                    "recording_time": 1396.502118587494,
                    "event_game_time": 1398.2689208984375
                },
                {
                    "type": "kill",
                    "victim": "Aphelios",
                    "recording_time": 1397.798261165619,
                    "event_game_time": 1399.5650634765625
                },
                {
                    "type": "kill",
                    "victim": "Camille",
                    "recording_time": 1453.306317806244,
                    "event_game_time": 1455.0731201171875
                },
                {
                    "type": "kill",
                    "victim": "Nautilus",
                    "recording_time": 1456.2041449546814,
                    "event_game_time": 1457.970947265625
                },
                {
                    "type": "assist",
                    "victim": "Orianna",
                    "recording_time": 1460.7581000328064,
                    "event_game_time": 1462.52490234375
                },
                {
                    "type": "inhibitor_kill",
                    "recording_time": 1486.105878353119,
                    "event_game_time": 1487.8726806640625
                },
                {
                    "type": "kill",
                    "victim": "Nautilus",
                    "recording_time": 1561.775800228119,
                    "event_game_time": 1563.5426025390625
                },
                {
                    "type": "kill",
                    "victim": "Camille",
                    "recording_time": 1588.0237250328064,
                    "event_game_time": 1589.79052734375
                },
                {
                    "type": "kill",
                    "victim": "Kindred",
                    "recording_time": 1649.0188422203064,
                    "event_game_time": 1650.78564453125
                },
                {
                    "type": "kill",
                    "victim": "Camille",
                    "recording_time": 1699.585858821869,
                    "event_game_time": 1701.3526611328125
                },
                {
                    "type": "death",
                    "killer": "JBS",
                    "recording_time": 1705.914472103119,
                    "event_game_time": 1707.6812744140625
                },
                {
                    "type": "assist",
                    "victim": "Kindred",
                    "recording_time": 1706.2436957359314,
                    "event_game_time": 1708.010498046875
                },
                {
                    "type": "assist",
                    "victim": "Nautilus",
                    "recording_time": 1706.280194759369,
                    "event_game_time": 1708.0469970703125
                },
                {
                    "type": "assist",
                    "victim": "Orianna",
                    "recording_time": 1717.9302191734314,
                    "event_game_time": 1719.697021484375
                },
                {
                    "type": "game_end",
                    "recording_time": 1731.6633734703064,
                    "event_game_time": 1733.43017578125
                }
            ],
            "match_id": 4872227736,
            "kills": 18,
            "dmg": 36537
        }

        player_champion = match_data['player_champion']
        skin_name = match_data['skin_name']

        thumbnail_manager.save_champion_splashart(player_champion, skin_name)
        thumbnail_manager.add_details_to_splashart(match_data)
