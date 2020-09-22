import io
import traceback

import requests
from bs4 import BeautifulSoup
from cassiopeia import Region
from unidecode import unidecode
from urllib.parse import unquote, quote
from datetime import datetime, timedelta

from lib.utils import pretty_log

TRY_AGAIN_LATER = 'An Error has occured, please try again later'

REGION_URLS = {
    Region.korea.value: 'kr/',
    Region.europe_west.value: 'euw/'
}
BASE_URL = ' http://porofessor.gg/'
SPECTATE_PLAYER_PAGE = 'partial/live-partial/'


class PorofessorNoResponseException(Exception):
    pass


def get_match_data(summoner_name, region):
    region_url = REGION_URLS[region]
    full_url = BASE_URL + SPECTATE_PLAYER_PAGE + region_url + summoner_name.replace(' ', '%20')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    r = requests.get(full_url, headers=headers)
    html = r.text

    if TRY_AGAIN_LATER in html:
        print('PorofessorNoResponseException')
        raise PorofessorNoResponseException
    soup = BeautifulSoup(html, "html.parser")
    match_data = {}

    players = extract_players_order(soup)
    if not len(players):
        print(f'[{__name__.upper()}] - No information for this match')
        return

    already_started = match_already_started(soup)
    # print(f'[{__name__.upper()}] - Players Order: {players}')
    match_data['players'] = players
    match_data['already_started'] = already_started
    print(f'{datetime.now()} [{__name__.upper()}] - Getting player match data for "{summoner_name}"')

    return match_data


def match_already_started(soup):
    duration = soup.find('span', id='gameDuration')

    if duration is None:
        duration = timedelta(seconds=0)
    else:
        try:
            duration = duration.text
            duration = duration.replace('(', '')
            duration = duration.replace(')', '')
            t = datetime.strptime(duration, "%M:%S")
            duration = timedelta(minutes=t.minute, seconds=t.second)
        except ValueError:
            pass
    print(f'[{__name__.upper()}] - Duration={duration}')

    return duration.seconds - 3 * 60 > 0


def get_summoners_name_from_html(soup):
    challengers = soup.findAll("div", class_="card card-5")
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
