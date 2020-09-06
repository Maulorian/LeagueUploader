import io
import traceback

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


def get_players_data(name):
    full_url = CURRENT_GAME_PAGE + name

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    r = requests.get(full_url, headers=headers)
    html = r.text
    with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")

    challengers = extract_players_order(soup)
    print(f'[{__name__.upper()}] - Players Order: {challengers}')

    return challengers


def extract_players_order(soup):
    players = []
    players_name = soup.findAll("div", {'class': 'card card-5'})

    for i in range(10):
        with open(f'player.html', 'w') as f:
            f.write(str(players_name[i]))
        player_name = players_name[i].attrs['data-summonername'].strip()


        # player_data = {}
        # player_data['champion'] = players_name[i].find('img')['title']
        # player_ranking_information = players_name[i].find('div', {'class': 'cardBody'})
        # player_ranking_information = player_ranking_information.find('div', {'class': 'box rankingsBox canExpand'})
        # player_ranking_information = player_ranking_information.find('div', {'class': 'imgFlex'})
        # player_ranking_information = player_ranking_information.find('div', {'class': 'txt'})
        # player_ranking_information = player_ranking_information.find('div', {'class': 'title'})
        # player_data['tier'] = player_ranking_information.find(text=True, recursive=False).strip()
        # league_points = player_ranking_information.find('span', {'class': 'subtitle'}).text.strip()
        # player_data['lp'] = league_points.split()[0]
        players.append(player_name)
        # players[player_name] = player_data


    return players


class MatchNotStartedException(Exception):
    pass


def get_current_match_duration(summoner_name):
    full_url = CURRENT_GAME_PAGE + summoner_name

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    r = requests.get(full_url, headers=headers)
    html = r.text
    with io.open(f'{__name__}_response.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")
    duration = soup.find('span', id='gameDuration')
    if duration is None:
        raise MatchNotStartedException
    print(duration)
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
        traceback.print_exc()
        return
