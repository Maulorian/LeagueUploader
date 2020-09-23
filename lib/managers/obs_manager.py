import subprocess

from lib.utils import pretty_log

OBS_EXE = 'obs64.exe'
OBS_PATH = 'C:\\Program Files\\obs-studio\\bin\\64bit'


def start():
    print(f'[OBS] - Starting')
    start_recording_command = f'cd "{OBS_PATH}" & {OBS_EXE}'
    print(start_recording_command)
    subprocess.Popen(start_recording_command, shell=True, stdout=subprocess.DEVNULL)


