TITLE_CANVAS = '{player_champion} {role} vs {enemy_champion} - {summoner_name} {region} {rank} ' \
               'Patch {version}'


def manual_replace(s, char, index):
    return s[:index] + char + s[index +1:]


def get_title(match_info):
    player_champion = match_info.get('player_champion')
    role = match_info.get('role')
    summoner_name = match_info.get('summoner_name')
    first_letter = summoner_name[0].upper()
    summoner_name = manual_replace(summoner_name, first_letter, 0)
    enemy_champion = match_info.get('enemy_champion')
    region = match_info.get('region').value
    rank = match_info.get('rank')
    version = match_info.get('version')

    return TITLE_CANVAS.format(player_champion=player_champion,
                               role=role,
                               summoner_name=summoner_name,
                               enemy_champion=enemy_champion,
                               region=region,
                               rank=rank,
                               version=version)