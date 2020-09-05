import requests
import io
from bs4 import BeautifulSoup
from cassiopeia import GameMode, Queue, GameType
from unidecode import unidecode

from urllib.parse import unquote
import cassiopeia as cass
import spectator

LADDER_URL = 'https://euw.op.gg/ranking/ladder/'
PLAYING_URL = 'https://euw.op.gg/spectate/pro/'
PLAYER_PAGE = 'https://euw.op.gg/summoner/spectator/userName='

def get_top100_challengers():
    r = requests.get(LADDER_URL)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    challengers = get_summoners_name_from_html(soup)
    return challengers

def get_challenger_in_ranked_match(challengers):
    print(f'[OPGG MANAGER] - Getting Player in Ranked Game')

    for summoner_name in challengers:
        summoner = cass.get_summoner(name=summoner_name)
        match = spectator.get_current_match(summoner)
        if match is None:
            continue
        if match.type != GameType.matched:
            continue
        print(f'[OPGG MANAGER] - Duration={match.duration}')
        just_started = match.duration.seconds-2*60 < 0

        if not just_started:
            continue
        if match.queue != Queue.ranked_solo_fives:
            continue

        return summoner_name


def get_challenger_player(from_ladder=False):
    print(f'[OPGG MANAGER] - Getting Challenger Player {{from_ladder={from_ladder}}}')
    if from_ladder:
        challengers = get_top100_challengers()
    else:
        challengers = get_currently_playing_challengers()

    challenger = get_challenger_in_ranked_match(challengers)
    return challenger


def get_summoners_name_from_html(soup):
    challengers = soup.findAll("a")
    challengers = list(map(lambda link: link['href'], challengers))
    challengers = list(filter(lambda href: '//euw.op.gg/summoner/userName=' in href, challengers))
    challengers = list(map(lambda href: href.split('=')[1], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unidecode(unquote(challenger)), challengers))
    return challengers

def get_player_position(summoner):
    name = summoner.name
    r = requests.get(PLAYER_PAGE + name)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")

    challengers = get_summoners_name_from_html(soup)
    return challengers.index(name)


def get_currently_playing_challengers():
    r = requests.get(PLAYING_URL)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    return get_summoners_name_from_html(soup)