import unittest

from lib.managers.programs_manager import open_program, CHROME_EXE, close_program


class TestProgramManager(unittest.TestCase):
    def test_open_program(self):
        open_program(CHROME_EXE)

    def test_close_program(self):
        close_program(CHROME_EXE)