import subprocess

import psutil

from lib.utils import pretty_log

DISCORD_EXE = 'Discord.exe'


def running(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

@pretty_log
def close_program(exe):
    if not running(exe):
        return
    close_command = f'TASKKILL /F /IM \"{exe}\"'
    print(close_command)
    subprocess.Popen(close_command, shell=True)