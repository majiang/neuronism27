from myhandler import BranchGeneral
from scoredata import Player

class BranchPlayerDegreePage(BranchGeneral):

    def action_name(self):
        return 'getting player degree list'

    def get_real(self, bid):
        limit = self.get_int('limit')
        limit = max(min(max(limit, 0), 300), 50)
        degree = max(self.get_int('degree'), 0)
        if degree == 0:
            players = Player.all().filter('bid =', bid).order('-degree').fetch(limit)
        else:
            players = Player.all().filter('bid =', bid).filter('degree', degree).order('-achieve_date').fetch(limit)
        content = {
          'bname': self.branch_name(),
          'players': players,
          'page_url': 'degree',
          'navigation': True,
          'prev_param': 'degree=%d&limit=%d' % (degree-1, limit),
          'next_param': 'degree=%d&limit=%d' % (degree+1, limit),
          'order_description': ['degree from high to low', '%d degree: new to old' % degree][degree > 0]
        }
        self.write_out('branch/player/degree', content)
