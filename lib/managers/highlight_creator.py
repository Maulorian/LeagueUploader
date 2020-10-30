import multiprocessing

from moviepy.editor import *

from lib.constants import VIDEOS_PATH, HIGHLIGHTS_PATH
from lib.managers.videos_to_upload_manager import get_match_data_to_upload, remove_match_data, add_match_data
from lib.utils import pretty_print

START_GAME = 20

INHIBITOR_KILL = 'inhibitor_kill'
BARON_KILL = 'baron_kill'
ASSIST = 'assist'
KILL = 'kill'
GAME_END = 'game_end'
GAME_START = 'game_start'
DEATH = 'death'
TURRET_KILL = 'turret_kill'

MAX_END_TO_START_TIME = 15
MAX_NOT_SPED_UP_EVENT_GAP = 10
SPEED_UP_FACTOR = 2

SLOW_DOWN_FACTOR = 1 / 2

BEFORE_EVENT_TIMES = {
    GAME_END: 2.5,
    GAME_START: 0,
    KILL: 20,
    DEATH: 10,
    ASSIST: 7.5,
    INHIBITOR_KILL: 5,
    BARON_KILL: 5,
    TURRET_KILL: 5
}

AFTER_EVENT_TIMES = {
    GAME_END: 0,
    GAME_START: 7.5,
    KILL: 7.5,
    DEATH: 1,
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

        if gap_smaller_than(MAX_END_TO_START_TIME, clip_data, next_clip_data):
            accelerate = True
            if gap_smaller_than(MAX_NOT_SPED_UP_EVENT_GAP, clip_data, next_clip_data):
                accelerate = False

            transition = make_transition(accelerate, clip_data, next_clip_data)

            final_clips_data.insert(j + 1, transition)
            j += 1
        j += 1
        i += 1

    return final_clips_data


def get_file_name_without_extension(file_name):
    return os.path.splitext(file_name)[0]


def get_highlight_file_name(file_name):
    return f"{get_file_name_without_extension(file_name)}_highlight.mp4"


class HighlightCreator:
    def __init__(self, file_name, events):
        self.file_name = get_file_name_without_extension(file_name)
        self.highlight_file_name = get_highlight_file_name(file_name)
        self.video = VideoFileClip(VIDEOS_PATH + file_name)
        self.events = events

    def close_video(self):
        self.video.close()

    def create_highlight(self):
        # pretty_print(self.events)

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
        highlight.write_videofile(HIGHLIGHTS_PATH + self.highlight_file_name, threads=multiprocessing.cpu_count())
        self.close_video()

    def get_clips_data(self):

        clips_data = []

        for event in self.events:
            event_type = event.get('type')
            before_event_time = BEFORE_EVENT_TIMES.get(event_type)
            after_event_time = AFTER_EVENT_TIMES.get(event_type)
            clip_data = {
                'start_time': max(0, event.get('recording_time') - before_event_time),
                'end_time': min(event.get('recording_time') + after_event_time, self.video.duration)
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


def next_clip_inside_clip(clip_data, next_clip_data):
    clip_data_start_time = clip_data['start_time']
    clip_data_end_time = clip_data['end_time']
    next_clip_data_start_time = next_clip_data['start_time']
    next_clip_data_end_time = next_clip_data['end_time']
    return clip_data_end_time >= next_clip_data_end_time and clip_data_start_time <= next_clip_data_start_time


def gather_clips_data(clips_data):
    gathered_clips_data = []
    while len(clips_data) > 0:
        clip_data = clips_data.pop(0)
        while True:
            try:
                next_clip_data = clips_data[0]
            except IndexError:
                break
            if next_clip_inside_clip(clip_data, next_clip_data):
                print(f'{next_clip_data} inside {clip_data}')
                clips_data.pop(0)
                continue
            if end_is_further_than_start(clip_data['end_time'], next_clip_data.get('start_time')):
                print('end is further than start')

                clip_data['end_time'] = next_clip_data.get('end_time')
                clips_data.pop(0)
            else:
                break
        gathered_clips_data.append(clip_data)
    return gathered_clips_data


def end_is_further_than_start(clip_data_end_time, next_clip_data_start_time):
    return clip_data_end_time >= next_clip_data_start_time


def create_highlights():
    print('Creating highlights')
    to_upload = get_match_data_to_upload()
    for match_data in to_upload:
        file_name = match_data['file_name']
        events = match_data['events']
        match_id = match_data['match_id']
        path = VIDEOS_PATH + file_name
        highlight_file_name = get_highlight_file_name(file_name)


        print(f'Creating {highlight_file_name}')

        if 'highlight_file_name' in match_data:
            print(f'{match_id} already has an highlight')
            continue

        if not os.path.exists(path):
            remove_match_data(match_id)
            continue
        hl_creator = HighlightCreator(file_name, events)
        hl_creator.create_highlight()

        os.remove(path)

        remove_match_data(match_id)
        match_data['highlight_file_name'] = highlight_file_name
        add_match_data(match_data)
