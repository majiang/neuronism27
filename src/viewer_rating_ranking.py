from myhandler import ViewerGeneral
from scoredata import Player
from userdata import get_branch

def color_from_rating(R):
    if R >= 2000:
        return '#ffcccc'
    if R >= 1800:
        return '#ffffcc'
    if R >= 1500:
        return '#ccccff'
    if R >= 1200:
        return '#ccffcc'
    return '#cccccc'

def transform_player(player):
    R = player.curR
    return {
            'rating_color': color_from_rating(R),
            'curR': R,
            }

class ViewerRatingRankingPage(ViewerGeneral):

    def action_name(self):
        return 'constructing rating ranking'

    def get_real(self, viewer):
        bid = viewer.bid
        played = max(self.get_int('games', 1000), 400)
        limit = min(max(self.get_int('limit', 150), 50), 500)
        players = sorted((transform_player(player) for player in Player.all().filter('bid =', bid).filter('rated', True).order('-last_visit').fetch(limit)
                      if played <= player.played), key=lambda player: -player['curR'])
        content = {
          'bname': get_branch(bid).name,
          'games': played,
          'players': players,
        }
        self.write_out('viewer/rating', content)
