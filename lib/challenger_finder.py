from cassiopeia import Region, Queue

from lib.externals_sites import opgg_extractor, porofessor_extractor

REGIONS_TO_SEARCH = [Region.korea.value, Region.europe_west.value]
# REGIONS_TO_SEARCH = [Region.europe_west, Region.korea]

ROLE_INDEXES = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
interests = ['Vayne', 'Irelia', 'Fiora', 'Yasuo']


def get_final_players_data(porofessor_players, opgg_players_data):
    players_data = {}
    for player_name in porofessor_players:
        players_data[player_name] = opgg_players_data[player_name]
    return players_data


# def find_spectate_tab_player():
#     already_searched_players = set()
#     no_ranked_enough = set()
#     while True:
#
#         for region in REGIONS_TO_SEARCH:
#             players = opgg_extractor.spectate_tab(region)
#             player_matches = {}
#             for summoner_name in players:
#                 if summoner_name in no_ranked_enough:
#                     continue
#                 opgg_match_data = opgg_extractor.get_match_data(summoner_name, region)
#                 if not opgg_match_data:
#                     continue
#
#                 opgg_players_data = opgg_match_data.get('players_data')
#                 for player in opgg_players_data:
#                     already_searched_players.add(player)
#
#                 player_data = opgg_players_data.get(summoner_name)
#                 rank = player_data.get('rank')
#                 print(f'rank: {rank}')
#                 if 'Challenger' not in rank:
#                     no_ranked_enough.add(summoner_name)
#                     continue
#
#                 if opgg_match_data.get('match_type') != Queue.ranked_solo_fives:
#                     print(f"Not a ranked: {opgg_match_data.get('match_type')}")
#                     continue
#
#                 porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)
#
#                 if not porofessor_match_data:
#                     continue
#
#                 duration = porofessor_match_data.get('duration')
#                 if duration is None:
#                     continue
#
#                 print(f'[{__name__.upper()}] - Duration={duration}')
#
#                 just_started = duration.seconds - 2 * 60 - 3.5 * 60 < 0
#                 if not just_started:
#                     continue
#
#                 porofessor_players = porofessor_match_data.get('players')
#                 players_data = get_final_players_data(porofessor_players, opgg_players_data)
#                 player_position = list(players_data.keys()).index(summoner_name)
#                 role = ROLE_INDEXES[player_position % 5]
#                 if role == 'support':
#                     continue
#                 match_data = {'summoner_name': summoner_name, 'players_data': players_data, 'region': region, 'rank': rank, 'role' : role, 'player_position': player_position}
#                 player_matches[summoner_name] = match_data
#             print(player_matches)
#             for i in player_matches:
#                 for p in i.get('players_data'):
#                     print(p)
#             if len(player_matches):
#                 return player_matches[0]


def find_ladder_player():
    already_searched_players = set()
    for region in REGIONS_TO_SEARCH:
        # while in_challenger_league:
        players = opgg_extractor.get_ladder(region)
        for summoner_name in players:
            if summoner_name in already_searched_players:
                print(f'{summoner_name} already checked')
                continue

            opgg_match_data = opgg_extractor.get_match_data(summoner_name, region)

            if not opgg_match_data:
                continue

            opgg_players_data = opgg_match_data.get('players_data')
            for player in opgg_players_data:
                already_searched_players.add(player)

            player_data = opgg_players_data.get(summoner_name)
            rank = player_data.get('rank')
            if 'Challenger' not in rank:
                print(f'{summoner_name} is only {rank}')
                break

            if opgg_match_data.get('match_type') != Queue.ranked_solo_fives:
                print(f"Not a ranked")
                continue

            porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)

            if not porofessor_match_data:
                continue

            already_started = porofessor_match_data.get('already_started')
            if already_started:
                continue

            # print(f'[{__name__.upper()}] - Duration={duration}')

            # just_started = duration.seconds - 2 * 60 - 3.5*60 < 0
            # if not just_started:
            #     continue
            porofessor_players = porofessor_match_data.get('players')

            players_data = get_final_players_data(porofessor_players, opgg_players_data)
            for player_name, player_data in players_data.items():
                print(player_name, player_data)
                player_position = list(players_data.keys()).index(player_name)
                role = ROLE_INDEXES[player_position % 5]
                player_data['player_position'] = player_position
                player_data['role'] = role

            for champion_skill in interests:
                for player_name, player_data in players_data.items():
                    if player_data['champion'] == champion_skill:
                        match_data = {'summoner_name': player_name, 'players_data': players_data, 'region': region}
                        return match_data

            match_data = {'summoner_name': summoner_name, 'players_data': players_data, 'region': region}
            return match_data
