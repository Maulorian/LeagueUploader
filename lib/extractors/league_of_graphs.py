import re

import requests
from bs4 import BeautifulStoneSoup, BeautifulSoup

from lib.constants import HEADERS_WITH_USER_AGENT
from lib.managers import vpn_manager

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


def get_players_data(match_id, region):
    vpn_manager.connect()

    region_url = REGION_URLS[region]
    full_url = BASE_URL + MATCH + region_url + str(match_id)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    }
    r = requests.get(full_url, headers=headers, timeout=60)
    html = r.text

    players_data = extract_players_data(html)

    return players_data


def extract_players_data(html):
    players_data = ['' for i in range(10)]
    soup = BeautifulSoup(html, "html.parser")

    players_html = soup.findAll("div", {'class': 'name'})
    summoner_names = [div.text.strip() for div in players_html]
    j = 0
    for i in range(0, 10, 2):
        players_data[j] = summoner_names[i]
        players_data[j + 5] = summoner_names[i + 1]
        j += 1
    return players_data
