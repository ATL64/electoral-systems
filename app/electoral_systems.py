SYSTEM_NAMES = ['dHondt', 'SL', 'LRM-Hare', 'LRM-Droop', 'LRM-HB', 'LRM-Imperiali']
MAX_LEVEL = 3
MAX_THRESHOLD = 15


class System():
    """
    Class representing an electoral system.

    ...
    Attributes
    ----------
    name: str
        The name of the system. Must be one of 'dHondt', 'SL', 'LRM-Hare',
        'LRM-Droop', 'LRM-HB', 'LRM-Imperiali'.
    level: int
        The regional level at which the parliament seats are assigned.
    threshold: int
        The minimum percentage of votes that a party needs to obtain in order
        to get representatives.
    threshold_country: bool
        Whether the threshold applies at a country-level or not. If False, it
        means that the threshold applies at a regional level.
    """
    def __init__(self, name: str, level: int, threshold: int, threshold_country=False):
        self.name = name
        self.level = level
        self.threshold = threshold
        self.threshold_country = threshold_country
        return

    @property
    def name(self):
        """
        The name of the system.
        """
        return self._name

    @name.setter
    def name(self, value):
        if value not in SYSTEM_NAMES:
            raise ValueError("System not supported")
        self._name = value

    @property
    def level(self):
        """
        The regional level at which the system applies.
        """
        return self._level

    @level.setter
    def level(self, value):
        if not 0 <= value <= MAX_LEVEL:
            raise ValueError("Regional level must be between 0 and {}".format(MAX_LEVEL))
        self._level = value

    @property
    def threshold(self):
        """
        The minimum percentage of votes that a party needs to obtain in order
        to get representatives.
        """
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if not 0 <= value <= MAX_THRESHOLD:
            raise ValueError("Threshold must be between 0 and {}".format(MAX_THRESHOLD))
        self._threshold = value

    @property
    def threshold_country(self):
        """
        Whether the threshold applies at a country-level or not. If False, it
        means that the threshold applies at a regional level.
        """
        return self._threshold_country

    @threshold_country.setter
    def threshold_country(self, value):
        if not type(value) == bool:
            raise TypeError("Country-level threshold should be boolean.")
        self._threshold_country = value
