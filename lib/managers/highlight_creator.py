import multiprocessing

from moviepy.editor import *

from lib.constants import VIDEOS_PATH
from lib.utils import pretty_print

START_GAME = 20

INHIBITOR_KILL = 'inhibitor_kill'
BARON_KILL = 'baron_kill'
ASSIST = 'assist'
KILL = 'kill'
GAME_END = 'game_end'
DEATH = 'death'
TURRET_KILL = 'turret_kill'

MAX_EVENT_GAP = 30
MAX_NOT_SPED_UP_EVENT_GAP = 10
BEFORE_EVENT_TIME = 15
SPEED_UP_FACTOR = 2

SLOW_DOWN_FACTOR = 1/2

AFTER_EVENT_TIMES = {
    GAME_END: 0,
    KILL: 7.5,
    DEATH: 5,
    ASSIST: 7.5,
    INHIBITOR_KILL: 2,
    BARON_KILL: 5,
    TURRET_KILL: 5
}


def make_transition(accelerate, clip_data, next_clip_data):
    transition = {
        'start_time': clip_data.get('end_time'),
        'end_time': next_clip_data.get('start_time'),
        'accelerate': accelerate
    }

    return transition


def add_transitions(clips_data):
    final_clips_data = [clip_data for clip_data in clips_data]
    i = 0
    j = 0
    while i <= len(clips_data) - 2:
        clip_data = clips_data[i]
        next_clip_data = clips_data[i + 1]

        if gap_smaller_than(MAX_EVENT_GAP, clip_data, next_clip_data):
            accelerate = True
            if gap_smaller_than(MAX_NOT_SPED_UP_EVENT_GAP, clip_data, next_clip_data):
                accelerate = False

            transition = make_transition(accelerate, clip_data, next_clip_data)

            final_clips_data.insert(j + 1, transition)
            j += 1
        j += 1
        i += 1

    return final_clips_data


class HighlightCreator:
    def __init__(self, file_name, events):
        self.file_name = os.path.splitext(file_name)[0]
        self.video = VideoFileClip(VIDEOS_PATH + file_name)
        self.events = events

    def create_highlight(self):
        pretty_print(self.events)

        clips_data = self.get_clips_data()
        pretty_print(clips_data)

        gathered_clips_data = gather_clips_data(clips_data)
        pretty_print(gathered_clips_data)

        final_clips_data = add_transitions(gathered_clips_data)
        pretty_print(final_clips_data)

        clips = self.create_clips(final_clips_data)

        highlight = concatenate_videoclips(clips)
        # clips = [clip.crossfadein(1) for i, clip in enumerate(clips) if i > 0]
        # highlight = concatenate_videoclips(clips, padding=-1, method="compose")
        highlight_file_name = f"{self.file_name}_highlight.mp4"
        highlight.write_videofile(VIDEOS_PATH + highlight_file_name, threads=multiprocessing.cpu_count())
        self.video.close()
        return highlight_file_name

    def get_clips_data(self):

        clips_data = []

        for event in self.events:
            event_type = event.get('type')
            after_event_time = AFTER_EVENT_TIMES.get(event_type)
            clip_data = {
                'start_time': event.get('time') - BEFORE_EVENT_TIME,
                'end_time': event.get('time') + after_event_time
            }
            clips_data.append(clip_data)
        clips_data.sort(key=lambda clip: clip.get('start_time'))
        return clips_data

    def create_clip(self, clip_data):
        start_time = clip_data.get('start_time')
        end_time = clip_data.get('end_time')
        clip = self.video.subclip(start_time, end_time)

        if clip_data.get('accelerate'):
            # sped_up_clip = clip.fl_time(lambda t: SPEED_UP_FACTOR * t)
            sped_up_clip = clip.fl_time(lambda t: SPEED_UP_FACTOR * t, apply_to=['audio'])
            new_duration = clip.duration / SPEED_UP_FACTOR
            sped_up_clip = sped_up_clip.set_duration(new_duration)
            clip = sped_up_clip

        return clip

    def create_linking_clip(self, clip_data, next_clip_data, speed_up):
        link_start = clip_data.get('end_time')
        link_end = next_clip_data.get('start_time')
        linking_clip = self.video.subclip(link_start, link_end)
        if speed_up:
            sped_up_linking_clip = linking_clip.fl_time(lambda t: SPEED_UP_FACTOR * t)
            new_duration = linking_clip.duration / SPEED_UP_FACTOR
            sped_up_linking_clip = sped_up_linking_clip.set_duration(new_duration)
            linking_clip = sped_up_linking_clip
        return linking_clip

    def create_clips(self, gathered_clips_data):
        clips = []
        for gathered_clip_data in gathered_clips_data:
            sub_clips = self.create_clip(gathered_clip_data)
            clips.append(sub_clips)
        return clips


def gap_smaller_than(gap, clip_data, next_clip_data):
    return abs(clip_data.get('end_time') - next_clip_data.get('start_time')) <= gap


def gather_clips_data(clips_data):
    gathered_clips_data = []
    while len(clips_data) > 0:
        clip_data = clips_data.pop(0)
        while True:
            try:
                next_clip_data = clips_data[0]
            except IndexError:
                break

            if clip_data['end_time'] >= next_clip_data.get('start_time'):
                clip_data['end_time'] = next_clip_data.get('end_time')
                clips_data.pop(0)
            else:
                break
        gathered_clips_data.append(clip_data)
    return gathered_clips_data
