import requests
import io
from bs4 import BeautifulSoup

from urllib.parse import unquote

LADDER_URL = 'https://euw.op.gg/ranking/ladder/'
SPECTATE_TAB_URL = 'https://euw.op.gg/spectate/pro/'
SPECTATE_PLAYER_PAGE = 'https://euw.op.gg/summoner/spectator/userName='
PLAYER_PAGE = 'https://euw.op.gg/summoner/userName='


def get_top100_challengers():
    r = requests.get(LADDER_URL)
    html = r.text
    with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    challengers = extract_names(soup)
    return challengers


def get_spectate_tab_players():
    print(f'[{__name__.upper()}] - Getting Players from OPGG Spectate Tab')

    r = requests.get(SPECTATE_TAB_URL)
    html = r.text
    with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    players = extract_names(soup)
    print(f'[{__name__.upper()}] - {players}')
    return players


def extract_names(soup):
    challengers = soup.findAll('a')
    challengers = list(map(lambda link: link['href'], challengers))
    challengers = list(filter(lambda href: '//euw.op.gg/summoner/userName=' in href, challengers))
    challengers = list(map(lambda href: href.split('=')[1], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unquote(challenger), challengers))
    return challengers

def get_players_data(name):
    full_url = SPECTATE_PLAYER_PAGE + name

    r = requests.get(full_url)
    html = r.text
    with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")

    challengers = extract_players_data(soup)
    print(f'[{__name__.upper()}] - Players Order: {challengers}')

    return challengers

def extract_players_data(soup):
    players = {}
    players_html = soup.find_all("div", {'class': 'Content'})
    players_html = soup.find_all("tr")
    players_html = list(filter(lambda tr: tr.get('id') is not None and 'SpectateBigListRow' in tr.get('id'), players_html))
    for i in range(10):
        with open(f'player.html', 'w') as f:
            f.write(str(players_html[i]))
        player_html = players_html[i]
        player_data = {}

        player_data['champion'] = player_html.find('a').get('title')

        player_name = player_html.find('a', {'class': "SummonerName"}).text.strip()
        player_ranking_information = player_html.find('div', {'class': 'TierRank'}).text.strip()
        player_data['rank'] = player_ranking_information

        players[player_name] = player_data

    return players
# def get_current_match_duration(summoner):
#     name = summoner.name
#     full_url = PLAYER_PAGE + name
#
#     r = requests.get(full_url)
#     html = r.text
#     with io.open(f'{__name__}_response.html', "w", encoding="utf-8") as f:
#         f.write(html)
#     print(html)
#     soup = BeautifulSoup(html, "html.parser")
#     duration = soup.find('small', {"class": "time"})
#     print(duration)





# def extract_name_and_champion(soup):
#     # < a href = "/champion/akali/statistics" target = "_blank" class ="Image tip" title = "Akali" >
#     # < a href = "//euw.op.gg/summoner/userName=Scarlet+2" class ="SummonerName" target = "_blank" > Scarlet 2 < / a >
#     players = {}
#     players_name = soup.findAll("a", {'class': 'SummonerName'})
#     print(players_name)
#     players_champions = soup.findAll("a", {'class': 'Image tip'})
#     print(players_champions)
#     for i in range(10):
#         player_name = players_name[i].text
#         player_champion = players_champions[i].attrs.get('title')
#
#         players[player_name] = player_champion
#
#
#     return players


# def get_ordered_players(name):
#     r = requests.get(PLAYER_PAGE + name)
#     html = r.text
#     with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
#         f.write(html)
#     soup = BeautifulSoup(html, "html.parser")
#
#     players = extract_name_and_champion(soup)
#     print(f'[OPGG MANAGER] - Players Order: {players}')
#
#     return players


# def get_match_information(name):
#     r = requests.get(PLAYER_PAGE + name + '&')
#     html = r.text
#     with io.open('opgg_response.html', "w", encoding="utf-8") as f:
#         f.write(html)
#     soup = BeautifulSoup(html, "html.parser")
#     match = soup.find('div', class_='tabItem Content SummonerLayoutContent summonerLayout-spectator')
#     print(match)


