import os
from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

VIDEOS_PATH = 'C:/Users/Alex/Documents/LeagueVideos/'
# API_URL = 'https://script.google.com/macros/s/AKfycbw9n8NM_qDmyuVyZZxt0w7Ih-W3DTxLDuxTaOl-VW5XPHqnEqPj/exec'
BASE_TAGS = ["league of legends", "lol"]


def upload_video(title, description):
    videos = os.listdir(VIDEOS_PATH)
    videos.reverse()
    video_name = videos[0]
    video_path = f'{VIDEOS_PATH}\\{video_name}'
    print(f'Uploading: video_path={video_name}, size={os.path.getsize(video_path) / 1000000}mb')

    # loggin into the channel
    channel = Channel()
    channel.login("client_secret.json", "credentials.storage")

    # setting up the video that is going to be uploaded
    video = LocalVideo(file_path=video_path)

    # setting snippet
    video.set_title(title)
    video.set_description(description)
    video.set_tags(BASE_TAGS + ["irelia"])
    video.set_category("gaming")
    video.set_default_language("en-US")
    video.set_privacy_status("public")

    # setting thumbnail
    # video.set_thumbnail_path('test_thumb.png')

    # uploading video and printing the results
    video = channel.upload_video(video)
    print(video.id)
    print(video)

    # liking video
    video.like()
