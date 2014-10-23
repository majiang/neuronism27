from webapp2 import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from myhandler import MyHandler
import userdata
from google.appengine.api.users import create_logout_url
from scoredata import count_unprocessed, BranchCounter
from datetime import datetime

#def system_status(bid=None):
#    return count_unprocessed(bid)

class IndexPage(MyHandler):

    def get(self):
        # render menu
        self.write_out('index/header', {'logout_url': create_logout_url('/'), 'system_datetime': datetime.today()})
        master = None
        for master in self.master():
            self.write_out('index/master', {
              'unp': count_unprocessed()
            })
            break
        branch = self.branch()
        # TODO: rewrite using bid -> getbranch
        if branch:
            bid = branch[0].bid
            bname = branch[0].name
            branchcounter = BranchCounter.all().filter('bid =', bid).order('-date').get()
            if branchcounter:
                played = branchcounter.games
                last_game = branchcounter.date
            else:
                played = 0
                last_game = datetime(2000, 1, 1)
            self.write_out('index/branch', {
              'unp': count_unprocessed(bid),
              'master': master,
              'bname': bname,
              'played': played,
              'last_game': last_game
            })
        viewers = self.viewer()
        if viewers:
            self.write_out('index/viewer', {
              'viewers': [{
                'id': v.key().id(),
                'bid': v.bid,
                'bname': userdata.Branch.all().filter('bid =', v.bid).filter('mstr =', False).get().name,
                'pid': v.pid
              } for v in viewers]
            })
        self.write_out('index/guest', {
          'branches': [
            b for b in userdata.Branch.all().filter('mstr =', False).order('bid')
          ]
        })
        self.write_out('index/footer', {})


if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
        ('/.*', IndexPage),
    ], debug=True))
