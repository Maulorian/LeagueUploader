import re

import requests
from bs4 import BeautifulStoneSoup, BeautifulSoup

from lib.constants import HEADERS_WITH_USER_AGENT

BASE_URL = 'https://www.leagueofgraphs.com/'

SUMMONER = 'summoner/'
MATCH = 'match/'

REGION_URLS = {
    'KR': 'kr/'
}

class ObserverKeyNotFoundException(Exception):
    pass

def extract_match_recording_settings(html, match_id):
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.find_all('a'))
    buttons = soup.find_all('button', {'data-spectate-gameid': True})
    button = next((button for button in buttons if button['data-spectate-gameid'] == str(match_id)), None)
    if button is None:
        raise ObserverKeyNotFoundException
    observer_key = button['data-spectate-encryptionkey']
    host = button['data-spectate-endpoint']
    return host, observer_key


def get_match_recording_settings(match_id, region, random_player):
    region_url = REGION_URLS[region]
    url = BASE_URL + SUMMONER + region_url + random_player
    print(url)

    r = requests.get(url, headers=HEADERS_WITH_USER_AGENT, timeout=60)
    html = r.text
    # print(html)
    return extract_match_recording_settings(html, match_id)