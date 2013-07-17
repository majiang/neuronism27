from myhandler import MasterGeneral, BranchGeneral
from userdata import Branch
from scoredata import BranchState, BranchCounter

class BranchStatsPage:

    def show_stats(self, bid):
        if self.get_str('detail') == 'yes':
            return self.show_detail(bid)
        bname = Branch.all().filter('bid =', bid).filter('mstr =', False).get().name
        played = BranchState.all().filter('bid =', bid).get().counter.games
        stats = BranchCounter.all().filter('bid =', bid).order('-date').fetch(36)
        colors = 'bfbf00#50fd30#05dc9b#1675f2#7516f2#dc059b#fd5030'.split('#')
        games_stat = [{
            'color': colors[p.date.weekday()],
            'date': p.date,
            'games': (p.games - q.games),
          } for (p, q) in zip(stats[:-1], stats[1:])
        ]
        dates = [gs['date'] for gs in games_stat]
        self.write_out('master/branch_stat', {
          'bname': bname, 'played': played, 'games_stat': games_stat,
          'min_date': min(dates), 'max_date': max(dates)
        })

    def show_detail(self, bid):
        bname = Branch.all().filter('bid =', bid).filter('mstr =', False).get().name
        played = BranchState.all().filter('bid =', bid).get().counter.games
        stats = BranchCounter.all().filter('bid =', bid).order('-date').fetch(141)
        colors = 'bfbf00#50fd30#05dc9b#1675f2#7516f2#dc059b#fd5030'.split('#')
        dow_names = 'Monday,Tuesday,Wednesday,Thursday,Friday,SATURDAY,SUNDAY'.split(',')
        detail_stat = [{'dow': dow_names[i], 'color': colors[i], 'stats': []} for i in range(7)]
        week_stat = {'dow': 'WEEK', 'color': '000000', 'stats': []}
        processed = 0
        for (p, q) in zip(stats[:-1], stats[1:]):
            if processed == 0:
                week_stat['stats'].append({
                    'to_date': p.date,
                    'games': p.games
                })
            elif processed == 6:
                lastindex = len(week_stat['stats']) - 1
                week_stat['stats'][lastindex]['games'] -= q.games
                week_stat['stats'][lastindex]['from_date'] = p.date
                week_stat['stats'][lastindex]['visualize'] = 'l' * int(week_stat['stats'][lastindex]['games'] / 7.0)
            dow = p.date.weekday()
            detail_stat[dow]['stats'].append({
                'date': p.date,
                'games': (p.games - q.games),
                'visualize': 'l' * int((p.games - q.games) / 2.5)
            })
            processed = (processed + 1) % 7
        stats = [week_stat] + detail_stat
        for i in range(len(stats)):
            stats[i]['average'], stats[i]['stdev'] = average_stdev_games(stats[i]['stats'])
        self.write_out('master/branch_detail', {
          'bname': bname, 'played': played, 'stats': stats
        })

def average_stdev_games(stat):
    n = 0
    s = 0
    ss = 0
    for g in stat:
        n += 1
        s += g['games']
        ss += g['games'] ** 2
    average = float(s) / n
    stdev = ((float(ss) - s * average) / (n - 1)) ** 0.5
    return average, stdev

class BranchSelfStatsPage(BranchGeneral, BranchStatsPage):

    def get_real(self, bid):
        self.show_stats(bid)


class MasterBranchesPage(MasterGeneral, BranchStatsPage):

    def branch_list(self):
        branches = sorted([branch.additional_info() for branch in Branch.all().filter('mstr =', False)], key=(lambda b: b.bid))
        self.write_out('master/branch_list', {'branches': branches})
        return

    def start_repr(self, bid):
        try:
            user = self.user()
            uid = user.user_id()
            branch = Branch.all().filter('bid =', bid).filter('uid =', uid).get()
            if branch:
                if branch.mstr:
                    self.redirect('/')
                    return
            branch = Branch(
              user=user, uid=uid,
              name='Dummy branch name', bid=bid,
              mstr=True
            )
            branch.put()
            self.redirect('/')
            return
        except:
            self.write_out('master/branch_action/fail', {'bid': bid})

    def quit_repr(self):
        for branch in Branch.all().filter('uid =', self.user().user_id()):
            if branch.mstr:
                branch.delete()
        self.redirect('/master/branch')

    def get_real(self):
        if self.get_str('quit'):
            return self.quit_repr()
        bid = self.get_int('bid')
        if bid < 0:
            return self.branch_list()
        if self.get_str('represent'):
            return self.start_repr(bid)
        else:
            return self.show_stats(bid)
