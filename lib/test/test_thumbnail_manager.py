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
from lib.managers.upload_manager import VIDEOS_PATH, upload_default_video, update_video, TO_UPLOAD_PATH
from lib.spectator import get_video_path

sys.path.append('C:\\Users\\Alex\\PycharmProjects\\LeagueUploader')
load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)


class TestThumbnail(unittest.TestCase):
    def test_get_summoner_spell(self):
        summoner_name = ''
        image = get_summoner_spell(summoner_name)