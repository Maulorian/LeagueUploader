import os

import datapipelines
import requests
from cassiopeia import Region, cassiopeia

from lib.managers.recorded_games_manager import get_recorded_games, delete_game
from lib.utils import pretty_print

SCHEMA = 'https://'

BASE_URL = '.api.riotgames.com/lol/'
REGION_URLS = {
    Region.korea.value: 'kr',
    Region.europe_west.value: 'euw1'
}

CHALLENGER_LEAGUE_URL = 'league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
CURRENT_GAME_URL = 'spectator/v4/active-games/by-summoner/'
MATCH_URL = 'match/v4/matches/'


def get_match_duration(region, id):
    region_url = REGION_URLS.get(region)
    url = SCHEMA + region_url + BASE_URL + str(id)

    r = requests.get(url, headers={"X-Riot-Token": os.getenv("RIOT_KEY")})
    return r.json().get('gameLength')


def get_all_challenger_players(region):
    region_url = REGION_URLS.get(region)
    url = SCHEMA + region_url + BASE_URL + CHALLENGER_LEAGUE_URL

    response = requests.get(url, headers={"X-Riot-Token": os.getenv("RIOT_KEY")}, timeout=60)
    parsed = response.json()
    summoners = parsed.get('entries')
    summoners = sorted(summoners, key=lambda summoner_data: summoner_data.get('leaguePoints'), reverse=True)
    summoners_data = []
    for summoner in summoners:
        summoner_data = {
            'summoner_name': summoner.get('summonerName'),
            'lp': summoner.get('leaguePoints'),
            'region': region,
            'summoner_id': summoner.get('summonerId')
        }
        summoners_data.append(summoner_data)
    return summoners_data


def get_match(math_id, region):
    region_url = REGION_URLS.get(region)
    url = SCHEMA + region_url + BASE_URL + MATCH_URL +str(math_id)

    r = requests.get(url, headers={"X-Riot-Token": os.getenv("RIOT_KEY")})
    if r.status_code != 200:
        print(f'{math_id}: {r.status_code}')
        return
    return r.json()



