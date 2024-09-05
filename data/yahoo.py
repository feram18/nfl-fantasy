import pprint
from typing import List

from yahoo_fantasy_api.game import Game
from yahoo_fantasy_api.league import League
from yahoo_oauth import OAuth2

from model.match import Match
from model.standings import Standings, StandingsItem
from model.team import Team

YAHOO_AUTH = 'auth/yahoo.json'


class YahooFantasy:
    def __init__(self):
        self.oauth: OAuth2 = OAuth2(None, None, from_file=YAHOO_AUTH)
        self.game: Game = Game(self.oauth, 'nfl')
        self.league: League = self.game.to_league(self.game.league_ids(year=2024)[0])
        self.matches: List[Match] = self.fetch_matches()
        self.standings: Standings = self.fetch_standings()

    def print(self):
        pprint.pprint(self.matches)
        pprint.pprint(self.standings)

    def fetch_matches(self) -> List[Match]:
        matches = dict(self.league.matchups()['fantasy_content']['league'][1]['scoreboard']['0']['matchups'])

        return [
            Match(Team(matches[match]['matchup']['0']['teams']['0']['team'][0][2],
                       float(matches[match]['matchup']['0']['teams']['0']['team'][1]['team_points']['total']),
                       float(matches[match]['matchup']['0']['teams']['0']['team'][1]['team_projected_points']['total']),
                       []),
                  Team(matches[match]['matchup']['0']['teams']['1']['team'][0][2],
                       float(matches[match]['matchup']['0']['teams']['1']['team'][1]['team_points']['total']),
                       float(matches[match]['matchup']['0']['teams']['1']['team'][1]['team_projected_points']['total']),
                       []))
            for match in matches.keys() if match != 'count'
        ]

    def fetch_standings(self) -> Standings:
        return Standings([StandingsItem(entry['name'],
                                        entry['outcome_totals']['wins'],
                                        entry['outcome_totals']['ties'],
                                        entry['outcome_totals']['losses'],
                                        entry['outcome_totals']['percentage'],
                                        entry['rank'] if entry['rank'] != '' else 1)
                          for entry in self.league.standings()])
