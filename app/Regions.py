from abc import ABC
from collections import Counter
import copy
import math
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
        self.nota = nota # None Of The Above (https://en.wikipedia.org/wiki/None_of_the_above)
        self.spoilt_votes = spoilt_votes
        self.total_votes = sum(votes.values())
        return

    def compute_election_result(self, system, valid_parties=None):
        if valid_parties:
            valid_votes = {p:v for p,v in self.votes.items() if p in valid_parties}
        else:
            vote_threshold = self.total_votes*system['threshold']/100
            valid_votes = {k:v for k,v in self.votes.items() if v>vote_threshold}
        round_votes = copy.deepcopy(valid_votes)
        seat_counter = Counter()
        n_seats = copy.deepcopy(self.n_seats)

        if 'LRM' in system['name']: # Largest Remainder Method
            if 'Hare' in system['name']:
                seat_cost = sum(valid_votes.values()) / n_seats
            elif 'Droop' in system['name']:
                seat_cost = 1 + sum(valid_votes.values()) / (1 + n_seats)
            elif 'HB' in system['name']:
                seat_cost = sum(valid_votes.values()) / (1 + n_seats)
            elif 'Imperiali' in system['name']:
                seat_cost = sum(valid_votes.values()) / (2 + n_seats)
            remainders = {}
            seats_given = 0
            for party in valid_votes:
                rem, n = math.modf(valid_votes[party] / seat_cost)
                n = int(n)
                seat_counter[party] = n
                remainders[party] = rem
                seats_given += n

            sorted_remainders = dict(sorted(remainders.items(), key=lambda item: item[1], reverse=True))
            for party in remainders:
                if seats_given >= n_seats:
                    break
                seat_counter[party] += 1
                seats_given += 1

        else:
            while n_seats!=0:
                best_party = max(round_votes.items(), key=operator.itemgetter(1))[0]
                seat_counter[best_party] += 1
                if system['name']=='dHondt':
                    round_votes[best_party] = valid_votes[best_party] / (seat_counter[best_party] + 1)
                elif system['name']=='SL': # Sainte-Laguë
                    round_votes[best_party] = valid_votes[best_party] / (2*seat_counter[best_party] + 1)
                elif system['name']=='MSL': # Modified Sainte-Laguë
                    if best_party in seat_counter:
                        round_votes[best_party] = valid_votes[best_party] / (2*seat_counter[best_party] + 1)
                    else:
                        round_votes[best_party] = valid_votes[best_party] / 1.4

                n_seats -= 1

        return seat_counter
