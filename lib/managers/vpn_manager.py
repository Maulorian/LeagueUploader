import time

from lib.managers import programs_manager
from lib.utils import get_public_ip_address


def connect():
    ip = get_public_ip_address()
    programs_manager.open_program(programs_manager.PROTON_VPN)
    while True:
        new_ip = get_public_ip_address()
        if new_ip != ip:
            break
        time.sleep(5)


def disconnect():
    ip = get_public_ip_address()
    closed = programs_manager.close_program(programs_manager.PROTON_VPN)
    programs_manager.close_program(programs_manager.PROTON_VPN_SERVICE)
    programs_manager.close_program(programs_manager.PROTON_UPDATE_SERVICE)
    programs_manager.close_program(programs_manager.OPEN_VPN)
    if not closed:
        return
    while True:
        new_ip = get_public_ip_address()
        if new_ip != ip:
            break
        print(f'Ip address is still {ip}')
        time.sleep(5)
