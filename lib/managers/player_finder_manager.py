import datapipelines
from cassiopeia import cassiopeia, Queue

from lib.managers import vpn_manager
from lib.managers.recorded_games_manager import delete_game, get_recorded_games, update_game

GAMES_TO_KEEP = 20


def get_finished_recorded_games():
    finished_games = []
    vpn_manager.disconnect()
    games = get_recorded_games()
    for i, mongo_game in enumerate(games):
        match_id = mongo_game.get('match_id')
        region = mongo_game.get('region')
        players_data = mongo_game.get('players_data')
        data = {
            'mongo_game': mongo_game
        }
        if players_data is None:
            try:
                match = cassiopeia.get_match(match_id, region=region)

                if match.is_remake:
                    continue
            # except RuntimeError:
            #     continue
            except datapipelines.common.NotFoundError:
                continue
            data['cass_match'] = match
            print(f'[{i}/{len(games)}] Game {match_id} is finished')
        else:
            print(f'[{i}/{len(games)}] Game {match_id} was already checked finished')

        finished_games.append(data)
    return finished_games


def get_player_with_most_kills(finished_games_data):
    players_kills = []
    not_updated_mongo_game = []

    for game_data in finished_games_data:

        mongo_game = game_data.get('mongo_game')
        players_data = mongo_game.get('players_data')

        print(players_data)
        if players_data is None:
            cass_match = game_data.get('cass_match')
            match_id = cass_match.id
            not_updated_mongo_game.append(match_id)
            participants = cass_match.participants
            players_data = {}
            for participant in participants:
                summoner = participant.summoner
                try:
                    summoner_name = summoner.name
                except AttributeError:
                    continue
                kills = participant.stats.kills

                players_data[summoner_name] = {
                    'kills': kills,
                }
            mongo_game['players_data'] = players_data

        for summoner_name, player_data in players_data.items():
            kills = player_data.get('kills')
            players_kills.append({
                'summoner_name': summoner_name,
                'mongo_game': mongo_game,
                'kills': kills
            })

    players_kills_sorted = [player for player in
                            sorted(players_kills, key=lambda player: player.get('kills'), reverse=True)]
    player_with_most_kills = players_kills_sorted[0]

    top_mongo_games = keep_top_games(players_kills_sorted)
    to_update_top_games = top_mongo_games
    # to_update_top_games = {match_id: mongo_game for (match_id, mongo_game) in top_mongo_games.items() if match_id in not_updated_mongo_game}
    update_top_games(to_update_top_games)
    return player_with_most_kills


def update_top_games(games):
    for match_id, mongo_game in games.items():
        update_game(match_id, mongo_game)


def keep_top_games(players_kills_sorted):
    best_mongo_games = {}
    for player_data in players_kills_sorted:
        print(player_data.get('summoner_name'), player_data.get('kills'))

        mongo_game = player_data.get('mongo_game')
        match_id = player_data.get('mongo_game').get('match_id')

        best_mongo_games[match_id] = mongo_game

    mongo_game_ids_delete = list(best_mongo_games.keys())[GAMES_TO_KEEP:]
    print(f'Deleting {len(mongo_game_ids_delete)} games')
    for match_id in mongo_game_ids_delete:
        delete_game(match_id)

    to_keep = list(best_mongo_games.keys())[:GAMES_TO_KEEP]
    return {match_id: mongo_game for (match_id, mongo_game) in best_mongo_games.items() if match_id in to_keep}
