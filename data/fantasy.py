import pprint
from abc import ABC, abstractmethod
from typing import List, Optional

from model.match import Match
from model.standings import Standings


class Fantasy(ABC):
    league: Optional  # dependent on library
    name: str
    matches: List[Match]
    standings: Standings
    last_updated: float

    @abstractmethod
    def fetch_league(self):
        pass

    @abstractmethod
    def fetch_matches(self) -> List[Match]:
        pass

    @abstractmethod
    def fetch_standings(self) -> Standings:
        pass

    @abstractmethod
    def update(self):
        pass

    def debug(self):
        pprint.pprint(self.name)
        pprint.pprint(self.matches)
        pprint.pprint(self.standings)
