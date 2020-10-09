import os

import requests
from cassiopeia import Region, Queue, cassiopeia

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
    url = SCHEMA + region_url + BASE_URL + MATCH_URL + str(math_id)

    r = requests.get(url, headers={"X-Riot-Token": os.getenv("RIOT_KEY")})
    if r.status_code != 200:
        print(f'{math_id}: {r.status_code}')
        return
    return r.json()


def get_current_game_version():
    r = requests.get('https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json')
    version = r.json()['patches'][-1]['name']
    return version


def add_rank_information_to_player(players_data, region):
    print(players_data)
    for name, player_data in players_data.items():
        summoner = cassiopeia.get_summoner(name=name, region=region)
        ranked_league = summoner.league_entries[Queue.ranked_solo_fives]
        tier = ranked_league.tier
        lp = ranked_league.league_points
        player_data['tier'] = tier
        player_data['lp'] = lp
    return players_data
