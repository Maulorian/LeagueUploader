import opgg_manager
import spectator
import upload_manager

# spectator.spectate('ArribaSBuyakote')

challenger = opgg_manager.get_challenger_player(from_ladder=False)
if challenger:
    spectator.spectate(challenger)
