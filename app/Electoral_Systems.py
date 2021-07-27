from abc import ABC
from collections import Counter
import copy
import operator

class Electoral_System(ABC):
    def __init__(self, name: str):
        self.name = name
        return



# THESE TWO FUNCTIONS SHOULD BE REFACTORED OR SOMETHING - ONLY TWO CHARACTERS CHANGE

def compute_dHondt(votes: dict, n_seats: int, threshold: float):
    total_votes = sum(votes.values())
    vote_threshold = total_votes*threshold
    valid_votes = {k:v for k,v in votes.items() if v>vote_threshold}
    round_votes = copy.deepcopy(valid_votes)
    seat_counter = Counter()

    while n_seats!=0:
        best_party = max(round_votes.items(), key=operator.itemgetter(1))[0]
        seat_counter[best_party] += 1
        round_votes[best_party] = valid_votes[best_party] / (seat_counter[best_party] + 1)
        n_seats -= 1

    return seat_counter

def compute_Sainte_Lague(votes: dict, n_seats: int, threshold: float):
    total_votes = sum(votes.values())
    vote_threshold = total_votes*threshold
    valid_votes = {k:v for k,v in votes.items() if v>vote_threshold}
    round_votes = copy.deepcopy(valid_votes)
    seat_counter = Counter()

    while n_seats!=0:
        best_party = max(round_votes.items(), key=operator.itemgetter(1))[0]
        seat_counter[best_party] += 1
        round_votes[best_party] = valid_votes[best_party] / (2*seat_counter[best_party] + 1)
        n_seats -= 1

    return seat_counter
