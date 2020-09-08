import os

import requests
from cassiopeia import Region

SCHEMA = 'https://'

BASE_URL = '.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/'
REGION_URLS = {
    Region.korea: 'kr',
    Region.europe_west: 'euw1'
}


def get_match_duration(region, id):
    region_url = REGION_URLS.get(region)
    url = SCHEMA + region_url + BASE_URL + str(id)

    r = requests.get(url, headers={"X-Riot-Token": os.getenv("RIOT_KEY")})
    return r.json().get('gameLength')
