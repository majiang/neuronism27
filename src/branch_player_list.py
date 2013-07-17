from myhandler import BranchGeneral
from scoredata import Player

class BranchPlayerListPage(BranchGeneral):

    def action_name(self):
        return 'getting player list'

    def get_real(self, bid):
        start = self.get_int('from')
        limit = self.get_int('limit')
        start = max(start, 0)
        limit = min(max(limit, 50), 300)
        players = Player.all().filter('bid =', bid).filter('pid >', start).order('pid').fetch(limit)
        n = len(players)
        content = {
          'bname': self.branch_name(),
          'players': players,
          'page_url': 'list',
          'navigation': True,
          'prev_param': 'from=%d&limit=%d' % (start - limit, limit),
          'next_param': 'from=%d&limit=%d' % (players[n-1].pid, limit)
        }
        self.write_out('branch/player/list', content)
