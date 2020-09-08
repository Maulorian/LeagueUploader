import datetime

import requests
import io
from bs4 import BeautifulSoup

from urllib.parse import unquote

from cassiopeia import Region, Queue
from datetime import datetime
REGION_URLS = {
    Region.korea: 'www.op.gg',
    Region.europe_west: 'euw.op.gg'
}
SCHEMA = ' http://'
LADDER = '/ranking/ladder'
SPECTATE_PLAYER_PAGE = '/summoner/spectator/userName='
USERNAME_URL = '/summoner/userName='
SPECTATE_MATCH = '/match/new/batch/id='
PAGE = '/page='


def extract_match_type(soup):
    queue = soup.find('div', {'class': 'SpectateSummoner'})
    queue = queue.find('div', {'class': 'Box'})
    queue = queue.find('div', {'class': 'Title'})
    if 'Ranked Solo' in queue.text.strip():
        return Queue.ranked_solo_fives


class OPGGExtractor:
    def __init__(self, region):
        self.region = region

    def get_ladder(self, page_nb):
        region_url = REGION_URLS[self.region]
        ladder_url = SCHEMA + region_url + LADDER
        url = ladder_url if page_nb == 1 else ladder_url + PAGE + str(page_nb)
        print(f'[{__name__.upper()}] - Getting ladder in page {page_nb}')

        r = requests.get(url)
        html = r.text
        # with io.open('opgg_response.html', "w", encoding="utf-8") as f:
        #     f.write(html)

        soup = BeautifulSoup(html, "html.parser")
        players = self.extract_names(soup)
        players_dict = {}
        for player in players:
            players_dict[player] = True
        return players_dict.keys()

    def extract_names(self, soup):
        challengers = soup.findAll('a')
        challengers = list(map(lambda link: link['href'], challengers))
        challengers = list(filter(lambda href: USERNAME_URL in href, challengers))
        challengers = list(map(lambda href: href.split('=')[1], challengers))
        challengers = list(map(lambda challenger: challenger.replace('+', ' '), challengers))
        challengers = list(map(lambda challenger: unquote(challenger), challengers))
        challengers = list(map(lambda challenger: challenger.strip(), challengers))
        return challengers

    def get_match_data(self, player_name):

        region_url = REGION_URLS[self.region]
        url = SCHEMA + region_url + SPECTATE_PLAYER_PAGE + player_name

        r = requests.get(url)
        html = r.text
        # with io.open(f'{__name__.upper()}.html', "w", encoding="utf-8") as f:
        #     f.write(html)
        soup = BeautifulSoup(html, "html.parser")

        match_data = {}

        players = extract_players_data(soup)
        if not len(players):
            return

        match_type = extract_match_type(soup)
        # print(f'[{__name__.upper()}] - Players Order: {players}')
        match_data['players_data'] = players
        match_data['match_type'] = match_type
        print(f'{datetime.now()} [{__name__.upper()}] - Getting player match data for "{player_name}": {match_data}')

        return match_data

    def get_game_bat(self, match_id):
        region_url = REGION_URLS[self.region]
        url = SCHEMA + region_url + SPECTATE_MATCH + str(match_id)
        r = requests.get(url)
        return r.text

    def get_player_page(self):
        region_url = REGION_URLS[self.region]
        player_page_url = SCHEMA + region_url + USERNAME_URL
        return player_page_url


def extract_players_data(soup):
    players = {}
    players_html = soup.find_all("tr")
    players_html = list(
        filter(lambda tr: tr.get('id') is not None and 'SpectateBigListRow' in tr.get('id'), players_html))
    for i in range(len(players_html)):
        # with open(f'player.html', 'w') as f:
        #     f.write(str(players_html[i]))
        player_html = players_html[i]
        player_data = {}

        player_data['champion'] = player_html.find('a').get('title')
        player_name = player_html.find('a', {'class': "SummonerName"}).text.strip()
        player_ranking_information = player_html.find('div', {'class': 'TierRank'}).text.strip()
        player_data['rank'] = player_ranking_information

        players[player_name] = player_data

    return players

