import io
import traceback

import requests
from bs4 import BeautifulSoup
from cassiopeia import Region
from unidecode import unidecode
from urllib.parse import unquote, quote
from datetime import datetime, timedelta

REGION_URLS = {
    Region.korea: 'kr/',
    Region.europe_west: 'euw/'
}
BASE_URL = ' http://porofessor.gg/'
SPECTATE_PLAYER_PAGE = 'partial/live-partial/'


class PorofessorExtractor:
    def __init__(self, region):
        self.region = region

    def get_match_data(self, summoner_name):
        region_url = REGION_URLS[self.region]
        full_url = BASE_URL + SPECTATE_PLAYER_PAGE + region_url + summoner_name.replace(' ', '%20')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
        r = requests.get(full_url, headers=headers)
        html = r.text
        with io.open(f'{__name__}.html', "w", encoding="utf-8") as f:
            f.write(html)
        soup = BeautifulSoup(html, "html.parser")
        match = {}

        players = extract_players_order(soup)
        if not len(players):
            print(f'[OPGG MANAGER] - No information for this match')
            return

        duration = get_current_match_duration(soup)
        # print(f'[{__name__.upper()}] - Players Order: {players}')
        match['players'] = players
        match['duration'] = duration

        return match


def get_current_match_duration(soup):
    duration = soup.find('span', id='gameDuration')
    if duration is None:
        return timedelta(seconds=0)
    try:
        duration = duration.text
        duration = duration.replace('(', '')
        duration = duration.replace(')', '')
        t = datetime.strptime(duration, "%M:%S")
        duration = timedelta(minutes=t.minute, seconds=t.second)
        return duration
    except ValueError:
        return

def get_summoners_name_from_html(soup):
    challengers = soup.findAll("div", class_ ="card card-5")
    challengers = list(map(lambda div: div['data-summonername'], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unidecode(unquote(challenger)), challengers))
    return challengers


# def get_players_data(name):
#     print(f'[{__name__.upper()}] - Getting player data')
#     full_url = CURRENT_GAME_PAGE + name
#
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
#     r = requests.get(full_url, headers=headers)
#     html = r.text
#     with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
#         f.write(html)
#     soup = BeautifulSoup(html, "html.parser")
#
#     challengers = extract_players_order(soup)
#     print(f'[{__name__.upper()}] - Players Order: {challengers}')
#
#     return challengers


def extract_players_order(soup):
    players_html = soup.findAll("div", {'class': 'card card-5'})
    players = list(map(lambda player_html: player_html.attrs['data-summonername'].strip(), players_html))
    return players


class MatchNotStartedException(Exception):
    pass



