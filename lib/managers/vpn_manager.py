import time

from lib.managers import programs_manager
from lib.managers.programs_manager import running
from lib.utils import get_public_ip_address


def connect():
    if running(programs_manager.PROTON_VPN):
        return

    print('Connecting to vpn')
    ip = get_public_ip_address()
    while True:
        programs_manager.open_program(programs_manager.PROTON_VPN)
        start = time.time()

        while True:
            delta = time.time() - start
            if delta > 15:
                programs_manager.close_program(programs_manager.PROTON_VPN)
                programs_manager.close_program(programs_manager.PROTON_VPN_SERVICE)
                programs_manager.close_program(programs_manager.PROTON_UPDATE_SERVICE)
                programs_manager.close_program(programs_manager.OPEN_VPN)
                break
            new_ip = get_public_ip_address()
            if new_ip != ip:
                print('Connected')
                return


class VPNClosingException(Exception):
    pass


def disconnect():
    if not running(programs_manager.PROTON_VPN) and not running(programs_manager.OPEN_VPN):
        return
    print('Disconnecting from vpn')

    ip = get_public_ip_address()

    programs_manager.close_program(programs_manager.PROTON_VPN)
    programs_manager.close_program(programs_manager.PROTON_VPN_SERVICE)
    programs_manager.close_program(programs_manager.PROTON_UPDATE_SERVICE)
    programs_manager.close_program(programs_manager.OPEN_VPN)
    time.sleep(1)
    if running(programs_manager.PROTON_VPN) or running(programs_manager.OPEN_VPN):
        raise VPNClosingException

    while True:
        new_ip = get_public_ip_address()
        print(f'{new_ip=}')

        if new_ip != ip:
            print('Disconnected')

            break
        print(f'Ip address is still {ip}')
