import unittest

import lib.managers.programs_manager as programs_manager

class TestProgramManager(unittest.TestCase):
    def test_open_program(self):
        programs_manager.open_program(programs_manager.PROTON_VPN)

    def test_close_program(self):
        programs_manager.close_program(programs_manager.PROTON_VPN)
        programs_manager.close_program(programs_manager.PROTON_VPN_SERVICE)
        programs_manager.close_program(programs_manager.PROTON_UPDATE_SERVICE)
        programs_manager.close_program(programs_manager.OPEN_VPN)

        # pm.close_program(pm.PROTON_VPN)