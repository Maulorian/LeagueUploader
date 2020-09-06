from python import opgg_manager


def get_description(match_info):
    players = match_info.get('players')
    # player_champion = match_info.get('player_champion')
    # role = match_info.get('role')
    # summoner_name = match_info.get('summoner_name')
    # enemy_champion = match_info.get('enemy_champion')
    # champion_region_value = match_info.get('champion_region_value')
    # tier = match_info.get('tier')
    # league_points = match_info.get('league_points'),
    # version = match_info.get('version')
    description = 'Players opgg\'s:\n'
    for player_name, player_data in players.items():
        description += f'{player_name} {player_data.get("tier")} {player_data.get("league_points")} LP on {player_data.get("champion")} : {opgg_manager.PLAYER_PAGE}{player_name}\n'
    print(f'[{__name__.upper()}] - Description: {description}')
    return description
