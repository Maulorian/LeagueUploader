CHALLENGER_TAG = 'challenger'
REPLAYS_TAG = 'replays'
MATCHUPS_TAG = 'matchups'
HIGHLIGHTS = 'highlights'

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

    pro_player_info = match_info.get('pro_player_info')
    if pro_player_info:
        summoner_name = pro_player_info['name']

    tags = []
    tags.append(f'{player_champion} {CHALLENGER_TAG}')
    tags.append(f'{player_champion} {role} ')
    tags.append(f'{player_champion} {CHALLENGER_TAG} {HIGHLIGHTS}')
    tags.append(f'{player_champion} {region}')
    tags.append(f'{player_champion} vs {enemy_champion}')
    tags.append(f'{summoner_name} {player_champion}')
    tags.append(f'{summoner_name} {HIGHLIGHTS}')

    return tags
