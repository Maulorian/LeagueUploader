import os
import pprint
import time

import requests
from requests import get


def pretty_log(function):
    def wrapper(*args):
        result = function(*args)
        file_name = function.__module__.split('.')[-1]
        if len(args):
            try:
                print(f'[{file_name.upper()}] - {function.__name__}({",".join(list(args))}) = {result}')
            except TypeError:
                print(f'[{file_name.upper()}] - {function.__name__}() = {result}')
        else:
            print(f'[{file_name.upper()}] - {function.__name__}() = {result}')
        return result

    return wrapper


def pretty_print(string):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(string)


def wait_seconds(WAIT_TIME):
    # print(f"[SPECTATOR] - Waiting {WAIT_TIME}")
    time.sleep(WAIT_TIME)


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def get_public_ip_address():
    while True:
        try:
            ip = get('https://api.ipify.org').text
            return ip
        except requests.exceptions.ConnectionError:
            time.sleep(1)
