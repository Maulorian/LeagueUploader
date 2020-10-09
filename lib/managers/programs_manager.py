import os
import subprocess

import psutil

from lib.utils import pretty_log, cd

DISCORD_EXE = 'Discord.exe'
CHROME_EXE = 'chrome.exe'
OBS_EXE = 'obs64.exe'

PROTON_VPN = 'ProtonVPN.exe'
PROTON_VPN_SERVICE = 'ProtonVPNService.exe'
PROTON_UPDATE_SERVICE = 'ProtonVPN.UpdateService.eXE'
OPEN_VPN = 'openvpn.exe'

DIRECTORIES = {
    CHROME_EXE: "C:\\Program Files (x86)\\Google\\Chrome\\Application",
    DISCORD_EXE: "C:\\Users\\Alex\\AppData\\Local\\Discord\\app-0.0.307",
    OBS_EXE: 'C:\\Program Files\\obs-studio\\bin\\64bit',
    PROTON_VPN: 'C:\Program Files (x86)\Proton Technologies\ProtonVPN'

}


def running(processName):
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

@pretty_log
def close_program(exe):
    if not running(exe):
        return False
    close_command = f'TASKKILL /F /IM \"{exe}\"'
    print(close_command)
    subprocess.Popen(close_command, shell=True)
    return True

@pretty_log
def open_program(exe):
    if running(exe):
        return
    directory = DIRECTORIES[exe]
    with cd(directory):
        FNULL = open(os.devnull, 'w')
        subprocess.Popen([exe], stdout=FNULL, stderr=subprocess.STDOUT)
