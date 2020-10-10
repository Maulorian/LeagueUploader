import time

from lib.managers import programs_manager
from lib.utils import get_public_ip_address


def connect():
    ip = get_public_ip_address()
    while True:
        success = programs_manager.open_program(programs_manager.PROTON_VPN)
        start = time.time()
        if not success:
            return
        while True:
            delta = time.time() - start
            print(delta)
            if delta > 20:
                programs_manager.close_program(programs_manager.PROTON_VPN)
                programs_manager.close_program(programs_manager.PROTON_VPN_SERVICE)
                programs_manager.close_program(programs_manager.PROTON_UPDATE_SERVICE)
                programs_manager.close_program(programs_manager.OPEN_VPN)
                time.sleep(1)

                break
            new_ip = get_public_ip_address()
            if new_ip != ip:
                return
            time.sleep(1)


def disconnect():
    ip = get_public_ip_address()
    was_running = programs_manager.close_program(programs_manager.PROTON_VPN)
    programs_manager.close_program(programs_manager.PROTON_VPN_SERVICE)
    programs_manager.close_program(programs_manager.PROTON_UPDATE_SERVICE)
    programs_manager.close_program(programs_manager.OPEN_VPN)
    if not was_running:
        return
    while True:
        new_ip = get_public_ip_address()
        print(f'{new_ip=}')

        if new_ip != ip:
            break
        print(f'Ip address is still {ip}')
        time.sleep(1)
