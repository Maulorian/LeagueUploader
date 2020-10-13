import datapipelines
from cassiopeia import cassiopeia, Queue, Region

from lib.managers import vpn_manager
from lib.managers.recorded_games_manager import delete_game, get_recorded_games, update_game
from lib.utils import pretty_print

GAMES_TO_KEEP = 20


def get_finished_recorded_games():
    finished_games = []
    vpn_manager.disconnect()
    games = get_recorded_games()
    for i, mongo_game in enumerate(games):
        match_id = mongo_game.get('match_id')
        region = mongo_game.get('region')
        data = {
            'mongo_game': mongo_game
        }

        is_finished = mongo_game.get('is_finished')

        if not is_finished:
            try:
                cass_match = cassiopeia.get_match(match_id, region=region)
                is_remake = cass_match.is_remake
            except datapipelines.common.NotFoundError:
                print(f'[{i}/{len(games)}] Game {match_id} not finished')
                continue
            data['cass_match'] = cass_match

        print(f'[{i}/{len(games)}] Game {match_id} is finished')
        mongo_game['is_finished'] = True
        finished_games.append(data)
    return finished_games


def get_player_with_most_kills(finished_games_data):
    players_kills = []
    to_update = []

    for game_data in finished_games_data:

        mongo_game = game_data.get('mongo_game')
        players_data = mongo_game.get('players_data')

        if not players_data:
            cass_match = game_data.get('cass_match')
            match_id = cass_match.id
            to_update.append(match_id)

            participants = cass_match.participants
            players_data = {}
            for participant in participants:
                summoner = participant.summoner
                try:
                    summoner_name = summoner.name.strip()
                    print(summoner_name)
                except AttributeError:
                    continue
                stats = participant.stats
                kills = stats.kills
                dmg = stats.total_damage_dealt_to_champions
                players_data[summoner_name] = {
                    'kills': kills,
                    'dmg': dmg,
                }
            mongo_game['players_data'] = players_data

        for summoner_name, player_data in players_data.items():
            kills = player_data.get('kills')
            dmg = player_data.get('dmg')
            player_info = {
                'summoner_name': summoner_name,
                'mongo_game': mongo_game,
                'kills': kills,
                'dmg': dmg,
            }
            players_kills.append(player_info)

    # sorted_players = [player for player in
    #                   sorted(players_kills, key=lambda player: (round(player['dmg'], -4), player['kills']), reverse=True)]
    sorted_players = [player for player in
                      sorted(players_kills, key=lambda player: (player['kills'], player['dmg']),
                             reverse=True)]
    for player in sorted_players:
        print(player.get('summoner_name'), player.get('kills'), player.get('dmg'), player.get('mongo_game').get('match_id'))
    player_with_most_kills = sorted_players[0]

    games = {player_data.get('mongo_game').get('match_id'): player_data.get('mongo_game') for player_data in
             sorted_players if player_data.get('mongo_game').get('match_id') in to_update}

    update_top_games(games)
    return player_with_most_kills


def update_top_games(games):
    for match_id, mongo_game in games.items():
        update_game(match_id, mongo_game)

