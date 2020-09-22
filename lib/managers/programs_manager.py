import subprocess

from lib.utils import pretty_log

DISCORD_EXE = 'Discord.exe'


@pretty_log
def close_discord():
    close_command = f'TASKKILL /F /IM \"{DISCORD_EXE}\"'
    subprocess.Popen(close_command, shell=True)
