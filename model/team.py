from dataclasses import dataclass
from typing import List

from espn_api.football import Player


@dataclass
class Team:
    name: str
    score: float
    projected: float
    lineup: List[Player] | List[str]
    