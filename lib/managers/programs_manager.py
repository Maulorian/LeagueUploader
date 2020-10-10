import os
import subprocess

import psutil

DISCORD_EXE = 'Discord.exe'
CHROME_EXE = 'chrome.exe'
OBS_EXE = 'obs64.exe'

PROTON_VPN = 'ProtonVPN.exe'
PROTON_VPN_SERVICE = 'ProtonVPNService.exe'
PROTON_UPDATE_SERVICE = 'ProtonVPN.UpdateService.exe'
OPEN_VPN = 'openvpn.exe'

DIRECTORIES = {
    CHROME_EXE: "C:\\Program Files (x86)\\Google\\Chrome\\Application",
    DISCORD_EXE: "C:\\Users\\Alex\\AppData\\Local\\Discord\\app-0.0.307",
    OBS_EXE: 'C:\\Program Files\\obs-studio\\bin\\64bit',
    PROTON_VPN: 'C:\Program Files (x86)\Proton Technologies\ProtonVPN'

}


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def running(processName):
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def close_program(exe):
    if not running(exe):
        return False
    close_command = f'TASKKILL /F /IM \"{exe}\"'
    subprocess.Popen(close_command, shell=True)
    return True


def open_program(exe):
    if running(exe):
        return False
    directory = DIRECTORIES[exe]
    with cd(directory):
        subprocess.Popen([exe], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
        print(f'Successfully opened {exe}')

    return True
