import os

import subprocess

from pywinauto import Application

OBS_EXE = 'C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe'
OBS_EXE_STRING = f'\"{OBS_EXE}\"'


def open():
    print('Opening Obs')
    obs_dir_path = '\"C:\\Program Files\\obs-studio\\bin\\64bit\"'
    start_recording_command = f'cd {obs_dir_path} & {OBS_EXE_STRING}'
    # start_recording_command = f'cd {obs_dir_path} & {obs_executable_path} --startrecording'
    print(start_recording_command)
    # os.system(start_recording_command)
    from subprocess import Popen, PIPE, STDOUT
    subprocess.Popen(start_recording_command, shell=True, stdout=subprocess.DEVNULL)


def close():
    close_command = f"TASKKILL /F /IM obs64.exe"
    print(close_command)
    subprocess.Popen(close_command, shell=True)
