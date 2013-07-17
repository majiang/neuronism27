from myhandler import BranchGeneral, MyHandler
from datetime import date
from scoredata import SumScore, get_ss, SpanScore
from google.appengine.api import mail, users
from userdata import Branch

class BranchReportPage(BranchGeneral):
    def get_real(self, bid):
        year = self.get_int('year')
        month = self.get_int('month')
        try:
            first_day_of_month = date(year, month, 1)
            if month == 12:
                first_day_of_next = date(year + 1, 1, 1)
            else:
                first_day_of_next = date(year, month + 1, 1)
        except:
            return
        # get ranking data
        sss = SumScore.all().filter('bid =', bid).filter('term_end =', True).filter('date >=', first_day_of_month).filter('date <', first_day_of_next).order('date').fetch(1000)
        result = []
        for ss_e in sss:
            ss_s = get_ss(bid, ss_e.pid, ss_e.gfp - 20)
            if ss_s is None:
                continue
            result.append(SpanScore(ss_s, ss_e))
        result.sort(key=lambda ss: -ss.score)
        # report result
        attatchment = ''
        #player,score,point,--,-,+,++,r-point,1,2,3,4,date,#,R-bef,R-aft'
        for r in result:
            attatchment += '%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%d,%f,%f\n' % (
                r.pid, r.score,
                r.point, r.point_summary[0], r.point_summary[1], r.point_summary[2], r.point_summary[3],
                r.rp_gain, r.rank[0], r.rank[1], r.rank[2], r.rank[3],
                r.finish_date, r.games, r.rating_bef, r.rating_aft
            )
        branch = Branch.all().filter('bid =', bid).filter('mstr =', False).get()
        sender = branch.name + " <%s>" % users.get_current_user().email()
        neuron = 'stneuron@nifty.com'
        developer = 'r.97all@gmail.com'
        subject = 'NeuronISM: %d-%d score of %s' % (year, month, branch.name)
        body = 'see attachment.'
        attachments = [('%d-%d-%s.csv' % (year, month, branch.name), attatchment)]
        mail.send_mail(
            sender=sender,
            to=neuron,
            subject=subject,
            body=body,
            attachments=attachments
        )

class AdminAutoReportPage(MyHandler):

    def get(self):
        t = date.today()
        year = t.year
        month = t.month
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        for branch in Branch.all().filter('mstr =', False):
            self.process(branch, year, month)

    def process(self, branch, year, month):
        try:
            first_day_of_month = date(year, month, 1)
            if month == 12:
                first_day_of_next = date(year + 1, 1, 1)
            else:
                first_day_of_next = date(year, month + 1, 1)
        except:
            return
        sss = SumScore.all().filter('bid =', branch.bid).filter('term_end =', True).filter('date >=', first_day_of_month).filter('date <', first_day_of_next).order('date').fetch(1000)
        result = []
        for ss_e in sss:
            ss_s = get_ss(branch.bid, ss_e.pid, ss_e.gfp - 20)
            if ss_s is None:
                continue
            result.append(SpanScore(ss_s, ss_e))
        result.sort(key=lambda ss: -ss.score)
        # report result
        attatchment = ''
        #player,score,point,--,-,+,++,r-point,1,2,3,4,date,#,R-bef,R-aft'
        for r in result:
            attatchment += '%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%d,%f,%f\n' % (
                r.pid, r.score,
                r.point, r.point_summary[0], r.point_summary[1], r.point_summary[2], r.point_summary[3],
                r.rp_gain, r.rank[0], r.rank[1], r.rank[2], r.rank[3],
                r.finish_date, r.games, r.rating_bef, r.rating_aft
            )
        sender = branch.name + ' <admin@neuron-ism.appspotmail.com>'
        neuron = 'Neuron Backup <neuron.honbu+backup@gmail.com>'
        stneuron = 'Neuron Central <stneuron@nifty.com>'
        #developer = 'r.97all@gmail.com'
        subject = 'NeuronISM: %d-%d score of %s' % (year, month, branch.name)
        body = 'see attachment.'
        attachments = [('%d-%d-%s.csv' % (year, month, branch.name), attatchment)]
        mail.send_mail(
                sender=sender,
                to=[branch.user.email(), neuron, stneuron],
                subject=subject,
                body=body,
                attachments=attachments
            )

