import json
import ntpath
import os
import sys
import traceback
import unittest
import cassiopeia as cass
from dotenv import load_dotenv

from lib.managers import thumbnail_manager
from lib.managers.replay_api_manager import get_formated_timestamp
from lib.managers.upload_manager import VIDEOS_PATH, upload_default_video, update_video, TO_UPLOAD_PATH, delete_video, \
    upload_video, VideoUploadException
from lib.spectator import get_video_path

TEST_VIDEO_MKV = 'test_video.mkv'

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_KEY"))


# pp = pprint.PrettyPrinter(indent=2)


class TestUpload(unittest.TestCase):
    def test_get_video_path(self):
        path = get_video_path()
        print(path)

    def test_save_splash_art(self):
        print(os.getcwd())
        to_upload_json = open(TO_UPLOAD_PATH, "r")
        to_upload = json.load(to_upload_json)
        if len(to_upload) == 0:
            to_upload_json.close()
            return
        metadata = next(data for data in to_upload if data.get('skin_name') == 'Divine Sword Irelia')
        to_upload_json.close()

        player_champion = metadata['player_champion']
        skin_name = metadata['skin_name']

        thumbnail_manager.save_champion_splashart(player_champion, skin_name)
        thumbnail_manager.add_details_to_splashart(metadata)

    def test_upload_video(self):
        to_upload_json = open(TO_UPLOAD_PATH, "r")
        to_upload = json.load(to_upload_json)
        if len(to_upload) == 0:
            to_upload_json.close()
            return
        video_metadata = to_upload.pop(0)
        video_metadata['file_name'] = TEST_VIDEO_MKV
        to_upload_json.close()
        path = VIDEOS_PATH + video_metadata['file_name']
        if not os.path.exists(path):
            raise FileNotFoundError
        video_id = upload_default_video(video_metadata)
        update_video(video_id, video_metadata)

    def test_empty_queue(self):
        to_upload_json = open(TO_UPLOAD_PATH, "r")
        to_upload = json.load(to_upload_json)
        to_upload_json.close()
        while True:

            try:
                match_data = to_upload.pop(0)
            except IndexError:
                break


            path = VIDEOS_PATH + match_data['path']
            if not os.path.exists(path):
                print(f"{match_data['title']} - {path} File not found")
                continue

            try:
                player_champion = match_data['player_champion']
                skin_name = match_data['skin_name']

                thumbnail_manager.save_champion_splashart(player_champion, skin_name)
                thumbnail_manager.add_details_to_splashart(match_data)
            except Exception as e:
                traceback.print_exc()
                break
