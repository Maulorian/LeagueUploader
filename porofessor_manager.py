import io

import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import unquote
from datetime import datetime, timedelta

CURRENT_GAME_PAGE = 'https://porofessor.gg/partial/live-partial/euw/'


def get_summoners_name_from_html(soup):
    challengers = soup.findAll("div", class_ ="card card-5")
    challengers = list(map(lambda div: div['data-summonername'], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unidecode(unquote(challenger)), challengers))
    return challengers

def get_player_positions(summoner):
    name = summoner.name
    full_url = CURRENT_GAME_PAGE + name

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    r = requests.get(full_url, headers=headers)
    html = r.text
    with io.open(f'{__name__}_response.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")

    challengers = get_summoners_name_from_html(soup)
    print(f'[{__name__.upper()}] - Players Order: {challengers}')

    return challengers


def get_current_match_duration(summoner):
    name = summoner.name
    full_url = CURRENT_GAME_PAGE + name

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    r = requests.get(full_url, headers=headers)
    html = r.text
    with io.open(f'{__name__}_response.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")
    duration = soup.find('span', id='gameDuration')
    print(duration)
    if not duration:
        return
    try:
        duration = duration.text
        duration = duration.replace('(', '')
        duration = duration.replace(')', '')
        print(duration)
        t = datetime.strptime(duration, "%M:%S")
        # ...and use datetime's hour, min and sec properties to build a timedelta
        duration = timedelta(minutes=t.minute, seconds=t.second)
        return duration
    except ValueError:
        return
