from dataclasses import dataclass

from model.team import Team


@dataclass
class Match:
    home: Team
    away: Team
