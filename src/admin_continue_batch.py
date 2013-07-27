import logging
from scoredata import QueueScore, QueueStopper
from StringIO import StringIO
from score import get_players, get_points
from dbmanager import add_game
from google.appengine.ext.webapp import WSGIApplication
from datetime import datetime, timedelta
from util import long_ago
from myhandler import MyHandler
#from google.appengine.runtime import DeadlineExceededError

def get_qs():
    if QueueStopper.all().get():
        logging.debug('input is stopped.')
        return None
    qs = QueueScore.all().filter('game_date >', long_ago).order('game_date').order('input_date').get()
    if qs:
        return qs
    return QueueScore.all().order('game_date').order('input_date').get()


class AdminContinueBatchPage(MyHandler):

    def get(self):
        deadline = datetime.today()
        qs = get_qs()
        if qs is None:
            self.response.out.write('no data to process.')
            return
        if 'X-AppEngine-Cron' in self.request.headers:
            deadline += timedelta(minutes=5)
        else:
            deadline += timedelta(seconds=5)
        bid = qs.bid
        date = qs.game_date
        reader = StringIO(qs.body)
        reader.seek(qs.pos)
        i = 0
        while i < 1000:
            if deadline < datetime.today():
                break
            line = reader.readline()
            if not line:
                qs.delete()
                logging.debug('input %d games of %s for %d. current score in the queue finished.' % (i, date, bid))
                self.response.out.write('input %d games of %s for %d. current score in the queue finished.' % (i, date, bid))
                return
            dat = line.strip().split(',')
            players = get_players(dat[:4])
            points = get_points(dat[4:])
            try:
                add_game(bid, date, players, points)
            except Exception, e:
                logging.debug('input %d games of %s for %d and caught %s when inputting line"%s"' % (i, date, bid, repr(e), line))
                qs.put()
                self.mail_from_admin('r.97all@gmail.com', 'error report',
                    'input %d games of %s for %d and caught %s when inputting line"%s"' % (i, date, bid, repr(e), line)
                )
                QueueStopper().put()
                break
            i += 1
            qs.pos = reader.tell()
        qs.put()
        logging.debug('input %d games of %s for %d. current score in the queue continues.' % (i, date, bid))
        self.response.out.write('input %d games of %s for %d. current score in the queue continues.' % (i, date, bid))

app = WSGIApplication([
      ('/admin/continue_batch', AdminContinueBatchPage)
    ], debug=True)
