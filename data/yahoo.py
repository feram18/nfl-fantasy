import logging
import time
from typing import List

from yahoo_fantasy_api.game import Game
from yahoo_fantasy_api.league import League
from yahoo_oauth import OAuth2

import constants
from data.fantasy import Fantasy
from model.match import Match
from model.standings import Standings, StandingsItem
from model.team import Team
from utils import get_current_season

YAHOO_AUTH = 'auth/yahoo.json'


class YahooFantasy(Fantasy):
    def __init__(self):
        self.oauth: OAuth2 = OAuth2(None, None, from_file=YAHOO_AUTH)
        self.game: Game = Game(self.oauth, 'nfl')
        self.league: League = self.fetch_league()
        self.name: str = self.league.settings()['name']
        self.matches: List[Match] = self.fetch_matches()
        self.standings: Standings = self.fetch_standings()
        self.last_updated: float = time.time()

    def fetch_league(self) -> League:
        return self.game.to_league(self.game.league_ids(year=get_current_season())[0])

    def fetch_matches(self) -> List[Match]:
        matches = dict(self.league.matchups()['fantasy_content']['league'][1]['scoreboard']['0']['matchups'])

        # TODO: Get Lineups
        return [
            Match(Team(match['matchup']['0']['teams']['0']['team'][0][2],
                       float(match['matchup']['0']['teams']['0']['team'][1]['team_points']['total']),
                       float(match['matchup']['0']['teams']['0']['team'][1]['team_projected_points']['total']),
                       []),
                  Team(match['matchup']['0']['teams']['1']['team'][0][2],
                       float(match['matchup']['0']['teams']['1']['team'][1]['team_points']['total']),
                       float(match['matchup']['0']['teams']['1']['team'][1]['team_projected_points']['total']),
                       []))
            for key, match in matches.items() if key != 'count'
        ]

    def fetch_standings(self) -> Standings:
        return Standings([StandingsItem(entry['name'],
                                        entry['outcome_totals']['wins'],
                                        entry['outcome_totals']['ties'],
                                        entry['outcome_totals']['losses'],
                                        entry['outcome_totals']['percentage'],
                                        entry['rank'] if entry['rank'] != '' else 1)
                          for entry in self.league.standings()])

    def update(self):
        if self.last_updated - time.time() < constants.UPDATE_RATE:
            logging.debug('Updating Yahoo! Fantasy data...')
            self.matches: List[Match] = self.fetch_matches()
            self.standings: Standings = self.fetch_standings()
