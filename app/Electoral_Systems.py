# TO BE DECIDED IF WE WILL USE THIS CLASS OR NOT
# RIGHT NOW IT DOESN'T SEEM NECESSARY, BUT MIGHT BE USEFUL

from abc import ABC
from collections import Counter
import copy
import operator

class Electoral_System(ABC):
    def __init__(self, name: str):
        self.name = name
        return
