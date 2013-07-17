from myhandler import ViewerGeneral
from scoredata import Player
from userdata import Branch
from branch_player import MatchScore, WholeScore

class ViewerScoreDefaultPage(ViewerGeneral):

    def get_real(self, viewer):
        'viewer provides access for viewer.(bid, pid)'
        bid = viewer.bid
        pid = viewer.pid
        player = Player.all().filter('bid =', bid).filter('pid =', pid).get()
        branch_name = Branch.all().filter('bid =', bid).filter('mstr =', False).get().name
        lines = player.detail.strip().split('\n')
        n = len(lines)
        limit = min(max(self.get_int('limit'), 100), 10000)
        if n <= limit:
            limit = n
        lines = lines[-limit:]
        scores = []
        n -= limit
        for line in lines:
            scores.append(MatchScore(line, n+1))
            n += 1
        whole_score = WholeScore(scores)
        self.write_out('viewer/player', {
          'played': n,
          'bname': branch_name,
          'pid': pid,
          'scores': list(reversed(scores)),
          'whole_score': whole_score,
          'visit_history': False,
          'detail': True,
          'after_float': self.get_int('float', 0),
          'viewer_id': viewer.key().id()
        })
