from lib.extractors import opgg_extractor


def get_description(match_info):
    players_data = match_info.get('players_data')
    # player_champion = match_info.get('player_champion')
    # role = match_info.get('role')
    # summoner_name = match_info.get('summoner_name')
    # enemy_champion = match_info.get('enemy_champion')
    # champion_region_value = match_info.get('champion_region_value')
    # tier = match_info.get('tier')
    # league_points = match_info.get('league_points'),
    # version = match_info.get('version')
    description = 'Players opgg\'s:\n\n'
    player_page_url = opgg_extractor.get_player_page(match_info['region'])
    for player_name, player_data in players_data.items():
        description += f'{player_data.get("champion")} {player_data.get("rank")} : {player_page_url}{player_name.replace(" ", "+")}\n'
    print(f'[{__name__.upper()}] - Description: {description}')
    return description
