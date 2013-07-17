from myhandler import BranchGeneral
from scoredata import Player
from datetime import datetime, timedelta


class BranchPlayerInactivePage(BranchGeneral):

    def action_name(self):
        return 'getting inactive player list'

    def get_real(self, bid):
        days = self.get_int('days', 30)
        limit = self.get_int('limit')
        limit = max(min(max(limit, 0), 300), 50)
        players = Player.all().filter('bid =', bid).filter('customer', True).filter('last_visit <', datetime.today() - timedelta(days=days)).order('-last_visit').fetch(limit)
        content = {
          'bname': self.branch_name(),
          'players': players,
          'page_url': 'inactive',
          'navigation': False,
        }
        self.write_out('branch/player/inactive', content)
