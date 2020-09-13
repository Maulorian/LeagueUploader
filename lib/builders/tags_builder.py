CHALLENGER_TAG = 'challenger'
REPLAYS_TAG = 'replays'
MATCHUPS_TAG = 'matchups'


def get_tags(match_info):
    player_champion = match_info.get('player_champion')
    role = match_info.get('role')
    summoner_name = match_info.get('summoner_name')
    enemy_champion = match_info.get('enemy_champion')
    region = match_info.get('region')
    player_champion = player_champion.lower()
    enemy_champion = enemy_champion.lower()
    role = role.lower()
    summoner_name = summoner_name.lower()
    tags = []
    tags.append(f'{player_champion} {role}')
    tags.append(f'{player_champion} {CHALLENGER_TAG} {region}')
    tags.append(f'{player_champion} {region} {CHALLENGER_TAG} ')
    tags.append(f'{player_champion} vs {enemy_champion}')
    tags.append(f'{summoner_name} {player_champion}')
    tags.append(f'{summoner_name}')

    return tags
