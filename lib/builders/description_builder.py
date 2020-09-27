from lib.extractors import opgg_extractor


def get_player_kills(match_data):
    player_kill_timestamps = match_data.get('player_kill_timestamps')

    description = 'Kills:\n'
    description += '\n'
    description += '0:00 - Game Start\n'
    for timestamp in player_kill_timestamps:
        description += f'{timestamp.get("time")} - Kill vs {timestamp.get("victim")}\n'
    return description


def get_description(match_data):
    description = get_players_opgg(match_data)
    description += '\n'
    description = get_player_kills(match_data)

    print(f'[{__name__.upper()}] - Description: {description}')
    return description


def get_players_opgg(match_data):
    players_data = match_data.get('players_data')
    player_page_url = opgg_extractor.get_player_page(match_data['region'])

    description = 'Players Profiles:'
    description += '\n\n'

    summoners = [player_data.get("champion") for player_data in players_data.values()]
    padding = max(map(len, summoners))

    for i, player_data in enumerate(players_data.values()):
        summoners[i] = '{0} {1}'.format(summoners[i].ljust(padding), player_data.get("tier"))

    padding = max(map(len, summoners))

    for i, player_data in enumerate(players_data.values()):
        summoners[i] = '{0} ({1} LP)'.format(summoners[i].ljust(padding), player_data.get("lp"))

    padding = max(map(len, summoners))
    for i, player_name in enumerate(players_data.keys()):
        summoners[i] = '{0}: {1}{2}'.format(summoners[i].ljust(padding), player_page_url, player_name.replace(" ", "+"))

    description += '\n'.join(summoners)
    return description
