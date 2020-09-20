import json
import logging
import os
import re
import traceback

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client import client  # Added
from oauth2client import tools  # Added
from oauth2client.client import Storage
from oauth2client.file import Storage  # Added
from youtube_uploader_selenium import YouTubeUploader

from lib.builders import description_builder, tags_builder
from lib.builders.title_builder import get_title
from lib.managers.thumbnail_manager import save_champion_splashart, get_flag_image, add_details_to_splashart

VIDEOS_PATH = 'D:\\LeagueReplays\\'
METADATA_PATH = '../json/metadata.json'
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "../json/client_secret.json"
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

PRIVACY_STATUS = "private"

TO_UPLOAD_PATH = '..\\json\\to_upload.json'
TO_UPLOAD_BACKUP_PATH = '..\\json\\to_upload_backup.json'


# def camel_to_snake(name):
#     name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
#     return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


# def rename_video_path(video_path, title):
#     parts = os.path.splitext(video_path)
#     extension = parts[1]
#     reformated_title = camel_to_snake(title.replace(' ', ''))
#     return reformated_title + extension


def add_video_to_queue(metadata):
    print(f'[UPLOAD MANAGER] - Adding Video To Queue')

    to_upload_json = open(TO_UPLOAD_PATH, "r")
    to_upload = json.load(to_upload_json)
    to_upload.append(metadata)
    to_upload_json.close()

    to_upload_json = open(TO_UPLOAD_PATH, "w")
    json.dump(to_upload, to_upload_json, indent=2)
    to_upload_json.close()

    to_upload_json = open(TO_UPLOAD_BACKUP_PATH, "r")
    to_upload = json.load(to_upload_json)
    to_upload.append(metadata)
    to_upload_json.close()

    to_upload_json = open(TO_UPLOAD_BACKUP_PATH, "w")
    json.dump(to_upload, to_upload_json, indent=2)
    to_upload_json.close()


def upload_video(video_metadata):
    path = video_metadata['path']
    video_id = upload_default_video(video_metadata['path'])
    try:
        update_video(video_id, video_metadata)
        os.remove(path)
        print(f"{path} Removed!")
    except Exception:
        traceback.print_exc()
        delete_video(video_id)
        raise VideoUploadException


def delete_video(video_id):
    print(f'[UPLOAD MANAGER] - Deleting video {video_id}')
    youtube = get_authenticated_service()
    request = youtube.videos().delete(
        id=video_id
    )
    request.execute()


class VideoUploadException(Exception):
    pass

def empty_queue():
    print('Emptying queue')
    while True:
        to_upload_json = open(TO_UPLOAD_PATH, "r")
        to_upload = json.load(to_upload_json)
        if len(to_upload) == 0:
            print('uploads are empty')
            to_upload_json.close()
            break
        video_metadata = to_upload.pop(0)
        to_upload_json.close()
        try:
            upload_video(video_metadata)
        except VideoUploadException:
            break

        to_upload_json = open(TO_UPLOAD_PATH, "w")
        json.dump(to_upload, to_upload_json, indent=2)
        to_upload_json.close()


def upload_default_video(video_path):
    print(f'[UPLOAD MANAGER] - Upload video_path={video_path}, size={os.path.getsize(video_path)}kb')

    metadata = {
        'title': "title",
        'description': "description"
    }
    with open(METADATA_PATH, 'w') as file:
        file.write(json.dumps(metadata))

    uploader = YouTubeUploader(video_path, METADATA_PATH)
    was_video_uploaded, video_id = uploader.upload()
    print('[UPLOAD MANAGER] - Video Uploaded')

    return video_id


def update_video(video_id, metadata):
    print(f'[UPLOAD MANAGER] - Updating Video {video_id}')
    player_champion = metadata['player_champion']
    skin_name = metadata['skin_name']
    description = metadata['description']
    tags = metadata['tags']
    title = metadata['title']
    region = metadata['region']
    print(f'[UPLOAD MANAGER] - Setting title to "{title}"')

    save_champion_splashart(player_champion, skin_name)
    add_details_to_splashart(metadata)
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = get_authenticated_service()

    request = youtube.videos().update(
        part="snippet,status",
        body={
            "id": video_id,
            "snippet": {
                "defaultLanguage": "en",
                "description": description,
                "tags": tags,
                "title": title,
                "categoryId": "20",

            },
            "status": {
                "privacyStatus": PRIVACY_STATUS
            }
        }
    )
    print('[UPLOAD MANAGER] - Updating Metadata')

    request.execute()

    # youtube = get_authenticated_service()
    like_update = youtube.videos().rate(
        id=video_id,
        rating="like"
    )
    print('[UPLOAD MANAGER] - Liking Video')

    like_update.execute()

    # youtube = get_authenticated_service()
    thumbnail_update = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload('splash_art.jpeg')
    )
    print('[UPLOAD MANAGER] - Setting Thumbnail')

    thumbnail_update.execute()
    print('[UPLOAD MANAGER] - Video Updated')



def get_authenticated_service():  # Modified
    credential_path = 'credential_sample.json'
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)
    return build(api_service_name, api_version, credentials=credentials, cache_discovery=False)
