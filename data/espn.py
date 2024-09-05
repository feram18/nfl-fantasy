import json
import logging
from typing import List

from espn_api.football import League

from model.match import Match
from model.team import Team

ESPN_CREDENTIALS = 'auth/espn.json'


class EspnFantasy:
    def __init__(self):
        self.league: League = None
        self.scores: List[Match] = None
        self.initialize()

    def initialize(self):
        self.fetch_league()
        if len(self.league.draft) > 0:
            self.scores = self.fetch_scores()
        else:
            logging.error('League not yet drafted')

    def fetch_league(self):
        logging.debug('Fetching league...')
        with open(ESPN_CREDENTIALS, 'r') as credentials:
            creds = json.load(credentials)
            self.league = League(league_id=creds['league_id'],
                                 year=creds['year'],
                                 espn_s2=creds['espn_s2'],
                                 swid=creds['swid'])

    def fetch_scores(self):
        logging.debug('Fetching scores...')
        return [Match(Team(entry.home_team.team_name, entry.home_score, entry.home_projected, entry.home_lineup),
                      Team(entry.away_team.team_name, entry.away_score, entry.away_projected, entry.away_lineup))
                for entry in self.league.box_scores()]

    def refresh(self):
        self.fetch_scores()

    def print_all(self):
        if len(self.scores) > 0:
            for score in self.scores:
                print(score)
        else:
            logging.warning('No scores to display')
