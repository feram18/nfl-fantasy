from dataclasses import dataclass
from typing import List


@dataclass
class StandingsItem:
    team: str
    wins: int
    ties: int
    losses: int
    pct: str
    rank: int = 1


@dataclass
class Standings:
    positions: List[StandingsItem]
