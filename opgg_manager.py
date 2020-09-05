import time

import requests
import io
from bs4 import BeautifulSoup
from cassiopeia import GameMode, Queue, GameType
from unidecode import unidecode

from urllib.parse import unquote
import cassiopeia as cass
import spectator

LADDER_URL = 'https://euw.op.gg/ranking/ladder/'
SPECTATE_TAB_URL = 'https://euw.op.gg/spectate/pro/'
PLAYER_PAGE = 'https://euw.op.gg/summoner/spectator/userName='


def get_top100_challengers():
    r = requests.get(LADDER_URL)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    challengers = get_summoners_name_from_html(soup)
    return challengers


def get_current_match_duration(summoner):
    name = summoner.name
    full_url = PLAYER_PAGE + name

    r = requests.get(full_url)
    html = r.text
    with io.open(f'{__name__}_response.html', "w", encoding="utf-8") as f:
        f.write(html)
    print(html)
    soup = BeautifulSoup(html, "html.parser")
    duration = soup.find('small', {"class": "time"})
    print(duration)




def get_summoners_name_from_html(soup):
    challengers = soup.findAll("a")
    challengers = list(map(lambda link: link['href'], challengers))
    challengers = list(filter(lambda href: '//euw.op.gg/summoner/userName=' in href, challengers))
    challengers = list(map(lambda href: href.split('=')[1], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unidecode(unquote(challenger)), challengers))
    return challengers


def get_player_positions(summoner):
    name = summoner.name
    r = requests.get(PLAYER_PAGE + name)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")

    challengers = get_summoners_name_from_html(soup)
    print(f'[OPGG MANAGER] - Players Order: {challengers}')

    return challengers


# def get_match_information(name):
#     r = requests.get(PLAYER_PAGE + name + '&')
#     html = r.text
#     with io.open('opgg_response.html', "w", encoding="utf-8") as f:
#         f.write(html)
#     soup = BeautifulSoup(html, "html.parser")
#     match = soup.find('div', class_='tabItem Content SummonerLayoutContent summonerLayout-spectator')
#     print(match)


def get_spectate_tab_players():
    r = requests.get(SPECTATE_TAB_URL)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")

    return get_summoners_name_from_html(soup)