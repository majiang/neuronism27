from google.appengine.ext.webapp import WSGIApplication
from google.appengine.api.users import is_current_user_admin
from myhandler import MyHandler
from userdata import Master, Branch
from scoredata import BranchCounter, BranchState, SumScore, Player, QueueStopper
from google.appengine.api import mail
import logging
from branch_player import MatchScore, WholeScore
from branch_report import AdminAutoReportPage

class AdminPage(MyHandler):

    # temporary method not in use.
    # good sample for player batch operation.
    def search_rated(self):
        bIDs = [1, 2, 3, 1000] # 
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
        # write here code to process player.
        #player.rated = 400 <= player.played
        #player.put()
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

    def post(self):
        if self.get_str('announce') != 'body':
            return self.redirect('/')
        try:
            addresses = [branch.user.email() for branch in Branch.all().filter('mstr =', False)] #+ ['stneuron@nifty.com', 'neuron-ikeya@i.softbank.jp', 'neuron.honbu@gmail.com']
            self.mail_from_admin(addresses, 'NeuronISM: ' + self.get_str('subject'), self.get_str('body'))
        except:
            self.write_raw('fail to email: %s' % addresses)
        else:
            self.write_raw('success to email: %s' % addresses)

    def start_queue(self):
        for s in QueueStopper.all():
            s.delete()
        self.redirect('/')

    def stop_queue(self):
        if QueueStopper.all().get() is None:
            QueueStopper().put()
        self.redirect('/')

    def get(self):
        # authorize first
        if not is_current_user_admin():
            return self.redirect('/')
        # create master account if there's not
        user = self.user()
        master = Master.all().filter('uid =', user.user_id()).get()
        if master is None:
            Master(user=user, uid=user.user_id()).put()

        if self.get_str('quit'):
            return self.quit_master(self.user())
        if self.get_str('announce'):
            return self.write_out('admin/announcement/compose', {})
        if self.get_str('reduce'):
            return self.reduce_BC()
        if self.get_str('iterate_ss') == 'yes':
            return self.ss_fix()
        if self.get_str('stop_all') == 'yes':
            return self.stop_queue()
        if self.get_str('start_all') == 'yes':
            return self.start_queue()
        # add here other functions. default is blank.

app = WSGIApplication([
      ('/admin/report.*', AdminAutoReportPage),
      ('/admin.*', AdminPage)
    ], debug=True)
