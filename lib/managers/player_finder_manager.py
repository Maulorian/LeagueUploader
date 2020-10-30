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
        # finished = False
        if not finished:
            try:
                cass_match = cassiopeia.get_match(match_id, region=region)
                is_remake = cass_match.is_remake
                print(f'[{i}/{len(games)}] Game {match_id} {region} is finished')

            except datapipelines.common.NotFoundError:
                print(f'[{i}/{len(games)}] Game {match_id} not finished')
                continue
            data['cass_match'] = cass_match
            mongo_game[FINISHED] = True

        # print(f'[{i}/{len(games)}] Game {match_id} {region} is finished')
        finished_games.append(data)

    delete_games(deprecated_matches)
    return finished_games


def get_sorting(player_data, sorting_factors):
    return tuple(player_data.get(sorting_factor) for sorting_factor in sorting_factors)


class NotEnoughPlayerError(Exception):
    pass


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
                deaths = stats.deaths
                dmg = stats.total_damage_dealt_to_champions
                solo_kills = sum(1 for kill_event in participant.timeline.champion_kills if
                                 len(kill_event.assisting_participants) == 0)
                kda = (kills + assists) / max(deaths, 1)
                players_data[summoner_id] = {
                    'side': participant.side.value,
                    'kills': kills,
                    'dmg': dmg,
                    'solo_kills': solo_kills,
                    'assists': assists,
                    'kda': kda,
                    'deaths': deaths,
                    'match_id': match_id
                }
            mongo_game[PLAYERS_DATA] = players_data

        for summoner_id, player_data in players_data.items():
            kills = player_data.get('kills')
            dmg = player_data.get('dmg')
            solo_kills = player_data.get('solo_kills')
            kda = player_data.get('kda')
            assists = player_data.get('assists')
            deaths = player_data.get('deaths')
            player_info = {
                'summoner_id': summoner_id,
                'mongo_game': mongo_game,
                'kills': kills,
                'dmg': dmg,
                'solo_kills': solo_kills,
                'assists': assists,
                'kda': kda,
                'deaths': deaths,
            }
            players_kills.append(player_info)
    sorting_factors = ['kills', 'solo_kills', 'dmg']
    sorting_factors = ['solo_kills', 'kills', 'dmg']
    # sorting_factors = ['kda', 'kills']
    sorted_players = sorted(players_kills, key=lambda p: get_sorting(p, sorting_factors), reverse=True)
    sorted_players = [player for player in sorted_players if player.get('kills') >= 15]

    try:
        for player in sorted_players[:20]:
            print(player.get('mongo_game').get('match_id'))
            print(', '.join([f'{sorting_factor}={player.get(sorting_factor)}' for sorting_factor in sorting_factors]))

        player_with_most_kills = sorted_players[0]

    except IndexError:
        raise NotEnoughPlayerError
    finally:
        games = [player_data.get('mongo_game') for player_data in
                 sorted_players if player_data.get('mongo_game').get(MATCH_ID) in to_update]
        update_games(games)

    return player_with_most_kills
