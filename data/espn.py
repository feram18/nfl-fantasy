import json
import logging
import time
from typing import List

from espn_api.football import League

import constants
from data.fantasy import Fantasy
from model.match import Match
from model.standings import Standings, StandingsItem
from model.team import Team
from utils import calculate_winning_percentage, get_current_season

ESPN_CREDENTIALS = 'auth/espn.json'


def get_credentials() -> dict:
    with open(ESPN_CREDENTIALS, 'r') as credentials:
        return json.load(credentials)


class EspnFantasy(Fantasy):
    def __init__(self):
        self.credentials: dict = get_credentials()
        self.league: League = self.fetch_league()
        self.name: str = self.league.settings.name
        self.matches: List[Match] = self.fetch_matches() if len(self.league.draft) > 0 else None
        self.standings: Standings = self.fetch_standings()
        self.last_updated: float = time.time()

    def fetch_league(self) -> League:
        logging.debug('Fetching league...')
        return League(league_id=self.credentials['league_id'],
                      year=int(get_current_season()),
                      espn_s2=self.credentials['espn_s2'],
                      swid=self.credentials['swid'])

    def fetch_matches(self) -> List[Match]:
        logging.debug('Fetching matches...')
        return [Match(Team(entry.home_team.team_name,
                           entry.home_score,
                           entry.home_projected,
                           entry.home_lineup),
                      Team(entry.away_team.team_name,
                           entry.away_score,
                           entry.away_projected,
                           entry.away_lineup))
                for entry in self.league.box_scores()]

    def fetch_standings(self) -> Standings:
        logging.debug('Fetching standings...')
        return Standings(sorted([StandingsItem(team.team_name,
                                               team.wins,
                                               team.ties,
                                               team.losses,
                                               f'{calculate_winning_percentage(team.wins, team.losses, team.ties):.3f}'
                                               if (team.wins + team.ties + team.losses) != 0 else '0.000',
                                               team.standing)
                                 for team in self.league.standings()], key=lambda i: i.rank))

    def update(self):
        if self.last_updated - time.time() < constants.UPDATE_RATE:
            logging.debug('Updating ESPN Fantasy data...')
            self.league.refresh()
            self.matches = self.fetch_matches() if len(self.league.draft) > 0 else None
            self.standings = self.fetch_standings()
