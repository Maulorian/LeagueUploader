import datapipelines
from cassiopeia import Region, Queue, get_summoner, get_current_match

from lib.extractors import opgg_extractor, porofessor_extractor
from lib.extractors.porofessor_extractor import PorofessorNoResponseException

REGIONS_TO_SEARCH = [Region.korea.value, Region.europe_west.value]
# REGIONS_TO_SEARCH = [Region.europe_west.value, Region.korea.value]

ROLE_INDEXES = ['Top', 'Jgl', 'Mid', 'Bot', 'Sup']
interests = ['Samira', 'Vayne', 'Irelia', 'Fiora', 'Yasuo']


def get_final_players_data(porofessor_players, opgg_players_data):
    players_data = {}
    for player_name in porofessor_players:
        if player_name not in opgg_players_data.keys():
            return
        players_data[player_name] = opgg_players_data[player_name]
    return players_data




def find_ladder_player():
    already_searched_players = set()
    for region in REGIONS_TO_SEARCH:
        # while in_challenger_league:
        players = opgg_extractor.get_ladder(region)
        for index, summoner_name in enumerate(players):
            if summoner_name in already_searched_players:
                # print(f'{summoner_name} already checked')
                continue
            print(f'[{index}/{len(players)}] - Checking {summoner_name}')
            # summoner = get_summoner(name=summoner_name, region=region)
            #
            # try:
            #     current_match = get_current_match(summoner, region=region)
            # except datapipelines.common.NotFoundError:
            #     continue

            # duration = current_match.duration
            # print(f'{duration=}')
            #
            # if duration.days == 0 and duration.seconds > 0:
            #     continue
            # print(f'valid duration: {current_match.duration}')
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
            try:
                porofessor_match_data = porofessor_extractor.get_match_data(summoner_name, region)
            except PorofessorNoResponseException:
                return
            if not porofessor_match_data:
                continue

            already_started = porofessor_match_data.get('already_started')
            if already_started:
                continue

            porofessor_players = porofessor_match_data.get('players')

            players_data = get_final_players_data(porofessor_players, opgg_players_data)
            if not players_data:
                continue

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