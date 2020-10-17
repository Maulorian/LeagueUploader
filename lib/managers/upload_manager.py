import json
import logging
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client import client  # Added
from oauth2client import tools  # Added
from oauth2client.client import Storage
from oauth2client.file import Storage  # Added
from youtube_uploader_selenium import YouTubeUploader

from lib.constants import PROJECT_PATH, VIDEOS_PATH
from lib.managers.highlight_creator import HighlightCreator
from lib.managers.videos_to_upload_manager import get_videos_to_upload, remove_to_upload

LOG_NAME = "upload_logger"

import lib.managers.thumbnail_manager as thumbnail_manager

match_data_PATH = PROJECT_PATH + 'json/match_data.json'
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = PROJECT_PATH + "json/client_secret.json"
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

PRIVACY_STATUS = "public"
TO_UPLOAD_PATH = PROJECT_PATH + 'json\\to_upload.json'
TO_UPLOAD_BACKUP_PATH = PROJECT_PATH + 'json\\to_upload_backup.json'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def add_video_to_queue(match_data):
    print(f'[UPLOAD MANAGER] - Adding Video To Queue')

    to_upload_json = open(TO_UPLOAD_PATH, "r")
    to_upload = json.load(to_upload_json)
    to_upload.append(match_data)
    to_upload_json.close()

    to_upload_json = open(TO_UPLOAD_PATH, "w")
    json.dump(to_upload, to_upload_json, indent=2)
    to_upload_json.close()

    to_upload_json = open(TO_UPLOAD_BACKUP_PATH, "r")
    to_upload = json.load(to_upload_json)
    to_upload.append(match_data)
    to_upload_json.close()

    to_upload_json = open(TO_UPLOAD_BACKUP_PATH, "w")
    json.dump(to_upload, to_upload_json, indent=2)
    to_upload_json.close()


def upload_video(video_match_data):
    # path = VIDEOS_PATH + video_match_data['path']
    video_id = None
    retries = 3
    while True:
        try:
            video_id = upload_video_file(video_match_data)
            break
        except Exception:
            if retries == 0:
                raise Exception
            retries -= 1
            continue
    while True:
        try:
            update_video(video_id, video_match_data)
            break
        except Exception:
            if retries == 0:
                raise Exception
            retries -= 1
            continue


def delete_video(video_id):
    logger.info(f'[UPLOAD MANAGER] - Deleting video {video_id}')
    youtube = get_authenticated_service()
    request = youtube.videos().delete(
        id=video_id
    )
    request.execute()


class VideoUploadException(Exception):
    pass


def handle_match(match_data):
    file_name = match_data['file_name']
    path = VIDEOS_PATH + file_name
    if not os.path.exists(path):
        logger.info(f"{match_data['title']} - {path} File not found")
        match_id = match_data.get('match_id')
        remove_to_upload(match_id)
        return

    logger.info(f"{match_data['title']}")

    events = match_data['events']
    hl_creator = HighlightCreator(file_name, events)
    highlight_file_name = hl_creator.create_highlight()
    match_data['file_name'] = highlight_file_name
    upload_video(match_data)

    highlight_path = VIDEOS_PATH + highlight_file_name
    os.remove(path)
    os.remove(highlight_path)
    logger.info(f"{path} Removed!")
    match_id = match_data.get('match_id')
    remove_to_upload(match_id)


def empty_queue():
    logger.info('Emptying queue')

    while True:
        to_upload = get_videos_to_upload()
        try:
            match_data = to_upload[0]
        except IndexError:
            logger.info('uploads are empty')
            break
        handle_match(match_data)


def upload_video_file(match_data):
    logger.info(f'Updating Video')

    title = match_data['title']
    description = match_data['description']

    path = VIDEOS_PATH + match_data['file_name']

    logger.info(f'[UPLOAD MANAGER] - Uploading {title}')

    match_data = {
        'title': title,
        'description': description
    }
    with open(match_data_PATH, 'w') as file:
        file.write(json.dumps(match_data))

    uploader = YouTubeUploader(path, match_data_PATH)
    was_video_uploaded, video_id = uploader.upload()
    logger.info('[UPLOAD MANAGER] - Video Uploaded')

    return video_id


def update_video(video_id, match_data):
    logger.info(f'Updating Video')
    logger.info(f'[UPLOAD MANAGER] - Updating Video {video_id}')
    player_champion = match_data['player_champion']
    skin_name = match_data['skin_name']
    description = match_data['description']
    tags = match_data['tags']
    title = match_data['title']
    logger.info(f'[UPLOAD MANAGER] - Setting title to "{title}"')

    thumbnail_manager.save_champion_splashart(player_champion, skin_name)
    thumbnail_manager.add_details_to_splashart(match_data)

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = get_authenticated_service()

    request = youtube.videos().update(
        part="snippet,status",
        body={
            "id": video_id,
            "snippet": {
                "defaultLanguage": "en",
                "tags": tags,
                "categoryId": "20",
                "title": title,
                'description': description
            },
            "status": {
                "privacyStatus": PRIVACY_STATUS
            }
        }
    )
    logger.info('[UPLOAD MANAGER] - Updating match_data')

    request.execute()

    # youtube = get_authenticated_service()
    like_update = youtube.videos().rate(
        id=video_id,
        rating="like"
    )
    logger.info('[UPLOAD MANAGER] - Liking Video')

    like_update.execute()

    # youtube = get_authenticated_service()
    thumbnail_update = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload('splash_art.jpeg')
    )
    logger.info('[UPLOAD MANAGER] - Setting Thumbnail')

    thumbnail_update.execute()
    logger.info('[UPLOAD MANAGER] - Video Updated')


def get_authenticated_service():  # Modified
    credential_path = 'credential_sample.json'
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)
    return build(api_service_name, api_version, credentials=credentials, cache_discovery=False)
