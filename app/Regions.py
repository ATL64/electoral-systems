from abc import ABC
from collections import Counter
import copy
import operator

class Region():
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        return


class Electoral_Region(Region):
    def __init__(self, name: str, level: int, census: int, n_seats: int, votes: dict, nota: int, spoilt_votes: int):
        super(Electoral_Region, self).__init__(name, level)
        self.census = census
        self.n_seats = n_seats
        self.votes = votes
        self.nota = nota # None Of The Above
        self.spoilt_votes = spoilt_votes
        self.total_votes = sum(votes.values())
        return

    def compute_election_result(self, system):
        vote_threshold = self.total_votes*system['threshold']/100
        valid_votes = {k:v for k,v in self.votes.items() if v>vote_threshold}
        round_votes = copy.deepcopy(valid_votes)
        seat_counter = Counter()
        n_seats = copy.deepcopy(self.n_seats)

        while n_seats!=0:
            best_party = max(round_votes.items(), key=operator.itemgetter(1))[0]
            seat_counter[best_party] += 1
            if system['name']=='dHondt':
                round_votes[best_party] = valid_votes[best_party] / (seat_counter[best_party] + 1)
            else:
                round_votes[best_party] = valid_votes[best_party] / (2*seat_counter[best_party] + 1)
            n_seats -= 1

        return seat_counter
