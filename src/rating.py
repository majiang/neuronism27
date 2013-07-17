from math import exp, tanh

table = range(4)

class AbstractRating:

    def get_rating(self, played, point, rating):
        my_weight = [self.opponent_weight(p) for p in played]
        opp_w = [sum(my_weight) - my_weight[i] for i in table]
        ex = [sum((rating[i]-rating[j]) / 30.0 for j in table) for i in table]
        sw = [self.weight(p, r)*o for (p, r, o) in zip(played, rating, opp_w)]
        ac = self.actual(point)
        return [
          r+w*(a-e)
            for (r, w, a, e)
            in zip(rating, sw, ac, ex)
        ]

class NeuronismRating(AbstractRating):

    def opponent_weight(self, oppP):
        return (1 + tanh(oppP/50)) / 6

    def weight(self, p, r):
        w = max(0.25*exp(p/-240.87589233307), 0.04750593824228) # weight: 400G
        s = (1+1/(1+exp(0.02*(r-2000))))/2 # stabilizer: (1800, 1.00)..(2200, 0.50)
        #change to: s = (1+1/(1+exp(0.04*(r-1900))))/2 # stabilizer: (1800, 1.00)..(2000, 0.50)
        return w*s

    def actual(self, points):
        RP = [-150, -200, -300, -350]
        return [p+r for (p, r) in zip(points, RP)]
