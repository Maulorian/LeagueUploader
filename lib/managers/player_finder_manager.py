import datapipelines
from cassiopeia import cassiopeia

from lib.managers import vpn_manager
from lib.managers.recorded_games_manager import get_recorded_games, update_games, delete_games
from lib.managers.riot_api_manager import get_current_game_version
from lib.utils import log_name

VERSION = 'version'

PLAYERS_DATA = 'players_data'

MATCH_ID = 'match_id'

REGION = 'region'

FINISHED = 'finished'

GAMES_TO_KEEP = 20

@log_name
def get_finished_recorded_games():
    finished_games = []
    vpn_manager.disconnect()
    games = get_recorded_games()
    version = get_current_game_version()

    deprecated_matches = []
    for i, mongo_game in enumerate(games):
        match_id = mongo_game.get(MATCH_ID)
        region = mongo_game.get(REGION)
        data = {
            'mongo_game': mongo_game
        }

        finished = mongo_game.get(FINISHED)
        game_version = mongo_game.get(VERSION)
        if game_version != version:
            print(f'{match_id} on patch {game_version} is deprecated')
            deprecated_matches.append(match_id)
            continue
        if not finished:
            try:
                cass_match = cassiopeia.get_match(match_id, region=region)
                is_remake = cass_match.is_remake
                print(f'[{i}/{len(games)}] Game {match_id} {region} is finished')

            except datapipelines.common.NotFoundError:
                print(f'[{i}/{len(games)}] Game {match_id} not finished')
                continue
            data['cass_match'] = cass_match

        # print(f'[{i}/{len(games)}] Game {match_id} {region} is finished')
        mongo_game[FINISHED] = True
        finished_games.append(data)

    delete_games(deprecated_matches)
    return finished_games


@log_name
def get_player_with_most_kills(finished_games_data):
    players_kills = []
    to_update = []

    for game_data in finished_games_data:

        mongo_game = game_data.get('mongo_game')
        players_data = mongo_game.get(PLAYERS_DATA)

        if not players_data:
            cass_match = game_data.get('cass_match')
            match_id = cass_match.id
            to_update.append(match_id)

            participants = cass_match.participants
            players_data = {}
            for participant in participants:
                summoner = participant.summoner
                try:
                    summoner_id = summoner.id
                except AttributeError:
                    continue
                stats = participant.stats
                kills = stats.kills
                assists = stats.assists
                dmg = stats.total_damage_dealt_to_champions
                players_data[summoner_id] = {
                    'side': participant.side.value,
                    'kills': kills,
                    'dmg': dmg,
                    'assists': assists
                }
            mongo_game[PLAYERS_DATA] = players_data

        for summoner_id, player_data in players_data.items():
            ally_assists = sum(pl.get('assists') for player_id, pl in players_data.items() if player_id != summoner_id and pl.get('side') == player_data.get('side'))
            kills = player_data.get('kills')
            dmg = player_data.get('dmg')
            player_info = {
                'summoner_id': summoner_id,
                'mongo_game': mongo_game,
                'kills': kills,
                'dmg': dmg,
                'ally_assists': ally_assists
            }
            players_kills.append(player_info)
    sorted_players = [player for player in
                      sorted(players_kills, key=lambda player: (player['kills'], -player['ally_assists']),
                             reverse=True)]
    # sorted_players = [player for player in
    #                   sorted(players_kills, key=lambda player: (player['kills'], player['dmg']),
    #                          reverse=True)]
    for player in sorted_players:
        print(player.get('summoner_id'), player.get('kills'), player.get('dmg'), player.get('ally_assists'),
              player.get('mongo_game').get(MATCH_ID))
    player_with_most_kills = sorted_players[0]
    for sorted_player in sorted_players[:25]:
        print(sorted_player.get('kills'), sorted_player.get('dmg'))
    games = [player_data.get('mongo_game') for player_data in
             sorted_players if player_data.get('mongo_game').get(MATCH_ID) in to_update]

    update_games(games)
    return player_with_most_kills
