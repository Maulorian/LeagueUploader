from lib.extractors import opgg_extractor


def get_player_kills(match_data):
    player_kill_timestamps = match_data.get('player_kill_timestamps')

    description = 'Kills:\n'
    description += '\n'
    description += '00:00 Game Start\n'
    for timestamp in player_kill_timestamps:
        description += f'{timestamp.get("time")} Kill vs {timestamp.get("victim")}\n'
    return description


def get_description(match_data):
    description = get_players_opgg(match_data)
    description += '\n'
    # description += get_player_kills(match_data)

    print(f'[{__name__.upper()}] - Description: {description}')
    return description


def get_players_opgg(match_data):
    players_data = match_data.get('players_data')
    player_page_url = opgg_extractor.get_player_page(match_data['region'])

    description = 'Players Profiles:'
    description += '\n\n'

    lines = [f'{player_data.get("champion")} - {player_data.get("tier")} {player_data.get("lp")} LP : {player_page_url}{player_name.replace(" ", "+")}' for player_name, player_data in players_data.items()]
    for i, line in enumerate(lines):
        description += f'{line}\n'
        if i == 4:
            description += '\n'
    return description
