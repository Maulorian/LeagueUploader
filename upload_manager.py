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


def upload_video():
    print('[UPLOAD MANAGER] - Upload Video')

    videos = os.listdir(VIDEOS_PATH)
    videos.reverse()
    video_name = videos[0]
    video_path = f'{VIDEOS_PATH}{video_name}'
    print(f'Uploading: video_path={video_name}, size={os.path.getsize(video_path)}kb')
    metadata = {
        'title': "title",
        'description': ""
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
    print(credentials is not None)
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)
    return build(api_service_name, api_version, credentials=credentials, cache_discovery=False)
