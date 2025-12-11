"""
Fantasy Reckoning - Metrics Calculator
Generates 5 personalized cards for each manager

Universal support for ANY Yahoo Fantasy Football league:
- Auction and Snake drafts
- Any league size (8, 10, 12, 14+ teams)
- Dynamic roster configuration
- Head-to-head and points-only scoring
"""

import json
import os
import glob
import argparse
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional


class FantasyWrappedCalculator:
    """
    Main calculator class for Fantasy Reckoning metrics
    Supports any Yahoo Fantasy Football league configuration
    """

    def __init__(self, data_file: Optional[str] = None):
        """
        Load and parse league data

        Args:
            data_file: Path to league JSON file. If None, auto-detects most recent file.
        """
        # Auto-detect data file if not provided
        if data_file is None:
            data_file = self._find_latest_league_file()
            print(f"Auto-detected league file: {data_file}")

        # Load data
        print(f"Loading league data from: {data_file}")
        with open(data_file, 'r') as f:
            self.data = json.load(f)

        # Parse core data
        self.league = self.data['league']
        self.teams = {t['team_key']: t for t in self.data['teams']}
        self.weekly_data = self.data['weekly_data']
        self.transactions = self.data.get('transactions', [])
        self.draft = self.data.get('draft', [])

        # Detect league configuration
        self.draft_type = self._detect_draft_type()
        self.roster_config = self._detect_roster_configuration()
        self.scoring_type = self.league.get('scoring_type', 'head')

        # Validate league compatibility
        self._validate_league()

        # Build helper indices
        self._build_indices()

        # Print league info
        self._print_league_summary()

    def _find_latest_league_file(self) -> str:
        """
        Auto-detect the most recent league data file

        Returns:
            Path to most recent league_*.json file

        Raises:
            FileNotFoundError: If no league files found
        """
        # Look for league_*.json files
        league_files = glob.glob('league_*.json')

        if not league_files:
            raise FileNotFoundError(
                "No league data files found. Please run data_puller.py first or specify --data parameter."
            )

        # Sort by modification time (most recent first)
        league_files.sort(key=os.path.getmtime, reverse=True)

        return league_files[0]

    def _detect_draft_type(self) -> str:
        """
        Detect if league used auction or snake draft

        Returns:
            'auction' or 'snake'
        """
        if not self.draft:
            return 'unknown'

        # Check if any draft pick has cost > $1 (auction indicator)
        has_auction_costs = any(pick.get('cost', 1) > 1 for pick in self.draft)

        if has_auction_costs:
            return 'auction'

        # Check for auction budget in team data
        has_auction_budget = any(
            team.get('auction_budget_total', 0) > 0
            for team in self.teams.values()
        )

        if has_auction_budget:
            return 'auction'

        return 'snake'

    def _detect_roster_configuration(self) -> Dict:
        """
        Detect league's roster configuration from actual roster data

        Returns:
            Dict with num_starters and position breakdown
        """
        if not self.weekly_data:
            return {'num_starters': 10, 'positions': {}}

        # Sample first week of first team to get roster structure
        first_team = list(self.weekly_data.keys())[0]
        week_keys = list(self.weekly_data[first_team].keys())

        if not week_keys:
            return {'num_starters': 10, 'positions': {}}

        sample_week = self.weekly_data[first_team][week_keys[0]]
        starters = sample_week.get('roster', {}).get('starters', [])

        num_starters = len(starters)

        # Count positions
        positions = {}
        for player in starters:
            pos = player.get('selected_position', 'FLEX')
            positions[pos] = positions.get(pos, 0) + 1

        return {
            'num_starters': num_starters,
            'positions': positions
        }

    def _validate_league(self):
        """
        Validate league data and check compatibility
        Sets feature flags based on available data

        Raises:
            ValueError: If league has critical compatibility issues
        """
        errors = []
        warnings = []

        # Initialize feature flags
        self.has_draft_data = bool(self.draft and len(self.draft) > 0)
        self.has_roster_positions = 'roster_positions' in self.league
        self.has_scoring_settings = 'stat_modifiers' in self.league
        self.supports_superflex = False
        self.supports_idp = False
        self.has_waiver_data = bool(self.transactions)

        # Check required data
        if not self.teams:
            errors.append("No team data found. Cannot generate Fantasy Reckoning.")

        if self.league.get('num_teams', 0) < 4:
            errors.append(f"League has only {self.league.get('num_teams', 0)} teams. Minimum 4 required.")

        if not self.weekly_data:
            errors.append("No weekly data found. Cannot calculate metrics.")

        # Check draft data
        if not self.has_draft_data:
            warnings.append("No draft data found (offline/keeper draft). Card 1 will be unavailable.")

        # Check roster configuration
        if not self.has_roster_positions:
            warnings.append("Roster positions unavailable - using defaults from weekly data.")
        else:
            # Check for special formats
            roster = self.league.get('roster_positions', {})

            # Detect superflex
            flex_positions = [k for k in roster.keys() if '/' in k and 'Q' in k]
            has_dedicated_qb = 'QB' in roster
            is_true_superflex = flex_positions and (not has_dedicated_qb or len(flex_positions) > 1)

            if is_true_superflex:
                self.supports_superflex = True
                warnings.append("Superflex/2QB detected - QB scarcity values may be approximate.")

            # Detect IDP
            idp_positions = [k for k in roster.keys() if k in ['DL', 'LB', 'DB']]
            if idp_positions:
                self.supports_idp = True
                warnings.append(f"IDP positions detected: {idp_positions} - not fully supported yet.")

        # Check scoring settings
        if not self.has_scoring_settings:
            warnings.append("Scoring settings unavailable - assuming standard PPR scoring.")

        # Check for special league types
        league_name = self.league.get('name', '').lower()
        special_formats = {
            'guillotine': 'Guillotine format not yet supported',
            'best ball': 'Best Ball format not yet supported',
            'empire': 'Empire format not yet supported'
        }

        for keyword, warning in special_formats.items():
            if keyword in league_name:
                errors.append(warning)

        # Check scoring type
        if self.scoring_type == 'points':
            warnings.append("Points-only league - some head-to-head metrics unavailable.")

        # Check transaction data
        if not self.has_waiver_data:
            warnings.append("No transaction data - Card 4 ecosystem analysis limited.")

        # Raise errors if any
        if errors:
            error_msg = "League compatibility issues:\n" + "\n".join(f"  ❌ {e}" for e in errors)
            raise ValueError(error_msg)

        # Print warnings if any
        if warnings:
            print("\n" + "="*70)
            print("⚠️  COMPATIBILITY WARNINGS")
            print("="*70)
            for w in warnings:
                print(f"  • {w}")
            print("="*70 + "\n")

    def _print_league_summary(self):
        """Print summary of detected league configuration"""
        print("\n" + "="*70)
        print("LEAGUE CONFIGURATION")
        print("="*70)
        print(f"League: {self.league.get('name', 'Unknown')}")
        print(f"Season: {self.league.get('season', 'Unknown')}")
        print(f"Teams: {len(self.teams)}")
        print(f"Draft Type: {self.draft_type.upper()}")
        print(f"Scoring: {self.scoring_type.upper()}")
        print(f"Roster Size: {self.roster_config['num_starters']} starters")
        if self.roster_config['positions']:
            print(f"Positions: {', '.join(f'{k}({v})' for k, v in self.roster_config['positions'].items())}")
        print("="*70 + "\n")

    def _build_indices(self):
        """Build lookup indices for fast data access"""
        # Draft picks by team
        self.draft_by_team = defaultdict(list)
        for pick in self.draft:
            self.draft_by_team[pick['team_key']].append(pick)

        # Transactions by team
        self.transactions_by_team = defaultdict(list)
        for trans in self.transactions:
            for player in trans.get('players', []):
                team_key = player.get('destination_team_key')
                if team_key:
                    self.transactions_by_team[team_key].append(trans)

        # Player points by week (for ROS calculations)
        self.player_points_by_week = defaultdict(lambda: defaultdict(float))
        # Player ID to name mapping
        self.player_names = {}
        for team_key, weeks in self.weekly_data.items():
            for week_key, week_data in weeks.items():
                roster = week_data.get('roster', {})
                for player in roster.get('starters', []) + roster.get('bench', []):
                    player_id = str(player['player_id'])
                    week_num = int(week_key.split('_')[1])
                    self.player_points_by_week[player_id][week_num] = player['actual_points']
                    # Store player name if we don't have it yet
                    if player_id not in self.player_names:
                        self.player_names[player_id] = player.get('player_name', f'Player {player_id}')

    def get_regular_season_weeks(self) -> range:
        """
        Get range of regular season weeks (excluding playoffs)

        Returns:
            range object for regular season weeks (e.g., range(1, 15) for weeks 1-14)
        """
        playoff_start = int(self.league.get('playoff_start_week', 15))
        current_week = int(self.league.get('current_week', 14))

        # Regular season is up to (but not including) playoff start
        last_reg_season_week = min(playoff_start - 1, current_week)

        return range(1, last_reg_season_week + 1)

    def get_ros_points(self, player_id: str, start_week: int) -> float:
        """
        Calculate Rest of Season points for a player starting from a given week

        Args:
            player_id: Player ID
            start_week: Week to start counting from (exclusive)

        Returns:
            Total points scored from week start_week+1 through end of season
        """
        total = 0.0
        current_week = self.league['current_week']

        for week in range(start_week + 1, current_week + 1):
            total += self.player_points_by_week[player_id].get(week, 0.0)

        return total

    def get_rostered_players(self, week: int) -> set:
        """
        Get all player IDs that were rostered in a given week

        Args:
            week: Week number

        Returns:
            Set of player IDs on rosters that week
        """
        rostered = set()
        week_key = f'week_{week}'

        for team_key in self.weekly_data:
            if week_key in self.weekly_data[team_key]:
                roster = self.weekly_data[team_key][week_key].get('roster', {})
                for player in roster.get('starters', []) + roster.get('bench', []):
                    rostered.add(str(player['player_id']))

        return rostered

    def get_available_fas(self, week: int, position: str = None) -> List[Tuple[str, float]]:
        """
        Get available free agents at a given week with their ROS points

        Args:
            week: Week number
            position: Optional position filter

        Returns:
            List of (player_id, ros_points) tuples for available players
        """
        rostered = self.get_rostered_players(week)
        available = []

        # Get all players who scored points that season
        for player_id, weeks_dict in self.player_points_by_week.items():
            if player_id not in rostered:
                ros_points = self.get_ros_points(player_id, week)
                if ros_points > 0:
                    available.append((player_id, ros_points))

        # Sort by ROS points descending
        available.sort(key=lambda x: x[1], reverse=True)

        return available

    def calculate_replacement_levels(self) -> Dict[str, float]:
        """
        Calculate position-specific replacement level points based on league settings

        Uses league roster configuration to determine replacement bands:
        - band_start = (teams × starters_at_position) + flex_allocation + 1
        - replacement = average seasonal PPG of players in replacement band

        Returns:
            Dict mapping position to replacement level PPG
            e.g., {'QB': 15.2, 'RB': 8.4, 'WR': 9.1, 'TE': 4.3}
        """
        num_teams = len(self.teams)

        # Get starting positions from league settings
        roster_positions = self.league.get('roster_positions', {})

        # Default starters if not in league settings
        default_starters = {
            'QB': 1,
            'RB': 2,
            'WR': 2,
            'TE': 1,
            'K': 1,
            'DEF': 1
        }

        starters = {}
        for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            starters[pos] = roster_positions.get(pos, default_starters.get(pos, 0))

        # Estimate flex allocation from actual weekly rosters
        # Sample several weeks to see which positions fill flex spots
        flex_usage = self._estimate_flex_allocation()

        # Calculate replacement levels for each position
        replacement_levels = {}

        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            # Calculate band start: (teams × starters) + flex_share + 1
            starters_at_pos = starters[position]
            flex_share = flex_usage.get(position, 0)
            band_start = int((num_teams * starters_at_pos) + flex_share) + 1

            # Band size = approximately same as number of starters
            # (represents "next tier" of players)
            band_size = max(int(num_teams * starters_at_pos), 1)

            # Get all players at this position with their season totals
            players_at_position = []
            for player_id, weeks_dict in self.player_points_by_week.items():
                # Determine player position
                player_pos = self._get_player_primary_position(player_id)

                if player_pos == position:
                    # Calculate total points and games played
                    total_points = sum(weeks_dict.values())
                    games_played = len([pts for pts in weeks_dict.values() if pts > 0])

                    if games_played > 0:
                        ppg = total_points / games_played
                        players_at_position.append({
                            'player_id': player_id,
                            'total_points': total_points,
                            'games_played': games_played,
                            'ppg': ppg
                        })

            # Sort by total points (season-long value)
            players_at_position.sort(key=lambda x: x['total_points'], reverse=True)

            # Get replacement band
            if len(players_at_position) >= band_start + band_size:
                replacement_band = players_at_position[band_start:band_start + band_size]
                # Average PPG of replacement band
                replacement_ppg = sum(p['ppg'] for p in replacement_band) / len(replacement_band)
            elif len(players_at_position) >= band_start:
                # Not enough for full band, use what's available
                replacement_band = players_at_position[band_start:]
                replacement_ppg = sum(p['ppg'] for p in replacement_band) / len(replacement_band) if replacement_band else 0
            else:
                # Position is very scarce, use bottom 25% as proxy
                if players_at_position:
                    bottom_quartile = players_at_position[int(len(players_at_position) * 0.75):]
                    replacement_ppg = sum(p['ppg'] for p in bottom_quartile) / len(bottom_quartile) if bottom_quartile else 0
                else:
                    replacement_ppg = 0

            replacement_levels[position] = round(replacement_ppg, 2)

        return replacement_levels

    def _estimate_flex_allocation(self) -> Dict[str, float]:
        """
        Estimate how flex spots are allocated across RB/WR/TE by sampling actual rosters

        Returns:
            Dict mapping position to average flex spots used by that position
            e.g., {'RB': 4.8, 'WR': 6.0, 'TE': 1.2} in 12-team with 1 flex
        """
        flex_counts = {'RB': 0, 'WR': 0, 'TE': 0}
        sample_count = 0

        # Sample up to 5 weeks for each team
        for team_key in list(self.weekly_data.keys())[:min(len(self.weekly_data), 12)]:
            team_weeks = self.weekly_data[team_key]
            for week_key in list(team_weeks.keys())[:5]:
                week_data = team_weeks[week_key]
                roster = week_data.get('roster', {})
                starters = roster.get('starters', [])

                for player in starters:
                    selected_pos = player.get('selected_position', '')

                    # Check if this is a flex position
                    if selected_pos in ['FLEX', 'W/R/T', 'W/R', 'W/T', 'R/T']:
                        # Get player's actual position
                        eligible = player.get('eligible_positions', [])
                        if 'RB' in eligible:
                            flex_counts['RB'] += 1
                        elif 'WR' in eligible:
                            flex_counts['WR'] += 1
                        elif 'TE' in eligible:
                            flex_counts['TE'] += 1

                        sample_count += 1

        # Convert counts to averages
        if sample_count > 0:
            num_teams = len(self.teams)
            weeks_sampled = 5
            total_samples = num_teams * weeks_sampled

            return {
                'RB': flex_counts['RB'] / total_samples * num_teams if total_samples > 0 else 0,
                'WR': flex_counts['WR'] / total_samples * num_teams if total_samples > 0 else 0,
                'TE': flex_counts['TE'] / total_samples * num_teams if total_samples > 0 else 0
            }

        # Default estimates if no flex data (assume standard flex distribution)
        return {'RB': 0.4 * len(self.teams), 'WR': 0.5 * len(self.teams), 'TE': 0.1 * len(self.teams)}

    def _get_player_primary_position(self, player_id: str) -> str:
        """
        Get a player's primary position by checking their most common roster position

        Args:
            player_id: Player ID

        Returns:
            Position string (QB, RB, WR, TE, K, DEF)
        """
        position_counts = {}

        # Check all weeks/teams to find this player
        for team_key in self.weekly_data:
            for week_key in self.weekly_data[team_key]:
                week_data = self.weekly_data[team_key][week_key]
                roster = week_data.get('roster', {})

                # Check starters and bench
                for player in roster.get('starters', []) + roster.get('bench', []):
                    if str(player.get('player_id')) == str(player_id):
                        # Get eligible positions
                        eligible = player.get('eligible_positions', [])
                        if eligible:
                            # Use first eligible position as primary
                            primary = eligible[0]
                            position_counts[primary] = position_counts.get(primary, 0) + 1

        # Return most common position
        if position_counts:
            return max(position_counts, key=position_counts.get)

        # Default fallback
        return 'FLEX'

    def calculate_optimal_lineup(self, roster: Dict, filter_injured: bool = True) -> Dict:
        """
        Calculate optimal lineup for a given roster

        Args:
            roster: Roster dict with starters and bench
            filter_injured: If True, exclude Q/D/O/IR players

        Returns:
            Dict with optimal_points, bench_mistakes, etc.
        """
        all_players = roster.get('starters', []) + roster.get('bench', [])

        # Filter out injured if requested
        if filter_injured:
            available_players = [
                p for p in all_players
                if not p.get('status') or p.get('status') not in ['Q', 'D', 'O', 'IR']
            ]
        else:
            available_players = all_players

        # Simple optimal: take highest scoring players
        # TODO: Account for position constraints (QB/RB/WR/TE/FLEX)
        available_players.sort(key=lambda x: x['actual_points'], reverse=True)

        # Use ACTUAL number of starters from this specific roster (not global config)
        # This handles weeks where roster size varies (injuries, IR slots, etc.)
        actual_starters = roster.get('starters', [])
        num_starters = len(actual_starters)

        optimal_starters = available_players[:num_starters]
        optimal_points = sum(p['actual_points'] for p in optimal_starters)

        # Calculate actual points
        actual_points = sum(p['actual_points'] for p in actual_starters)

        return {
            'optimal_points': optimal_points,
            'actual_points': actual_points,
            'points_left_on_bench': optimal_points - actual_points,
            'efficiency_pct': (actual_points / optimal_points * 100) if optimal_points > 0 else 0
        }

    def generate_all_cards(self) -> Dict:
        """
        Generate all 5 cards for all managers

        Returns:
            Dict mapping manager names to their card data
        """
        results = {}

        for team_key, team in self.teams.items():
            manager_name = team['manager_name']
            print(f"\nGenerating cards for {manager_name}...")

            cards = {
                'manager_id': team_key,
                'manager_name': manager_name,
                'season': self.league['season'],
                'league': self.league['name'],
                'cards': {}
            }

            # Generate each card
            try:
                cards['cards']['card_1_draft'] = self.calculate_card_1(team_key)
                print(f"  ✓ Card 1: The Draft")
            except Exception as e:
                print(f"  ✗ Card 1 failed: {e}")
                cards['cards']['card_1_draft'] = {'error': str(e)}

            try:
                cards['cards']['card_2_identity'] = self.calculate_card_2(team_key)
                print(f"  ✓ Card 2: The Identity")
            except Exception as e:
                print(f"  ✗ Card 2 failed: {e}")
                cards['cards']['card_2_identity'] = {'error': str(e)}

            try:
                cards['cards']['card_3_inflection'] = self.calculate_card_3(team_key)
                print(f"  ✓ Card 3: Inflection Points")
            except Exception as e:
                print(f"  ✗ Card 3 failed: {e}")
                cards['cards']['card_3_inflection'] = {'error': str(e)}

            try:
                cards['cards']['card_4_ecosystem'] = self.calculate_card_4(team_key)
                print(f"  ✓ Card 4: The Ecosystem")
            except Exception as e:
                print(f"  ✗ Card 4 failed: {e}")
                cards['cards']['card_4_ecosystem'] = {'error': str(e)}

            try:
                cards['cards']['card_5_accounting'] = self.calculate_card_5(team_key, cards['cards'])
                print(f"  ✓ Card 5: The Accounting")
            except Exception as e:
                print(f"  ✗ Card 5 failed: {e}")
                cards['cards']['card_5_accounting'] = {'error': str(e)}

            cards['generated_at'] = datetime.now().isoformat()
            results[manager_name] = cards

        return results

    def calculate_card_1(self, team_key: str) -> Dict:
        """Card 1: The Draft - ROI, steals, busts"""
        from card_1_draft import calculate_card_1_draft
        return calculate_card_1_draft(self, team_key)

    def calculate_card_2(self, team_key: str) -> Dict:
        """Card 2: The Identity - Archetype and parallel timelines"""
        from card_2_identity import calculate_card_2_identity
        return calculate_card_2_identity(self, team_key)

    def calculate_card_3(self, team_key: str) -> Dict:
        """Card 3: Inflection Points - Pivotal moments"""
        from card_3_inflection import calculate_card_3_inflection
        return calculate_card_3_inflection(self, team_key)

    def calculate_card_4(self, team_key: str) -> Dict:
        """Card 4: The Ecosystem - Drops and lost bids that helped rivals"""
        from card_4_ecosystem import calculate_card_4_ecosystem
        return calculate_card_4_ecosystem(self, team_key)

    def calculate_card_5(self, team_key: str, other_cards: Dict) -> Dict:
        """Card 5: The Accounting - Win/loss attribution"""
        from card_5_accounting import calculate_card_5_accounting
        return calculate_card_5_accounting(self, team_key, other_cards)


def main():
    """Main execution with CLI argument support"""
    parser = argparse.ArgumentParser(
        description='Fantasy Reckoning - Generate personalized analytics for Yahoo Fantasy Football leagues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect most recent league file
  python fantasy_wrapped_calculator.py

  # Specify a league data file
  python fantasy_wrapped_calculator.py --data league_908221_2025.json

  # Use team names in output files (recommended)
  python fantasy_wrapped_calculator.py --use-team-names
        """
    )

    parser.add_argument(
        '--data',
        type=str,
        help='Path to league data JSON file (auto-detects if not specified)'
    )

    parser.add_argument(
        '--use-team-names',
        action='store_true',
        help='Use team names instead of manager names for output files'
    )

    args = parser.parse_args()

    print('='*70)
    print('FANTASY RECKONING - METRICS CALCULATOR')
    print('='*70)

    # Initialize calculator
    calc = FantasyWrappedCalculator(data_file=args.data)

    print(f"\nGenerating Fantasy Reckoning for {len(calc.teams)} teams...")
    print(f"Current Week: {calc.league['current_week']}\n")

    # Generate all cards
    results = calc.generate_all_cards()

    # Save individual files for each manager/team
    for manager_name, cards in results.items():
        # Determine filename based on preference
        if args.use_team_names:
            # Use team name from the cards data
            team_key = cards['manager_id']
            team_name = calc.teams[team_key]['team_name']
            # Clean team name for filename
            clean_name = team_name.lower()
            clean_name = ''.join(c if c.isalnum() or c == ' ' else '' for c in clean_name)
            clean_name = clean_name.replace(' ', '_')
            filename = f"fantasy_wrapped_{clean_name}.json"
        else:
            # Use manager name (original behavior)
            filename = f"fantasy_wrapped_{manager_name.replace(' ', '_').lower()}.json"

        with open(filename, 'w') as f:
            json.dump(cards, f, indent=2)
        print(f"✓ Saved: {filename}")

    print('\n' + '='*70)
    print('FANTASY RECKONING GENERATION COMPLETE!')
    print('='*70)
    print(f"\n📊 Generated {len(results)} personalized reports")
    print(f"🏈 League: {calc.league['name']}")
    print(f"📅 Season: {calc.league['season']}")
    print(f"✨ Draft Type: {calc.draft_type.upper()}")
    print()


if __name__ == '__main__':
    main()
