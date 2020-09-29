import datetime
import re

import requests
import io
from bs4 import BeautifulSoup

from urllib.parse import unquote

from cassiopeia import Region, Queue, Side
from datetime import datetime

from lib.utils import pretty_log

REGION_URLS = {
    Region.korea.value: 'www.op.gg',
    Region.europe_west.value: 'euw.op.gg'
}
SCHEMA = ' http://'
LADDER = '/ranking/ladder'
SPECTATE_PLAYER_PAGE = '/summoner/spectator/userName='
USERNAME_URL = '/summoner/userName='
SPECTATE_MATCH = '/match/new/batch/id='
PAGE = '/page='
SPECTATE = '/spectate'
SPECTATE_TAB = '/pro'
PRO_PLAYERS_LIST = '/list/'


def extract_match_type(soup):
    queue = soup.find('div', {'class': 'SpectateSummoner'})
    queue = queue.find('div', {'class': 'Box'})
    queue = queue.find('div', {'class': 'Title'})
    if 'Ranked Solo' in queue.text.strip():
        return True
    return False


def spectate_tab(region):
    region_url = REGION_URLS[region]
    spectate_tab = SCHEMA + region_url + SPECTATE + SPECTATE_TAB
    print(f'[{__name__.upper()}] - Getting spectate_tab')

    r = requests.get(spectate_tab, timeout=60)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    players = extract_names(soup)
    return players


@pretty_log
def get_ladder(region):
    region_url = REGION_URLS[region]
    ladder_url = SCHEMA + region_url + LADDER
    url = ladder_url
    # print(f'[{__name__.upper()}] - Getting ladder in first page')

    r = requests.get(url, timeout=60)
    html = r.text
    # with io.open('opgg_response.html', "w", encoding="utf-8") as f:
    #     f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    players = extract_names(soup)
    players_dict = {}
    for player in players:
        players_dict[player] = True
    return players_dict.keys()


def extract_pro_player_names(html):
    soup = BeautifulSoup(html, "html.parser")
    player_tags = soup.findAll('li', {'data-summoner-name': True})
    pro_player_names = {}
    for player_tag in player_tags:
        summoner_team = player_tag.find('div', {'class': 'SummonerTeam'})
        summoner_name = player_tag.find('div', {'class': 'SummonerName'})
        pro_name = player_tag.find('span', {'class': 'SummonerExtra'})

        summoner_team = summoner_team.text.strip()
        summoner_name = summoner_name.text.strip()
        pro_name = pro_name.text.strip()
        pro_player_info = {
            'team': None,
            'name': pro_name
        }
        if summoner_team != 'Progamer':
            pro_player_info['team'] = summoner_team

        pro_player_names[summoner_name] = pro_player_info
    return pro_player_names


def get_pro_players_info(region):
    region_url = REGION_URLS[region]
    pro_players_url = SCHEMA + region_url + SPECTATE + PRO_PLAYERS_LIST
    r = requests.get(pro_players_url, timeout=60)
    html = r.text
    players_name = extract_pro_player_names(html)
    return players_name

def extract_names(soup):
    challengers = soup.findAll('a')
    challengers = list(map(lambda link: link['href'], challengers))
    challengers = list(filter(lambda href: USERNAME_URL in href, challengers))
    challengers = list(map(lambda href: href.split('=')[1], challengers))
    challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
    challengers = list(map(lambda challenger: unquote(challenger), challengers))
    challengers = list(map(lambda challenger: challenger.strip(), challengers))
    return challengers


def get_match_data(player_name, region):
    region_url = REGION_URLS[region]
    url = SCHEMA + region_url + SPECTATE_PLAYER_PAGE + player_name

    r = requests.get(url, timeout=60)
    html = r.text
    # with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
    #     f.write(html)
    soup = BeautifulSoup(html, "html.parser")

    match_data = {}

    players = extract_players_data(soup)
    if not len(players):
        # print(f'{datetime.now()} [{__name__.upper()}] - No opgg information for "{player_name}"')
        return

    is_ranked = extract_match_type(soup)
    # print(f'[{__name__.upper()}] - Players Order: {players}')
    match_data['players_data'] = players
    match_data['is_ranked'] = is_ranked
    print(f'{datetime.now()} [{__name__.upper()}] - Getting player match data for "{player_name}"')

    return match_data


def get_player_page(region):
    region_url = REGION_URLS[region]
    player_page_url = SCHEMA + region_url + USERNAME_URL
    return player_page_url


def extract_players_data(soup):
    players = {}
    players_html = soup.find_all("tr")
    players_html = list(
        filter(lambda tr: tr.get('id') is not None and 'SpectateBigListRow' in tr.get('id'), players_html))
    side = Side.blue
    for i in range(len(players_html)):
        # with open(f'player.html', 'w') as f:
        #     f.write(str(players_html[i]))
        player_html = players_html[i]
        player_data = {}

        player_data['champion'] = player_html.find('a').get('title')
        player_name = player_html.find('a', {'class': "SummonerName"}).text.strip()
        player_ranking_information = player_html.find('div', {'class': 'TierRank'}).text.strip()
        tier, lp = get_tier_lp_from_rank(player_ranking_information)

        player_data['tier'] = tier
        player_data['lp'] = lp
        player_data['side'] = side
        if i == 4:
            side = Side.red
        players[player_name] = player_data

    return players


def get_tier_lp_from_rank(rank):
    # print(f"getting tier and lp from {rank}")
    p = re.compile("([a-zA-Z]*( [1-4])?) \\(([0-9]*) LP\\)")
    result = p.search(rank)
    if not result:
        return 'Unranked', None

    tier = result.group(1)
    lp = result.group(3)
    return tier, lp
