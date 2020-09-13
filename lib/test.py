import cassiopeia
from cassiopeia import Region

from lib.managers.league_manager import close_game
from lib.managers.replay_api_manager import get_player_data, get_player_skin, get_players_data, get_player_position
from lib.managers.thumbnail_manager import save_champion_splashart
from lib.managers.upload_manager import add_video_to_queue

# add_video_to_queue({})
# close_game()
# print(get_player_data('Syndra').get('skinName'))
# cassiopeia.set_default_region(Region.europe_west)
# print(get_player_skin('Syndra'))
# save_champion_splashart('Ashe', get_player_skin('Ashe'))
print(get_player_position('Caitlyn'))