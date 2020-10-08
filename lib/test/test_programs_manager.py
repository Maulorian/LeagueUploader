import unittest

from lib.managers.programs_manager import open_program, CHROME_EXE, CHROME_DIR, close_program


class TestProgramManager(unittest.TestCase):
    def test_open_program(self):
        open_program(CHROME_EXE, CHROME_DIR)

    def test_close_program(self):
        close_program(CHROME_EXE)