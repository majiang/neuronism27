from myhandler import BranchGeneral
from scoredata import Player

class BranchPlayerActivePage(BranchGeneral):

    def action_name(self):
        return 'getting active player list'

    def get_real(self, bid):
        limit = self.get_int('limit')
        limit = max(min(max(limit, 0), 300), 50)
        players = Player.all().filter('bid =', bid).order('-prev_visit').fetch(limit)
        content = {
          'bname': self.branch_name(),
          'players': players,
          'page_url': 'active',
          'navigation': False,
        }
        self.write_out('branch/player/active', content)
