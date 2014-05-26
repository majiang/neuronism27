from myhandler import BranchGeneral
from scoredata import Player
from datetime import date
from time import strptime
from util import long_ago

class MatchScore:
    'gfp, game_date, point, rank, opps, opp_r, opp_p, R_bef, R_aft'
    def __init__(self, line, i):
        dat = line.strip().split(',')
        self.game_date = date(*strptime(dat[0], '%Y-%m-%d')[0:3])
        self.rank = int(dat[1]) + 1
        self.point = int(dat[2])
        self.score = self.point + [-150, -200, -300, -350][self.rank - 1]
        self.R_bef = float(dat[3])
        self.R_aft = float(dat[4])
        opps_data = [int(e) for e in dat[5:]]
        self.opps = opps_data[0:3]
        self.R_opp = float(sum(opps_data[3:6])) / 3
        self.oppps = opps_data[6:9]
        self.perf = self.R_opp + self.score * 10
        self.game_no = i
        self.R_strong = (2100 <= self.R_aft) or (1900 <= self.R_aft < 2000)
        self.R_red = (2000 <= self.R_aft)
        self.R_yellow = (1800 <= self.R_aft < 2000)
    def get_score(self, rival):
        for i in range(3):
            if self.opps[i] == rival:
                rival_rank = i + (self.rank <= i + 1)
                return self.oppps[i] + [-150, -200, -300, -350][rival_rank] # TODO: with (rival_rank+1)

class VsScore:
    def __init__(self, scores, rival):
        self.scores = []
        self.rival = rival
        for score in scores:
            if rival not in score.opps:
                continue
            self.scores.append({'my_score': score.score, 'rival_score': score.get_score(rival)})

def dev(sumsq, count, av):
    try:
        return ((sumsq / count) - av ** 2) ** 0.5
    except:
        return 0

class WholeScore:
    def __init__(self, scores):
        # todo: VPM, GPV
        self.min_R, self.max_R = 4500.0, -1500.0
        self.min_score, self.max_score = 100000000.0, -100000000.0
        self.game_count = 0
        self.rank_dist = [0 for i in range(4)] # rank distribution
        point_sep = [50 * i for i in range(11)]# + [0]
        self.point_dist = [0 for i in range(12)] # point distribution
        sum_oppR, sum_score, sum_perf = 0, 0, 0
        sq_oppR, sq_score, sq_perf = 0, 0, 0
        date_dist = {}
        first = True
        for score in scores:
            if first:
                self.min_R, self.max_R = min(self.min_R, score.R_bef), max(self.max_R, score.R_bef)
                first = False
            self.min_R, self.max_R = min(self.min_R, score.R_aft), max(self.max_R, score.R_aft)
            self.curr_R = score.R_aft
            self.min_score, self.max_score = min(self.min_score, score.score), max(self.max_score, score.score)
            self.game_count += 1
            self.rank_dist[score.rank - 1] += 1
            for p in range(11):
                if score.point < point_sep[p]:
                    self.point_dist[p] += 1
                    break
            else:
                self.point_dist[11] += 1
            #self.point_dist.reverse()
            sum_oppR += score.R_opp
            sum_score += score.score
            sum_perf += score.perf
            sq_oppR += score.R_opp ** 2
            sq_score += score.score ** 2
            sq_perf += score.perf ** 2
            if score.game_date not in date_dist:
                if score.game_date < long_ago:
                    continue
                date_dist[score.game_date] = 0
            date_dist[score.game_date] += 1
        colors = 'bfbf00#50fd30#05dc9b#1675f2#7516f2#dc059b#fd5030'.split('#')
        dates = list(sorted(date_dist.keys(), reverse=True))
        self.date_dist = [{
          'color': colors[d.weekday()],
          'date': d,
          'played': date_dist[d]
        } for d in dates]
        try:
            date_diff = (dates[0] - dates[len(dates)-1]).days
            visits = len(self.date_dist)
            sub_game_count = sum(date_dist.values())
            if 10 <= visits:
                self.GPV = sub_game_count / visits
                if 30 <= date_diff:
                    self.VPM = (visits - 0.5) * 30 / date_diff
                    self.GPM = self.GPV * self.VPM
        except:
            pass
        self.av_oppR = sum_oppR / self.game_count
        self.av_score = sum_score / self.game_count
        self.av_perf = sum_perf / self.game_count
        self.dev_oppR = dev(sq_oppR, self.game_count, self.av_oppR)
        self.dev_score = dev(sq_score, self.game_count, self.av_score)
        self.dev_perf = dev(sq_perf, self.game_count, self.av_perf)
        isqr_games = self.game_count ** -0.5
        #self.dev_oppR /= self.game_count ** 0.5
        self.dev_score *= isqr_games
        self.dev_perf *= isqr_games
        self.rank_perc = [r * 100 / self.game_count for r in self.rank_dist]
        self.pdr = reversed(self.point_dist)


class BranchPlayerPage(BranchGeneral):
    '2012-04-12,0,1160,oldR,newR,op1,op2,op3,R1,R2,R3,P1,P2,P3'
    def get_real(self, bid):
        pid = self.get_int('pid')
        player = Player.all().filter('bid =', bid).filter('pid =', pid).get()
        limit = self.get_int('limit', 1000)
        detail = self.get_str('detail')
        use_all = self.get_str('all')
        if player is None:
            return self.response.out.write(
              "player %d of %s doesn't exist" % (pid, self.branch_name()))
        if self.get_str('admin_view') == 'yes':
            return self.response.out.write('<br>'.join(player.detail.strip().split('\n')))
        lines = player.detail.strip().split('\n')
        n = len(lines)
        if use_all or not 0 < limit <= n:
            limit = n
        scores = []
        for i in range(len(lines) - limit, len(lines)):
            scores.append(MatchScore(lines[i], i + 1))
        rival = self.get_int('rival')
        if 0 < rival:
            return self.get_rival(pid, VsScore(scores, rival))
        whole_score = WholeScore(scores)
        self.write_out('branch/player', {
          'played': n,
          'bname': self.branch_name(),
          'pid': pid,
          'scores': list(reversed(scores)),
          'simple': not detail,
          'whole_score': whole_score,
        })

    def get_rival(self, pid, vsscore):
        self.write_out('branch/rival', {
          'bname': self.branch_name(),
          'pid': pid,
          'rid': vsscore.rival,
          'scores': vsscore.scores
        })
