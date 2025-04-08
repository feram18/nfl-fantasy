import json
import logging
import time
from collections import defaultdict
from typing import List

from sleeper_wrapper import League

import constants
from data.fantasy import Fantasy
from model.match import Match
from model.standings import Standings, StandingsItem
from model.team import Team
from utils import calculate_winning_percentage, get_current_week

SLEEPER_CREDENTIALS = 'auth/sleeper.json'


def get_credentials() -> dict:
    with open(SLEEPER_CREDENTIALS, 'r') as credentials:
        return json.load(credentials)


class Sleeper(Fantasy):
    def __init__(self):
        self.credentials: dict = get_credentials()
        self.league: League = self.fetch_league()
        self._rosters = self.league.get_rosters()
        self._users = self.league.get_users()
        self._teams: dict = self.parse_teams()
        self._mapper: dict = self.league.map_rosterid_to_ownerid(self._rosters)
        self.name: str = self.league.get_league_name()
        self.matches: List[Match] = self.fetch_matches()
        self.standings: Standings = self.fetch_standings()
        self.last_updated: float = time.time()

    def fetch_league(self) -> League:
        return League(self.credentials['league_id'])

    def fetch_matches(self) -> List[Match]:
        matchups = defaultdict(list)
        for team in sorted(self.league.get_matchups(week=get_current_week()), key=lambda x: x['matchup_id']):
            matchups[team['matchup_id']].append(team)

        return [Match(Team(self.map_roster_to_user(team[0]['roster_id']),
                           team[0]['points'],
                           0,
                           team[0]['starters']),
                      Team(self.map_roster_to_user(team[1]['roster_id']),
                           team[1]['points'],
                           0,
                           team[1]['starters'])) for _, team in matchups.items()]

    def fetch_standings(self) -> Standings:
        return Standings([StandingsItem(entry[0],
                                        entry[1],  # wins
                                        0,  # no ties
                                        entry[2],  # losses
                                        f'{calculate_winning_percentage(int(entry[1]), int(entry[2])):.3f}'
                                        if (int(entry[1]) + int(entry[2])) != 0 else '0.000',
                                        rank)
                          for rank, entry in enumerate(self.league.get_standings(self._rosters, self._users), 1)])

    def update(self):
        if self.last_updated - time.time() < constants.UPDATE_RATE:
            logging.debug('Updating Sleeper data...')
            self.matches = self.fetch_matches()
            self.standings = self.fetch_standings()

    def parse_teams(self) -> dict:
        return self.league.map_users_to_team_name(self._users)

    def map_roster_to_user(self, roster_id: int) -> str:
        user_id = self._mapper.get(roster_id)
        return self._teams.get(user_id) if user_id else None
