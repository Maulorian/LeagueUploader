import subprocess

from lib.utils import pretty_log

OBS_EXE = 'C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe'
OBS_EXE_STRING = f'\"{OBS_EXE}\"'


def start():
    print(f'[OBS] - Starting')
    obs_dir_path = '\"C:\\Program Files\\obs-studio\\bin\\64bit\"'
    start_recording_command = f'cd {obs_dir_path} & {OBS_EXE_STRING}'
    # start_recording_command = f'cd {obs_dir_path} & {obs_executable_path} --startrecording'
    # print(start_recording_command)
    subprocess.Popen(start_recording_command, shell=True, stdout=subprocess.DEVNULL)

@pretty_log
def close_obs():
    close_command = f"TASKKILL /F /IM obs64.exe"
    # print(f'[OBS] - Closing')
    # print(close_command)
    subprocess.Popen(close_command, shell=True)
