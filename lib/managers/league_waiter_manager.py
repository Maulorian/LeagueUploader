import subprocess
import time

import requests

from lib.managers.league_manager import bugsplat
from lib.managers.replay_api_manager import get_current_game_time, game_finished, game_launched, game_time_when_started, \
    game_paused
from lib.utils import wait_seconds, pretty_print

WAIT_TIME = 2


def wait_finish(recording_times, game_time_when_started_recording, recording_start_time):
    print("[SPECTATOR] - Waiting for game to finish..")
    previous_game_time = game_time_when_started_recording
    # total_delay = game_time_when_started_recording

    game_crash_retries = 10
    while True:
        current_game_time = get_current_game_time()

        if current_game_time == previous_game_time:
            game_crash_retries -= 1
            print(f'{game_crash_retries=}')

            if game_crash_retries == 0:
                raise GameCrashedException
        previous_game_time = current_game_time

        current_time = time.time()
        current_time_passed_recording = current_time - recording_start_time
        print(f'{current_game_time=}')
        print(f'{current_time_passed_recording=}')

        # delay = current_time_passed_recording - current_game_time
        # delta_delay = delay - game_time_when_started_recording
        # game_time_when_started_recording = delay

        # total_delay += delta_delay
        # recording_times[current_game_time] = total_delay
        recording_times[current_time_passed_recording] = current_game_time
        pretty_print(recording_times)

        if bugsplat():
            raise GameCrashedException
        finished = game_finished()
        if finished:
            print("[SPECTATOR] - Game Finished")
            break


class LaunchCrashedException(Exception):
    pass


class GameCrashedException(Exception):
    pass


def wait_for_game_launched():
    print("[SPECTATOR] - Waiting for game to launch..")

    start = time.time()
    while True:
        time_passed = time.time() - start
        if time_passed > 30:
            raise LaunchCrashedException
        try:
            if game_launched():
                print("[SPECTATOR] - Game has launched")
                break
            if bugsplat():
                raise GameCrashedException

        except (requests.exceptions.ConnectionError, subprocess.CalledProcessError):
            # print("[SPECTATOR] - Game not yet launched")
            pass


def wait_for_game_start():
    print("[SPECTATOR] - Waiting for game to start..")

    start = time.time()
    while True:
        time_passed = time.time() - start
        print(time_passed)
        if time_passed > 30:
            raise LaunchCrashedException
        game_time = game_time_when_started()
        if game_time:
            print(f"[SPECTATOR] - Game has started at {game_time}")
            return game_time
        if bugsplat():
            raise GameCrashedException

# def wait_for_game_start():
#     print("[SPECTATOR] - Waiting for game to start..")
#
#     start = time.time()
#     start_game_time = get_current_game_time()
#
#     while True:
#         current_game_time = get_current_game_time()
#         if current_game_time > start_game_time:
#             break
#
#         time_passed = time.time() - start
#         if time_passed > 30:
#             raise LaunchCrashedException
#
#         if bugsplat():
#             raise GameCrashedException
#     print(f"[SPECTATOR] - Game has started")
