from myhandler import BranchGeneral
from datetime import date
from scoredata import SumScore, get_ss, SpanScore

def month_after(year, month):
    return normalize_year_month(year, month + 1)

def month_before(year, month):
    return normalize_year_month(year, month - 1)

def normalize_year_month(year, month):
    return year + (month - 1) // 12, (month - 1) % 12 + 1

class BranchScoreViewPage(BranchGeneral):

    def action_name(self):
        return 'getting recent scores'

    def get_real(self, bid):
        year, month = normalize_year_month(
            self.get_int('from_year', date.today().year),
            self.get_int('from_month', date.today().month) - self.get_int('month', 0)
        )
        from_to_mode = self.get_str('from_to')
        from_cnt_mode = self.get_str('from_cnt')
        if not from_to_mode or from_cnt_mode:
            return self.render_single_month(bid, year, month)
        # construct from_date
        day = self.get_int('from_day', 1)
        from_date = date(year, month, day)
        if from_cnt_mode:
            # from_count_mode
            return self.render_from_count(bid, from_date, max(min(self.get_int('limit', 500), 1000), 100))
        # otherwise: from_to_mode
        to_year = self.get_int('to_year', year)
        to_month = self.get_int('to_month', month)
        to_day = self.get_int('to_day', day)
        return self.render_from_to(bid, from_date, date(to_year, to_month, to_day))

    def render(self, result, navigation=False, prev_param='', next_param=''):
        self.write_out('branch/score/view', {
            'count': len(result),
            'bname': self.branch_name(),
            'result': result,
            'navigation': navigation,
            'prev_param': prev_param,
            'next_param': next_param
        })

    def get_result(self, sss, bid):
        result = []
        for ss_e in sss:
            ss_s = get_ss(bid, ss_e.pid, ss_e.gfp - 20)
            if ss_s is None:
                continue
            result.append(SpanScore(ss_s, ss_e))
        result.sort(key=lambda ss: -ss.score)
        return result

    def get_single_month(self, bid, from_year, from_month):
        to_year, to_month = month_after(from_year, from_month)
        from_date = date(from_year, from_month, 1)
        to_date = date(to_year, to_month, 1)
        return self.get_result(
            SumScore.all().filter('bid =', bid).filter('term_end =', True).filter('date >=', from_date).filter('date <', to_date).order('date').fetch(1000), bid)

    def render_single_month(self, bid, year, month):
        prev = month_before(year, month)
        next = month_after(year, month)
        self.render(
            self.get_single_month(bid, year, month),
            navigation=True,
            prev_param='from_year=%d&from_month=%d' % prev,
            next_param='from_year=%d&from_month=%d' % next
        )

    def get_from_to(self, bid, from_date, to_date):
        return self.get_result(
            SumScore.all().filter('bid =', bid).filter('term_end =', True).filter('date >=', from_date).filter('date <=', to_date).order('date').fetch(1000), bid)

    def render_from_to(self, bid, from_date, to_date):
        self.render(self.get_from_to(bid, from_date, to_date))

    def get_from_count(self, bid, from_date, limit):
        return self.get_result(
            SumScore.all().filter('bid =', bid).filter('term_end =', True).filter('date >=', from_date).order('date').fetch(limit), bid)

    def render_from_count(self, bid, from_date, limit):
        self.render(self.get_from_count(bid, from_date, limit))

