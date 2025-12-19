"""
Yahoo Fantasy Football API Data Puller for Fantasy Reckoning
Extracts complete season data for metrics calculation

Compatible with yahoo-fantasy-api version 2.12.2
GitHub: https://github.com/spilchen/yahoo_fantasy_api
Docs: https://yahoo-fantasy-api.readthedocs.io/
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

# Load environment variables
load_dotenv()


class FantasyWrappedDataPuller:
    """
    Pulls all necessary data from Yahoo Fantasy API
    """

    def __init__(self, league_id, season_year):
        """
        Initialize with league ID and season

        Args:
            league_id: Yahoo league ID (e.g., '12345')
            season_year: Season year (e.g., 2024)
        """
        self.league_id = str(league_id)
        self.season_year = int(season_year)
        self.sc = None  # OAuth session
        self.gm = None  # Game object
        self.lg = None  # League object

    def authenticate(self):
        """
        Handle Yahoo OAuth2 authentication
        Opens browser for user to authorize
        """
        print("Authenticating with Yahoo Fantasy API...")
        print("A browser window will open for you to authorize the app.")
        print("After authorization, you'll be redirected - copy the verification code.")

        # Create OAuth2 object - this will handle the auth flow
        self.sc = OAuth2(None, None, from_file='oauth2.json')

        if not self.sc.token_is_valid():
            self.sc.refresh_access_token()

        # Initialize game and league objects
        self.gm = yfa.Game(self.sc, 'nfl')

        # Get the game ID for the specified season
        game_id = self.gm.game_id()

        # Construct the full league key: game_id.l.league_id
        full_league_key = f"{game_id}.l.{self.league_id}"
        print(f"Using league key: {full_league_key}")

        self.lg = self.gm.to_league(full_league_key)

        print("✓ Authentication successful!")

    def _make_api_call_with_delay(self, func, *args, **kwargs):
        """
        Make API call with delay to avoid rate limits

        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass to function

        Returns:
            Result of function call
        """
        time.sleep(0.5)  # 500ms delay between calls
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"API call failed: {e}")
            return None

    def get_league_metadata(self):
        """
        Extract basic league information

        Returns:
            dict: League metadata
        """
        print("Fetching league metadata...")

        settings = self.lg.settings()
        standings = self.lg.standings()

        metadata = {
            'league_id': self.league_id,
            'name': settings.get('name', 'Unknown League'),
            'season': self.season_year,
            'num_teams': settings.get('num_teams', len(standings)),
            'playoff_start_week': settings.get('playoff_start_week', 15),
            'scoring_type': settings.get('scoring_type', 'head2head'),
            'current_week': self.lg.current_week(),

            # Enhanced settings for roster configuration
            'roster_positions': settings.get('roster_positions', {}),

            # Enhanced settings for waiver/FAAB
            'waiver_type': settings.get('waiver_type', 'unknown'),
            'waiver_rule': settings.get('waiver_rule', 'unknown'),
            'faab_budget': settings.get('faab_budget', 100),

            # Optional: Scoring settings (for future use)
            'stat_categories': settings.get('stat_categories', {}),
            'stat_modifiers': settings.get('stat_modifiers', {}),
        }

        print(f"✓ League: {metadata['name']} ({metadata['num_teams']} teams)")

        # Print roster configuration if available
        if metadata['roster_positions']:
            print(f"✓ Roster config: {len(metadata['roster_positions'])} position types")

        return metadata

    def get_all_teams(self):
        """
        Get all teams/managers in league

        Returns:
            list of dict: Team information
        """
        print("Fetching all teams...")

        teams_data = []
        standings = self.lg.standings()
        teams = self.lg.teams()

        # Convert standings list to dict for easier lookup
        standings_dict = {}
        if isinstance(standings, list):
            for team in standings:
                team_key = team.get('team_key')
                standings_dict[team_key] = team
        else:
            standings_dict = standings

        for team_key, team_info in teams.items():
            # Get team standings info
            team_standings = standings_dict.get(team_key, {})

            # Extract manager name from managers array
            manager_name = 'Unknown'
            managers = team_info.get('managers', [])
            if managers and len(managers) > 0:
                # managers is a list of dicts with 'manager' key
                first_manager = managers[0].get('manager', {})
                manager_name = first_manager.get('nickname', 'Unknown')

            team_data = {
                'team_id': team_key,
                'team_key': team_key,
                'team_name': team_info.get('name', 'Unknown'),
                'manager_name': manager_name,
                'final_standing': team_standings.get('rank', 0),
                'wins': team_standings.get('outcome_totals', {}).get('wins', 0),
                'losses': team_standings.get('outcome_totals', {}).get('losses', 0),
                'ties': team_standings.get('outcome_totals', {}).get('ties', 0),
                'points_for': float(team_standings.get('points_for', 0.0)),
                'points_against': float(team_standings.get('points_against', 0.0)),
                # Auction draft data
                'auction_budget_total': team_info.get('auction_budget_total', 200),
                'auction_budget_spent': team_info.get('auction_budget_spent', 0),
                'faab_balance': team_info.get('faab_balance', 0),
            }
            teams_data.append(team_data)

        print(f"✓ Found {len(teams_data)} teams")
        return teams_data

    def get_weekly_scores(self, team_id, week):
        """
        Get scoring data for a specific team and week

        Args:
            team_id: Yahoo team ID
            week: Week number (1-17)

        Returns:
            dict: Weekly scoring data
        """
        try:
            # matchups() returns a dict with raw JSON from Yahoo API
            scoreboard_data = self.lg.matchups(week)

            # The structure is: fantasy_content -> league[1] -> scoreboard -> 0 -> matchups
            matchups_dict = None

            if 'fantasy_content' in scoreboard_data:
                league_data = scoreboard_data['fantasy_content'].get('league', [])
                if len(league_data) > 1 and isinstance(league_data[1], dict):
                    scoreboard = league_data[1].get('scoreboard', {})
                    if '0' in scoreboard:
                        matchups_dict = scoreboard['0'].get('matchups', {})

            if not matchups_dict:
                print(f"No matchups found for week {week}")
                return None

            # matchups_dict is a dict with numeric string keys: {'0': {matchup}, '1': {matchup}, ...}
            # Also contains 'count' field which is an int - filter it out
            matchups_list = [v for v in matchups_dict.values() if isinstance(v, dict)]

            # Find this team's matchup
            team_matchup = None
            opponent_id = None
            opponent_points = 0.0
            result = 'L'
            team_points = 0.0

            # Iterate through matchups to find the one containing our team
            for matchup_obj in matchups_list:
                # Each matchup has structure: {'matchup': {...}}
                matchup_data = matchup_obj.get('matchup', {})

                # Teams are under matchup_data['0']['teams']
                # teams is a dict like: {'0': {'team': [...]}, '1': {'team': [...]}}
                if '0' not in matchup_data or 'teams' not in matchup_data['0']:
                    continue

                teams_dict = matchup_data['0']['teams']

                # Extract both teams from the matchup
                # Each team is structured as: {'team': [[metadata_list], {points_obj}]}
                teams_in_matchup = []
                for team_key in ['0', '1']:
                    if team_key in teams_dict:
                        team_array = teams_dict[team_key].get('team', [])
                        if len(team_array) >= 2:
                            # team_array[0] is list of metadata dicts
                            # team_array[1] is the points/stats object
                            metadata_list = team_array[0]
                            points_obj = team_array[1]

                            # Extract team_key from metadata
                            team_id_str = None
                            for item in metadata_list:
                                if isinstance(item, dict) and 'team_key' in item:
                                    team_id_str = item['team_key']
                                    break

                            teams_in_matchup.append({
                                'team_key': team_id_str,
                                'points_obj': points_obj,
                                'metadata': metadata_list
                            })

                # Look for our team in this matchup
                for idx, team_data in enumerate(teams_in_matchup):
                    if team_data['team_key'] == team_id:
                        # Found our team! Extract points
                        points_obj = team_data['points_obj']
                        team_points = float(points_obj.get('team_points', {}).get('total', 0.0))
                        projected_points = float(points_obj.get('team_projected_points', {}).get('total', 0.0))

                        # Get opponent
                        opponent_idx = 1 - idx
                        if opponent_idx < len(teams_in_matchup):
                            opponent = teams_in_matchup[opponent_idx]
                            opponent_id = opponent['team_key']
                            opponent_points = float(opponent['points_obj'].get('team_points', {}).get('total', 0.0))

                            # Determine result
                            if team_points > opponent_points:
                                result = 'W'
                            elif team_points < opponent_points:
                                result = 'L'
                            else:
                                result = 'T'

                        team_matchup = {
                            'week': week,
                            'actual_points': team_points,
                            'projected_points': projected_points,
                            'opponent_id': opponent_id,
                            'opponent_points': opponent_points,
                            'result': result,
                        }
                        break

                if team_matchup:
                    break

            return team_matchup

        except Exception as e:
            print(f"Error fetching week {week} scores for team {team_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_weekly_roster(self, team_id, week):
        """
        Get complete roster for a team in a specific week

        Args:
            team_id: Yahoo team ID
            week: Week number

        Returns:
            dict: Roster data with starters and bench
        """
        try:
            # roster() returns a list of player dicts, not a dict with .items()
            roster_list = self.lg.to_team(team_id).roster(week)

            if not roster_list:
                print(f"No roster data found for team {team_id} week {week}")
                return {'starters': [], 'bench': []}

            starters = []
            bench = []

            # roster_list is an array of player dicts with fields:
            # player_id, name, position_type, eligible_positions, selected_position, status
            for player_data in roster_list:
                player_info = {
                    'player_id': player_data.get('player_id', 0),
                    'player_name': player_data.get('name', 'Unknown'),
                    'position': player_data.get('position_type', 'Unknown'),
                    'selected_position': player_data.get('selected_position', 'BN'),
                    'eligible_positions': player_data.get('eligible_positions', []),
                    'status': player_data.get('status', ''),
                    # Note: roster() method doesn't include player points
                    # Points would need to be fetched separately via player_stats()
                    # or extracted from matchup data
                    'actual_points': 0.0,
                    'projected_points': 0.0,
                }

                # Check if starter or bench
                if player_data.get('selected_position') == 'BN':
                    bench.append(player_info)
                else:
                    starters.append(player_info)

            # Note: To get actual player points, you would need to either:
            # 1. Use League.player_stats(player_ids, req_type='week', week=week)
            # 2. Extract from the matchup/scoreboard data which includes roster + stats
            # The basic roster() method only returns positions, not statistics

            return {
                'starters': starters,
                'bench': bench,
                'total_starter_points': sum(p['actual_points'] for p in starters),
                'total_bench_points': sum(p['actual_points'] for p in bench),
            }

        except Exception as e:
            print(f"Error fetching week {week} roster for team {team_id}: {e}")
            import traceback
            traceback.print_exc()
            return {'starters': [], 'bench': []}

    def get_player_stats_for_week(self, player_ids, week):
        """
        Get player statistics for multiple players in a specific week

        Args:
            player_ids: List of player IDs
            week: Week number

        Returns:
            dict: Player ID -> stats dict
        """
        try:
            if not player_ids:
                return {}

            # Make single API call for all players
            stats_list = self.lg.player_stats(player_ids, 'week', week=week)

            # Convert to dict keyed by player_id
            stats_dict = {}
            for player_stats in stats_list:
                player_id = player_stats.get('player_id')
                stats_dict[player_id] = {
                    'points': float(player_stats.get('total_points', 0.0)),
                    'stats': player_stats
                }

            return stats_dict

        except Exception as e:
            print(f"      Error fetching player stats for week {week}: {e}")
            return {}

    def get_weekly_roster_with_stats(self, team_id, week):
        """
        Get complete roster with player stats for a team in a specific week

        Args:
            team_id: Yahoo team ID
            week: Week number

        Returns:
            dict: Roster data with starters, bench, and actual points
        """
        try:
            # Get roster positions
            roster_list = self.lg.to_team(team_id).roster(week)

            if not roster_list:
                return {'starters': [], 'bench': [], 'total_starter_points': 0.0, 'total_bench_points': 0.0}

            # Collect all player IDs for batch stats query
            player_ids = [p.get('player_id') for p in roster_list if p.get('player_id')]

            # Get stats for all players in one API call
            player_stats = self.get_player_stats_for_week(player_ids, week)

            starters = []
            bench = []

            for player_data in roster_list:
                player_id = player_data.get('player_id', 0)
                stats = player_stats.get(player_id, {})

                player_info = {
                    'player_id': player_id,
                    'player_name': player_data.get('name', 'Unknown'),
                    'position': player_data.get('position_type', 'Unknown'),
                    'selected_position': player_data.get('selected_position', 'BN'),
                    'eligible_positions': player_data.get('eligible_positions', []),
                    'status': player_data.get('status', ''),  # Q/D/O/IR injury status
                    'actual_points': stats.get('points', 0.0),
                    'stats_detail': stats.get('stats', {})
                }

                # Check if starter or bench
                if player_data.get('selected_position') == 'BN':
                    bench.append(player_info)
                else:
                    starters.append(player_info)

            return {
                'starters': starters,
                'bench': bench,
                'total_starter_points': sum(p['actual_points'] for p in starters),
                'total_bench_points': sum(p['actual_points'] for p in bench),
            }

        except Exception as e:
            print(f"      Error fetching roster+stats for team {team_id} week {week}: {e}")
            import traceback
            traceback.print_exc()
            return {'starters': [], 'bench': [], 'total_starter_points': 0.0, 'total_bench_points': 0.0}

    def get_transactions(self):
        """
        Get all transactions for the season

        Returns:
            list of dict: Transaction history with FAAB data
        """
        print("Fetching transaction history...")

        try:
            # Get all transaction types (add, drop, trade)
            # count=1000 should cover entire season
            transactions = self.lg.transactions('add,drop,trade', 1000)

            transaction_list = []
            for trans in transactions:
                trans_data = {
                    'transaction_id': trans.get('transaction_id', ''),
                    'type': trans.get('type', 'unknown'),
                    'timestamp': int(trans.get('timestamp', 0)),
                    'status': trans.get('status', ''),
                    'faab_bid': trans.get('faab_bid', None),
                    'players': []
                }

                # Parse players involved
                # Structure: players -> {0, 1, 2...} -> player -> [[metadata], {transaction_data}]
                players_dict = trans.get('players', {})

                for key in players_dict:
                    if key == 'count':
                        continue

                    player_obj = players_dict[key].get('player', [])
                    if len(player_obj) >= 2:
                        # player_obj[0] is metadata list
                        # player_obj[1] is transaction_data
                        metadata = player_obj[0]
                        transaction_data = player_obj[1].get('transaction_data', [])

                        # Extract player name from metadata
                        player_name = None
                        player_id = None
                        position = None
                        for item in metadata:
                            if isinstance(item, dict):
                                if 'name' in item:
                                    player_name = item['name'].get('full', 'Unknown')
                                if 'player_id' in item:
                                    player_id = item['player_id']
                                if 'display_position' in item:
                                    position = item['display_position']

                        # Extract transaction details
                        for td in transaction_data:
                            if isinstance(td, dict):
                                trans_data['players'].append({
                                    'player_name': player_name,
                                    'player_id': player_id,
                                    'position': position,
                                    'type': td.get('type'),  # 'add' or 'drop'
                                    'source_type': td.get('source_type'),  # 'waivers', 'freeagents'
                                    'destination_team_key': td.get('destination_team_key'),
                                    'destination_team_name': td.get('destination_team_name'),
                                })

                transaction_list.append(trans_data)

            print(f"✓ Found {len(transaction_list)} transactions")
            return transaction_list

        except Exception as e:
            print(f"Error fetching transactions: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_draft_results(self):
        """
        Get complete draft results

        Returns:
            list of dict: Draft picks
        """
        print("Fetching draft results...")

        try:
            draft_results = self.lg.draft_results()

            draft_picks = []
            for pick in draft_results:
                # Extract player info
                player_id = pick.get('player_id', 0)

                # Get player name from API response
                # The API sometimes has player data in different places
                player_name = 'Unknown'
                position = 'Unknown'

                # Try to get from pick dict directly
                if 'player_key' in pick:
                    player_id = pick.get('player_key', player_id)

                pick_data = {
                    'round': pick.get('round', 0),
                    'pick': pick.get('pick', 0),
                    'overall_pick': (pick.get('round', 1) - 1) * 14 + pick.get('pick', 0),  # 14 teams
                    'team_id': pick.get('team_key', ''),
                    'team_key': pick.get('team_key', ''),
                    'player_id': str(player_id),
                    'player_name': player_name,  # Will be enriched later if needed
                    'position': position,
                    'cost': int(pick.get('cost', 1)),  # Auction cost
                }
                draft_picks.append(pick_data)

            # Sort by overall pick
            draft_picks.sort(key=lambda x: x['overall_pick'])

            print(f"✓ Found {len(draft_picks)} draft picks")
            return draft_picks

        except Exception as e:
            print(f"Error fetching draft results: {e}")
            return []

    def get_matchups(self, week):
        """
        Get all matchups for a specific week

        Args:
            week: Week number

        Returns:
            list of dict: Matchup data
        """
        try:
            # matchups() returns a dict with raw JSON from Yahoo API
            # Note: There is no scoreboard() method - use matchups()
            scoreboard_data = self.lg.matchups(week)
            matchups = []

            # The structure is: fantasy_content -> league[1] -> scoreboard -> 0 -> matchups
            matchups_dict = None

            if 'fantasy_content' in scoreboard_data:
                league_data = scoreboard_data['fantasy_content'].get('league', [])
                if len(league_data) > 1 and isinstance(league_data[1], dict):
                    scoreboard = league_data[1].get('scoreboard', {})
                    if '0' in scoreboard:
                        matchups_dict = scoreboard['0'].get('matchups', {})

            if not matchups_dict:
                print(f"No matchups found for week {week}")
                return []

            # matchups_dict is a dict with numeric string keys: {'0': {matchup}, '1': {matchup}, ...}
            # Also contains 'count' field which is an int - filter it out
            matchups_list = [v for v in matchups_dict.values() if isinstance(v, dict)]

            # Parse each matchup
            for matchup_obj in matchups_list:
                # Each matchup has structure: {'matchup': {...}}
                matchup_data = matchup_obj.get('matchup', {})

                # Teams are under matchup_data['0']['teams']
                if '0' not in matchup_data or 'teams' not in matchup_data['0']:
                    continue

                teams_dict = matchup_data['0']['teams']

                # Extract both teams
                teams_in_matchup = []
                for team_key in ['0', '1']:
                    if team_key in teams_dict:
                        team_array = teams_dict[team_key].get('team', [])
                        if len(team_array) >= 2:
                            metadata_list = team_array[0]
                            points_obj = team_array[1]

                            # Extract team_key from metadata
                            team_id_str = None
                            for item in metadata_list:
                                if isinstance(item, dict) and 'team_key' in item:
                                    team_id_str = item['team_key']
                                    break

                            teams_in_matchup.append({
                                'team_key': team_id_str,
                                'points_obj': points_obj
                            })

                if len(teams_in_matchup) >= 2:
                    team1 = teams_in_matchup[0]
                    team2 = teams_in_matchup[1]

                    team1_key = team1['team_key']
                    team1_points = float(team1['points_obj'].get('team_points', {}).get('total', 0.0))

                    team2_key = team2['team_key']
                    team2_points = float(team2['points_obj'].get('team_points', {}).get('total', 0.0))

                    # Determine winner
                    if team1_points > team2_points:
                        winner = team1_key
                    elif team2_points > team1_points:
                        winner = team2_key
                    else:
                        winner = 'TIE'

                    matchup = {
                        'week': week,
                        'team1_id': team1_key,
                        'team1_points': team1_points,
                        'team2_id': team2_key,
                        'team2_points': team2_points,
                        'winner': winner,
                    }
                    matchups.append(matchup)

            return matchups

        except Exception as e:
            print(f"Error fetching week {week} matchups: {e}")
            import traceback
            traceback.print_exc()
            return []

    def calculate_optimal_lineup(self, roster_data):
        """
        Calculate optimal lineup for a given week

        Args:
            roster_data: Output from get_weekly_roster()

        Returns:
            dict: Optimal lineup analysis
        """
        starters = roster_data.get('starters', [])
        bench = roster_data.get('bench', [])

        # Simple approach: find bench players who scored more than starters
        bench_mistakes = []

        for bench_player in bench:
            for starter in starters:
                # Only compare same positions (or flex-eligible)
                if bench_player['actual_points'] > starter['actual_points']:
                    mistake = {
                        'benched_player': bench_player['player_name'],
                        'benched_points': bench_player['actual_points'],
                        'started_player': starter['player_name'],
                        'started_points': starter['actual_points'],
                        'point_differential': bench_player['actual_points'] - starter['actual_points'],
                    }
                    bench_mistakes.append(mistake)
                    break  # Only count each bench player once

        # Calculate optimal points (actual starters + best bench swaps)
        optimal_points = roster_data.get('total_starter_points', 0.0)
        for mistake in bench_mistakes:
            optimal_points += mistake['point_differential']

        return {
            'optimal_points': optimal_points,
            'actual_points': roster_data.get('total_starter_points', 0.0),
            'bench_mistakes': bench_mistakes,
            'points_left_on_bench': sum(m['point_differential'] for m in bench_mistakes),
        }

    def pull_complete_season_data(self):
        """
        Master function: Pull all data needed for Fantasy Wrapped

        Returns:
            dict: Complete structured data for entire season
        """
        print("\n" + "="*60)
        print("FANTASY RECKONING DATA PULLER")
        print("="*60 + "\n")

        # Get league metadata
        league_metadata = self.get_league_metadata()
        current_week = league_metadata.get('current_week', 14)

        # Get all teams
        all_teams = self.get_all_teams()

        # Get weekly data for each team
        print(f"\nFetching weekly data for weeks 1-{current_week}...")
        weekly_data = {}

        for team in all_teams:
            team_id = team['team_id']
            print(f"\n  Processing {team['team_name']}...")
            weekly_data[team_id] = {}

            for week in range(1, current_week + 1):
                print(f"    Week {week}...", end=" ")

                # Get scores
                scores = self._make_api_call_with_delay(
                    self.get_weekly_scores, team_id, week
                )

                # Get roster with player stats (includes bench points and injury status)
                roster = self._make_api_call_with_delay(
                    self.get_weekly_roster_with_stats, team_id, week
                )

                # Calculate optimal lineup
                optimal = self.calculate_optimal_lineup(roster) if roster else {}

                # Combine data
                week_data = scores or {}
                week_data['roster'] = roster
                week_data['optimal_lineup'] = optimal
                week_data['bench_points'] = roster.get('total_bench_points', 0.0) if roster else 0.0

                weekly_data[team_id][f'week_{week}'] = week_data
                print("✓")

        # Get transactions
        transactions = self.get_transactions()

        # Get draft results
        draft = self.get_draft_results()

        # Compile complete data
        complete_data = {
            'league': league_metadata,
            'teams': all_teams,
            'weekly_data': weekly_data,
            'transactions': transactions,
            'draft': draft,
            'generated_at': datetime.now().isoformat(),
        }

        print("\n" + "="*60)
        print("DATA EXTRACTION COMPLETE!")
        print("="*60)

        return complete_data

    def save_to_json(self, data, filename=None):
        """
        Save extracted data to JSON file

        Args:
            data: Data dictionary to save
            filename: Output filename (optional)
        """
        if filename is None:
            filename = f'league_{self.league_id}_{self.season_year}.json'

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Data saved to: {filename}")


def main():
    """
    Main execution function
    """
    # Load credentials from environment
    league_id = os.getenv('LEAGUE_ID')
    season = int(os.getenv('SEASON_YEAR', 2024))

    if not league_id:
        print("ERROR: Please set LEAGUE_ID in your .env file")
        return

    print(f"League ID: {league_id}")
    print(f"Season: {season}\n")

    # Initialize puller
    puller = FantasyWrappedDataPuller(league_id, season)

    # Authenticate
    puller.authenticate()

    # Pull all data
    complete_data = puller.pull_complete_season_data()

    # Save to file
    puller.save_to_json(complete_data)

    print("\n✓ Ready for Fantasy Reckoning analysis!")


if __name__ == "__main__":
    main()
