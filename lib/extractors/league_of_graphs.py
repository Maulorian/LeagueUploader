import re

import requests
from bs4 import BeautifulStoneSoup, BeautifulSoup

from lib.constants import HEADERS_WITH_USER_AGENT

BASE_URL = 'https://www.leagueofgraphs.com/'

MATCH = 'match/'

REGION_URLS = {
    'KR': 'kr/'
}


def extract_match_recording_settings(html):
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.find_all('a'))
    button = soup.find('td', {'class': 'replayTd'})
    infos = button.find('a')
    try:
        observer_key = infos['data-spectate-encryptionkey']
        host = infos['data-spectate-endpoint']
    except TypeError:
        return None, None
    return host, observer_key


def get_match_recording_settings(match_id, region):
    region_url = REGION_URLS[region]
    url = BASE_URL + MATCH + region_url + str(match_id)
    print(url)

    r = requests.get(url, headers=HEADERS_WITH_USER_AGENT, timeout=60)
    html = r.text
    # print(html)
    return extract_match_recording_settings(html)