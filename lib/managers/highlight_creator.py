from datetime import timedelta, datetime

from moviepy.editor import *

from lib.managers.upload_manager import VIDEOS_PATH
from lib.utils import pretty_print

MULTI_KILL_TIME = 10


def get_clips(events):
    clips = []
    for event in events:
        clip = {}
        seconds = event.get('seconds')
        start = timedelta(seconds=seconds)
        clip['start'] = start
        clips.append(clip)
    clips.sort(key=lambda clip: clip.get('start'))
    pretty_print(clips)


def create_highlight(events):
    clips = get_clips(events)
    video = VideoFileClip(VIDEOS_PATH + "hl.mkv")
    clip = video.subclip(0,60)
    clip = clip.fx(vfx.speedx, 0.5)
    import multiprocessing

    threads = multiprocessing.cpu_count()
    print(f'{threads=}')
    clip.write_videofile(VIDEOS_PATH + "result.mp4", threads=threads)
    # clip.write_videofile(VIDEOS_PATH + "result.mp4", bitrate="12000k", threads=threads)
