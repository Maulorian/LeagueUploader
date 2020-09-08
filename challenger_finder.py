from cassiopeia import Region, Queue

from opgg_extractor import OPGGExtractor
from porofessor_manager import PorofessorExtractor

REGIONS_TO_SEARCH = [Region.korea, Region.europe_west]


def find_player():
    for region in REGIONS_TO_SEARCH:
        in_challenger_league = True
        page_nb = 1
        # while in_challenger_league:
        opgg_extractor = OPGGExtractor(region)
        players = opgg_extractor.get_ladder(page_nb)
        for summoner_name in players:
            # summoner = get_summoner(region=region, name=summoner_name)
            # try:
            #     match = summoner.current_match
            # except NotFoundError:
            #     continue

            # print(match)
            opgg_match_data = opgg_extractor.get_match_data(summoner_name)
            if not opgg_match_data:
                continue
            print(opgg_match_data)
            # summoner = get_summoner(region=region, name=summoner_name)
            # match = summoner.current_match
            # print(match.duration)
            opgg_players_data = opgg_match_data.get('players_data')
            player_data = opgg_players_data.get(summoner_name)
            rank = player_data.get('rank')
            if 'Challenger' not in rank:
                # in_challenger_league = False
                print(f'{summoner_name} is only {rank}')
                break

            if opgg_match_data.get('match_type') != Queue.ranked_solo_fives:
                continue
            porofessor_extractor = PorofessorExtractor(region)
            porofessor_match_data = porofessor_extractor.get_match_data(summoner_name)
            print(porofessor_match_data)
            if not porofessor_match_data:
                continue
            duration = porofessor_match_data.get('duration')
            if not duration:
                continue

            print(f'[{__name__.upper()}] - Duration={duration}')

            just_started = duration.seconds - 2 * 60 - 3.5*60 < 0
            if not just_started:
                continue

            porofessor_players = porofessor_match_data.get('players')
            players_data = {}
            for player_name in porofessor_players:
                players_data[player_name] = opgg_players_data[player_name]

            match_data = {'summoner_name': summoner_name, 'players_data': players_data, 'region': region}

            return match_data

            # page_nb += 1