TITLE_CANVAS = '{player_champion} {role} vs {enemy_champion} - {summoner_name} {champion_region_value} {rank} ' \
               ' Patch {version} '


def get_title(match_info):
    player_champion = match_info.get('player_champion')
    role = match_info.get('role')
    summoner_name = match_info.get('summoner_name')
    enemy_champion = match_info.get('enemy_champion')
    champion_region_value = match_info.get('champion_region_value')
    rank = match_info.get('rank')
    version = match_info.get('version')

    return TITLE_CANVAS.format(player_champion=player_champion,
                               role=role,
                               summoner_name=summoner_name,
                               enemy_champion=enemy_champion,
                               champion_region_value=champion_region_value,
                               rank=rank,
                               version=version)