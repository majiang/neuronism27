from scoredata import get_player, get_branch

from rating import NeuronismRating
ratesys = NeuronismRating()
table = range(4)

def add_game(bid, date, pids, points):
    'add the score into the system: trusting the arguments'
    branch = get_branch(bid)
    branch.add_game(date, pids)
    branch.put()
    players = [get_player(bid, pid) for pid in pids]
    rating_bef = [player.curR for player in players]
    played_games = [player.played for player in players]
    rating_aft = ratesys.get_rating(played_games, points, rating_bef)
    for i in table:
        if pids[i] == 0:
            continue # player #0: ignore score.
        players[i].update_score(
          players=pids, # opponents' (and my) player id
          ratings=rating_bef, # rating
          point=points,
          rating=rating_aft[i],
          date=date
        )
