from google.appengine.ext import db
from util import min_date, yesterday, firstday, long_ago

class BranchCounter(db.Model):
    'index: bid > date'
    bid = db.IntegerProperty(required=True)
    date = db.DateProperty(required=True, default=min_date)
    games = db.IntegerProperty(required=True, default=0, indexed=False)
    customers = db.TextProperty(default='')

    def add(self, customers):
        self.games += 1
        if self.date < long_ago:
            self.put()
            return
        for customer in customers:
            if customer:
                self.customers += '%d,' % customer
        self.put()

    def next(self, date):
        if self.date > date:
            raise ValueError('date rollback')
        next_counter = BranchCounter(
          bid=self.bid,
          date=date,
          games=self.games
        )
        next_counter.put()
        return next_counter

def multiset_to_dict(raw):
    ret = {}
    for e in raw.strip(',').split(','):
        i = int(e)
        ret[i] = ret.get(i, 0) + 1
    return ret

def count_customers(bid, date):
    bc = BranchCounter.all().filter('bid =', bid).filter('date =', date).get()
    if bc:
        return multiset_to_dict(bc.customers)
    return {}

def count_games(bid, date_from, date_to):
    bc_from = BranchCounter.all().filter('bid =', bid).filter('date =', yesterday(date_from)).get()
    bc_to = BranchCounter.all().filter('bid =', bid).filter('date =', yesterday(date_to)).get()
    if (bc_from is None) or (bc_to is None):
        return 0
    return bc_to.games - bc_from.games

def monthly_customers(bid, year, month):
    date_cur = firstday(year, month)
    stats_players = []
    stats_games = []
    try:
        games = BranchCounter.all().filter('bid =', bid).filter('date =', yesterday(date_cur)).get().games
    except:
        games = 0
    while date_cur.month == month:
        cur = BranchCounter.all().filter('bid =', bid).filter('date =', date_cur).get()
        if cur is None:
            continue
        stats_players.append(multiset_to_dict(cur.customers))
        stats_games.append(cur.games - games)
        games = cur.games
    return {'customers': stats_players, 'games': stats_games}

class BranchState(db.Model):
    bid = db.IntegerProperty(required=True)
    counter = db.ReferenceProperty(reference_class=BranchCounter, indexed=False)

    def add_game(self, date, pids):
        if self.counter.date != date:
            self.counter = self.counter.next(date)
        self.counter.add(pids)
        self.put()

    def today(self):
        return self.counter.date

def new_branch_counter(bid):
    ret = BranchCounter(bid=bid, customers='')
    ret.put()
    return ret

def get_branch(bid):
    ret = BranchState.all().filter('bid =', bid).get()
    if ret is None:
        ret = BranchState(bid=bid, counter=new_branch_counter(bid))
        ret.put()
    return ret

def branch_newest_date(bid):
    return get_branch(bid).counter.date

class SumScore(db.Model):
    'index: bid > term_end > date; bid > pid > gfp'
    bid = db.IntegerProperty(required=True)
    pid = db.IntegerProperty(required=True)
    gfp = db.IntegerProperty(required=True, default=0)
    term_end = db.BooleanProperty(required=True, default=False)
    date = db.DateProperty(required=True, default=min_date)
    total_point = db.IntegerProperty(required=True, default=0, indexed=False)
    rank_dist = db.ListProperty(long, required=True, default=[0,0,0,0], indexed=False)
    point_dist = db.ListProperty(long, required=True, default=[0,0,0,0,0,0,0,0,0,0,0,0], indexed=False)
    rating = db.FloatProperty(required=True, default=1500.0, indexed=False)

    def next(self, date, point, rank, new_rating):
        new_rd = self.rank_dist[:]
        new_pd = self.point_dist[:]
        new_rd[rank] += 1
        if point < 0:
            new_pd[0] += 1
        elif point >= 500:
            new_pd[11] += 1
        else:
            new_pd[1 + point // 50] += 1
        ret = SumScore(
          bid=self.bid,
          pid=self.pid,
          gfp=self.gfp+1,
          term_end=((self.gfp + 1) % 20 == 0),
          date=date,
          total_point=(self.total_point + point - 250),
          rank_dist=new_rd,
          point_dist=new_pd,
          rating=new_rating
        )
        ret.put()
        return ret

def encode_detail(date, myid, players, ratings, point, rating):
    '2012-04-12,1,1160,oldR,newR,op1,op2,op3,R1,R2,R3,P1,P2,P3'
    rank = players.index(myid)
    mypt = point[rank]
    return '%s,%d,%d,%.2f,%.2f,%d,%d,%d,%d,%d,%d,%d,%d,%d' % (
      (date, rank, mypt, ratings[rank], rating) +
      tuple(players[:rank] + players[rank+1:]) +
      tuple(ratings[:rank] + ratings[rank+1:]) +
      tuple(point[:rank] + point[rank+1:])
    )

def get_ss(bid, pid, gfp):
    return SumScore.all().filter('bid =', bid).filter('pid =', pid).filter('gfp =', gfp).get()

class Player(db.Model):
    'index: bid > pid; bid > degree > achieve_date; bid > rated > last_visit'
    bid = db.IntegerProperty(required=True)
    pid = db.IntegerProperty(required=True)
    detail = db.TextProperty(default='')
    current = db.ReferenceProperty(reference_class=SumScore, required=True, indexed=False)
    last_visit = db.DateProperty(required=True, default=min_date)
    prev_visit = db.DateProperty(required=True, default=min_date)
    played = db.IntegerProperty(required=True, default=0)
    customer = db.BooleanProperty(required=True, default=False)
    rated = db.BooleanProperty(default=False)
    maxR = db.FloatProperty(required=True, default=1500.0)
    curR = db.FloatProperty(required=True, default=1500.0)
    degree = db.IntegerProperty(required=True, default=0)
    achieve_date = db.DateProperty(required=False)

    def get_prev(self, gfp):
        if gfp < 0:
            gfp += self.played
        return get_ss(self.bid, self.pid, gfp)

    def update_score(self, players, ratings, point, rating, date):
    # detail
        dat = self.detail.splitlines()
        dat.append(encode_detail(date, self.pid, players, ratings, point, rating))
        self.detail = '\n'.join(dat)
    # current
        rank = players.index(self.pid)
        self.current = self.current.next(date, point[rank], rank, rating)
    # dates, played
        self.last_visit = date
        self.played += 1
        if 100 <= self.played:
            self.customer = True
        if 10 <= self.played:
            self.rated = True
        prev = self.get_prev(-20)
        if prev:
            self.prev_visit = prev.date
    # delete old data (indent is correct!)
            if self.played % 20:
                prev.delete()
        if self.played % 20 == 0 and self.played % 2000 != 0:
            preev = self.get_prev(-2000)
            if preev:
                preev.delete()
    # ratings, degree
        self.curR = self.current.rating
        if self.maxR < self.curR:
            self.maxR = self.curR
            new_degree = int(self.maxR*0.02) - 35
            if self.degree < new_degree:
                self.degree = new_degree
                self.achieve_date = date
        self.put()

def new_sumscore(bid, pid):
    ret = SumScore(bid=bid, pid=pid)
    ret.put()
    return ret

def get_player(bid, pid):
    ret = Player.all().filter('bid =', bid).filter('pid =', pid).get()
    if ret is None:
        ret = Player(bid=bid, pid=pid, current=new_sumscore(bid, pid))
        ret.put()
    return ret

class QueueScore(db.Model):
    'index: game_date > input_date'
    bid = db.IntegerProperty(required=True)
    game_date = db.DateProperty(required=True)
    input_date = db.DateTimeProperty(required=True, auto_now_add=True)
    body = db.TextProperty(required=True)
    pos = db.IntegerProperty(required=True, default=0, indexed=False)

class FrequentQuery(db.Model):
    bid = db.IntegerProperty(required=True)
    pids = db.ListProperty(int, default=[])

    @classmethod
    def by_bid(cls, bid):
        ret = FrequentQuery.all().filter('bid =', bid).get()
        if ret is None:
            ret = FrequentQuery(bid=bid)
            ret.put()
        return ret

    def query(self):
        ret = []
        for pid in self.pids:
            player = get_player(self.bid, pid)
            ret.append({'pid': pid, 'games': (player.played % 20), 'date': player.last_visit})
        return ret

    def append(self, pid):
        if pid in self.pids:
            return ''
        self.pids.append(pid)
        self.put()
        return 'added query: player = %d' % pid

    def remove(self, pid):
        if pid not in self.pids:
            return ''
        self.pids.remove(pid)
        self.put()
        return 'removed query: player = %d' % pid


def count_unprocessed(bid=None):
    if bid:
        return QueueScore.all().filter('bid =', bid).count(200)
    return QueueScore.all().count(500)


def diff_list(start, end):
    return [(e-s) for (s, e) in zip(start, end)]

class SpanScore():
    'bid, pid, gfp, term_end, date, total_point, rank_dist, point_dist, rating'

    def __init__(self, start, end):
        self.bid = start.bid
        self.pid = start.pid
        self.games = end.gfp - start.gfp
        self.count = start.gfp // 20
        self.finish_date = end.date
        self.point = end.total_point - start.total_point
        self.rank = diff_list(start.rank_dist, end.rank_dist)
        self.point_detail = diff_list(start.point_dist, end.point_dist)
        self.point_summary = [
          self.point_detail[0], 
          sum(self.point_detail[1:6]),
          sum(self.point_detail[6:11]),
          self.point_detail[11]
        ]
        self.rating_bef = start.rating
        self.rating_aft = end.rating
        self.rp_gain = sum(p*c for (p, c) in zip([100, 50, -50, -100], self.rank))
        self.score = self.point + self.rp_gain
        self.av_rank = float(sum(p*c for (p, c) in zip(range(4), self.rank))) / self.games + 1

class QueueStopper(db.Model):
    pass
