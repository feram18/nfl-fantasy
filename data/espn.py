import json
import logging
import pprint
from typing import List

from espn_api.football import League

from model.match import Match
from model.standings import Standings, StandingsItem
from model.team import Team

ESPN_CREDENTIALS = 'auth/espn.json'


def get_credentials():
    with open(ESPN_CREDENTIALS, 'r') as credentials:
        return json.load(credentials)


class EspnFantasy:
    def __init__(self):
        self.credentials = get_credentials()
        self.league: League = self.fetch_league()
        self.matches: List[Match] = self.fetch_matches() if len(self.league.draft) > 0 else None
        self.standings: Standings = self.fetch_standings()

    def print(self):
        pprint.pprint(self.matches)
        pprint.pprint(self.standings)

    def fetch_league(self) -> League:
        logging.debug('Fetching league...')
        return League(league_id=self.credentials['league_id'],
                      year=self.credentials['year'],
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
        return Standings([StandingsItem(team.team_name,
                                        team.wins,
                                        team.ties,
                                        team.losses,
                                        (team.wins + 0.5 * team.ties) / (team.wins + team.ties + team.losses),
                                        team.standing)
                          for team in self.league.standings()])
