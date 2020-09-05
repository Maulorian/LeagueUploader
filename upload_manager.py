import json
import os

from googleapiclient.discovery import build
from oauth2client import client  # Added
from oauth2client import tools  # Added
from oauth2client.client import Storage
from oauth2client.file import Storage  # Added
from youtube_uploader_selenium import YouTubeUploader

VIDEOS_PATH = 'D:\\LeagueReplays\\'
METADATA_PATH = 'metadata.json'
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

PRIVACY = "private"
BASE_TAGS = ["league of legends", "lol", "replays", "matchups", "challenger"]


def add_completed_tag(video_path):
    parts = os.path.splitext(video_path)
    name = parts[0]
    extension = parts[1]
    return name + '_completed' + extension


def add_video_to_queue(metadata):
    with open('to_upload.json', 'r') as to_upload_json:
        to_upload = json.load(to_upload_json)
        videos = os.listdir(VIDEOS_PATH)
        videos.reverse()
        video_name = videos[0]
        video_path = f'{VIDEOS_PATH}{video_name}'

        new_video_path = add_completed_tag(video_path)
        os.rename(video_path, new_video_path)

        metadata['path'] = new_video_path
        to_upload.append(metadata)
    with open('to_upload.json', 'w') as to_upload_json:
        json.dump(to_upload, to_upload_json, indent=2)


def upload_video(video_metadata):
    video_id = upload_default_video(video_metadata['path'])
    update_video(video_id, video_metadata)


def empty_queue():
    uploaded = []
    with open('to_upload.json', 'r') as to_upload_json:
        to_upload = json.load(to_upload_json)
        for video_metadata in to_upload:
            upload_video(video_metadata)
            uploaded.append(video_metadata['path'])

        to_upload[:] = [metadata for metadata in to_upload if metadata.get('path') not in uploaded]

    with open('to_upload.json', 'w') as to_upload_json:
        json.dump(to_upload, to_upload_json, indent=2)


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
                "tags": BASE_TAGS + tags,
                "title": title,
                "categoryId": "20"
            },
            "status": {
                "privacyStatus": PRIVACY,
                "madeForKids": True
            }
        }
    )
    request.execute()
    print('[UPLOAD MANAGER] - Video Updated')


def get_authenticated_service():  # Modified
    credential_path = os.path.join('./', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)
    return build(api_service_name, api_version, credentials=credentials, cache_discovery=False)
