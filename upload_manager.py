import json
import os

from googleapiclient.discovery import build
from oauth2client import client  # Added
from oauth2client import tools  # Added
from oauth2client.client import Storage
from oauth2client.file import Storage  # Added
from youtube_uploader_selenium import YouTubeUploader
import re

VIDEOS_PATH = 'D:\\LeagueReplays\\'
METADATA_PATH = 'metadata.json'
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

PRIVACY = "private"
BASE_TAGS = ["lol challenger matchups", "league challenger matchups", "lol challenger replays", "league challenger replays"]


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def rename_video_path(video_path, title):
    parts = os.path.splitext(video_path)
    extension = parts[1]
    reformated_title = camel_to_snake(title.replace(' ', ''))
    return reformated_title + extension


def add_video_to_queue(metadata):
    print(f'[UPLOAD MANAGER] - Adding Video To Queue')

    with open('to_upload.json', 'r') as to_upload_json:
        to_upload = json.load(to_upload_json)
        from pathlib import Path

        video_paths = sorted(Path(VIDEOS_PATH).iterdir(), key=os.path.getmtime)

        video_path = video_paths[-1]

        metadata['path'] = str(video_path)
        to_upload.append(metadata)
    with open('to_upload.json', 'w') as to_upload_json:
        json.dump(to_upload, to_upload_json, indent=2)

    with open('to_upload_backup.json', 'r') as to_upload_json:
        to_upload = json.load(to_upload_json)
        from pathlib import Path

        video_paths = sorted(Path(VIDEOS_PATH).iterdir(), key=os.path.getmtime)

        video_path = video_paths[-1]

        metadata['path'] = str(video_path)
        to_upload.append(metadata)
    with open('to_upload_backup.json', 'w') as to_upload_json:
        json.dump(to_upload, to_upload_json, indent=2)


def upload_video(video_metadata):
    video_id = upload_default_video(video_metadata['path'])
    update_video(video_id, video_metadata)


def empty_queue():
    print('Emptying queue')
    while True:
        with open('to_upload.json', 'r') as to_upload_json:
            to_upload = json.load(to_upload_json)
            if len(to_upload) == 0:
                break

            video_metadata = to_upload.pop(0)

        with open('to_upload.json', 'w') as to_upload_json:
            json.dump(to_upload, to_upload_json, indent=2)

        upload_video(video_metadata)


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
    print('[UPLOAD MANAGER] - Updating Video')
    title = metadata['title']
    print(f'[UPLOAD MANAGER] - Setting title to "{title}"')
    description = metadata['description']
    tags = metadata['tags']

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = get_authenticated_service()

    request = youtube.videos().update(
        part="snippet,status",
        body={
            "id": video_id,
            "snippet": {
                "defaultLanguage": "en",
                "description": description,
                "tags": tags + BASE_TAGS,
                "title": title,
                "categoryId": "20"
            },
            "status": {
                "privacyStatus": PRIVACY
            }
        }
    )
    request.execute()
    request = youtube.videos().rate(
        id=video_id,
        rating="like"
    )
    request.execute()
    print('[UPLOAD MANAGER] - Video Updated')


def get_authenticated_service():  # Modified
    credential_path = os.path.join('/', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)
    return build(api_service_name, api_version, credentials=credentials, cache_discovery=False)
