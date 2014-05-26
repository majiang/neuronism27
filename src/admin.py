from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.users import is_current_user_admin
from myhandler import MyHandler
from userdata import Master, Branch
from scoredata import BranchCounter, BranchState, SumScore, Player, QueueStopper
from google.appengine.api import mail
import logging
from branch_player import MatchScore, WholeScore

class PlayerNotFoundException(Exception):
    def __init__(self, bid, pid):
        logging.error('Player %d-%d not found.' % (bid, pid))

class PlayerPlayedLessThanSpecifiedException(Exception):
    def __init__(self, bid, pid, gfp, actual):
        logging.error('Player %d-%d played %d games < %d' % (bid, pid, actual, gfp))

class AdminPage(MyHandler):
    def get_point_dist(self, bid, pid, gfp):
        player = Player.all().filter('bid =', bid).filter('pid =', pid).get()
        if player is None:
            raise PlayerNotFoundException(bid, pid)
        if gfp == 0:
            return [0 for i in range(12)]
        scores = []
        for line in player.detail.strip().split('\n'):
            scores.append(MatchScore(line, 0))
            if len(scores) == gfp:
                return WholeScore(scores).point_dist
        raise PlayerPlayedLessThanSpecifiedException(bid, pid, gfp, len(scores))

    def find_ss(self, bidx, pid, gfp):
        'Stub: lexicographically next data of SS.'
        bid = [1, 2, 3, 4, 5, 6, 1000][bidx]
        ret = SumScore.all().filter(
            'bid =', bid).filter(
            'pid =', pid).filter(
            'gfp >', gfp).order('gfp').get()
        if not (ret is None):
            return ret
        # advance to next player
        ret = SumScore.all().filter('bid =', bid).filter('pid >', pid).order('pid').order('gfp').get()
        if not (ret is None):
            return ret
        # advance to next branch
        bidx += 1
        if 7 <= bidx:
            return None
        bid = [1, 2, 3, 4, 5, 6, 1000][bidx]
        return SumScore.all().filter('bid =', bid).order('pid').order('gfp').get()
        

    def ss_fix(self):
        bidx = self.get_int('bidx', 0)
        if 7 <= bidx:
            return self.write_out('admin/iterate_ss', {'finished': True})
        ss = self.find_ss(
            bidx,
            self.get_int('pid', 0),
            self.get_int('gfp', -1)
        )
        if ss is None:
            self.response.out.write('find_ss returned None. Terminating process.')
            return logging.debug('find_ss returned None. Terminating process.')
        logging.debug('processing SS %d %d %d' % (ss.bid, ss.pid, ss.gfp))
        # start process
        try:
            ss.point_dist = self.get_point_dist(ss.bid, ss.pid, ss.gfp)
            ss.put()
            #return logging.error('ss.put failed. Terminating process.')
        except:
            self.response.out.write('get_point_dist failed. Terminating process.')
            logging.debug('get_point_dist failed. Terminating process.')
            raise
        # end process
        if ss.bid != [1, 2, 3, 4, 5, 6, 1000][bidx]:
            bidx += 1
        self.write_out('admin/iterate_ss', {
            'next_url': ('/admin?iterate_ss=yes&bidx=%d&pid=%d&gfp=%d' % (bidx, ss.pid, ss.gfp)),
            'bidx': bidx,
            'bid': ss.bid,
            'pid': ss.pid,
            'gfp': ss.gfp
        })

    # temporary page not in use.
    # good sample for player batch operation.
    def search_rated(self):
        bIDs = [1, 2, 3, 1000]
        bidx = self.get_int('bidx', 0)
        pid = self.get_int('pid', 0)
        bid = bIDs[bidx]
        player = Player.all().filter('bid =', bid).filter('pid >', pid).order('pid').get()
        if player is None:
            bidx += 1
            try:
                bid = bIDs[bidx]
            except:
                return self.write_out('admin/search_rated', {'finished': True})
            pid = 0
            player = Player.all().filter('bid =', bid).filter('pid >', pid).order('pid').get()
        player.rated = 400 <= player.played
        player.put()
        next_url = '/admin?search_rated=yes&bidx=%d&pid=%d' % (bidx, player.pid)
        self.write_out(
          'admin/search_rated', {
            'next_url': next_url,
            'current_bid': bid,
            'current_pid': pid})

    def quit_master(self, user):
        for master in Master.all().filter('uid =', user.user_id()):
            master.delete()
        return

    def reset_branch(self):
        target = self.get_int('target')
        i = 0
        try:
            for cls in [BranchCounter, BranchState, SumScore, Player]:
                for entity in cls.all().filter('bid =', target):
                    entity.delete()
                    i += 1
        except:
            logging.debug('deleted %d entities' % i)
            return
        else:
            mail.send_mail(
              'admin@neuron-ism.appspotmail.com', 'r.97all@gmail.com',
              'finish reset', 'finish resetting.'
            )
        return self.redirect('/')

    def reduce_BC(self):
        # 349180
        target = self.get_int('target')
        bc = BranchCounter.get_by_id(target)
        bc.customers = ''
        bc.put()
        return

    def post(self):
        if self.get_str('announce') != 'body':
            return self.redirect('/')
        try:
            addresses = [branch.user.email() for branch in Branch.all().filter('mstr =', False)] + ['stneuron@nifty.com', 'neuron-ikeya@i.softbank.jp', 'neuron.honbu@gmail.com']
            for address in addresses:
                self.mail_from_admin(address, 'NeuronISM: ' + self.get_str('subject'), self.get_str('body'))
        except:
            self.write_raw('fail')
        else:
            self.write_raw('success to email: %s' % addresses)

    def arbitrary(self):
        ss = SumScore.all().filter('bid =', 1).filter('pid =', 24).filter('gfp =', 40).get()
        ss.point_dist = [1,2,2,4,3,5,7,4,4,5,2,1]
        ss.put()

    def get(self):
        if not is_current_user_admin():
            return self.redirect('/')
        if self.get_str('arbitrary'):
            return self.arbitrary()
        if self.get_str('quit'):
            return self.quit_master(self.user())
        if self.get_str('announce'):
            return self.write_out('admin/announcement/compose', {})
        #if self.get_str('reset_branch'):
        #    return self.reset_branch()
        if self.get_str('reduce'):
            return self.reduce_BC()
        #if self.get_str('search_rated'):
        #    return self.search_rated()
        if self.get_str('iterate_ss') == 'yes':
            return self.ss_fix()
        if self.get_str('stop_all') == 'yes':
            if QueueStopper.all().get() is None:
                QueueStopper().put()
            return
        if self.get_str('start_all') == 'yes':
            for s in QueueStopper.all():
                s.delete()
        user = self.user()
        master = Master.all().filter('uid =', user.user_id()).get()
        if master is None:
            Master(user=user, uid=user.user_id()).put()
        self.redirect('/')

if __name__ == '__main__':
    run_wsgi_app(WSGIApplication([
      ('/admin.*', AdminPage),
    ], debug=True))
