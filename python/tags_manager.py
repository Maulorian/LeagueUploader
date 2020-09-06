REPLAYS_TAG = 'challenger replays'
MATCHUPS_TAG = 'challenger matchups'


def get_tags(match_info):
    player_champion = match_info.get('player_champion')
    role = match_info.get('role')
    summoner_name = match_info.get('summoner_name')
    enemy_champion = match_info.get('enemy_champion')
    # champion_region_value = match_info.get('champion_region_value')
    # tier = match_info.get('tier')
    # league_points = match_info.get('league_points'),
    # version = match_info.get('version')

    tags = []
    tags.append(f'{player_champion} {REPLAYS_TAG}')
    tags.append(f'{player_champion} {MATCHUPS_TAG}')
    tags.append(f'{summoner_name} {REPLAYS_TAG}')
    tags.append(f'{summoner_name} {MATCHUPS_TAG}')
    tags.append(f'{role} {REPLAYS_TAG}')
    tags.append(f'{role} {MATCHUPS_TAG}')
    tags.append(f'{player_champion} vs {enemy_champion} {REPLAYS_TAG}')
    tags.append(f'{player_champion} vs {enemy_champion} {MATCHUPS_TAG}')
    return tags
