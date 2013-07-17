from myhandler import BranchGeneral
from scoredata import Player
from util import long_ago

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

def color_from_played(G):
    if G >= 5000:
        return '#ff9999'
    if G >= 3900:
        return '#ffcccc'
    if G >= 3000:
        return '#ffffcc'
    if G >= 2200:
        return '#ccccff'
    if G >= 1500:
        return '#ccffcc'
    if G >= 900:
        return '#cccccc'
    return '#ffffff'

class BranchRatingRankingPage(BranchGeneral):

    def action_name(self):
        return 'constructing rating ranking'

    def get_real(self, bid):
        played = max(self.get_int('games', 1000), 400)
        limit = min(max(self.get_int('limit', 300), 50), 500)
        players = filter(lambda player: played <= player.played,
            Player.all().filter('bid =', bid).filter('rated', True).order('-last_visit').fetch(limit))
            #Player.all().filter('bid =', bid).filter('rated', True).filter('last_visit >', long_ago).order('-last_visit').fetch(limit))
        players.sort(key=lambda player: -player.curR)
        for i in range(len(players)):
            players[i].rating_color = color_from_rating(players[i].curR)
            players[i].played_color = color_from_played(players[i].played)
        content = {
          'bname': self.branch_name(),
          'games': played,
          'players': players,
        }
        self.write_out('branch/player/rating', content)
