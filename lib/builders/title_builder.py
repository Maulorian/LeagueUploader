TITLE_CANVAS = '{player_champion} {role} vs {enemy_champion} - {kills} - {name} - {region} {tier} ({lp} LP) ' \
               'Patch {version}'


def manual_replace(s, char, index):
    return s[:index] + char + s[index + 1:]


def get_title(match_info):
    player_champion = match_info.get('player_champion')
    role = match_info.get('role')
    name = match_info.get('summoner_name').title()
    kills = f'{match_info.get("kills")} kills'

    pro_player_info = match_info.get('pro_player_info')
    if pro_player_info:
        name = []
        if pro_player_info['team']:
            name.append(pro_player_info["team"].title())
        name.append(pro_player_info["name"].title())
        name = ' '.join(name)

    enemy_champion = match_info.get('enemy_champion')
    region = match_info.get('region')
    tier = match_info.get('tier')
    lp = match_info.get('lp')
    version = match_info.get('version')

    return TITLE_CANVAS.format(player_champion=player_champion,
                               role=role,
                               kills=kills,
                               name=name,
                               enemy_champion=enemy_champion,
                               region=region,
                               tier=tier,
                               lp=lp,
                               version=version)