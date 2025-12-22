"""
Fantasy Reckoning - Metrics Calculator
Generates 4 personalized cards for each manager

4-Card Structure:
  Card 1: The Leader - How you played and stacked up against your rivals
  Card 2: The Ledger - Where your points came from (and where they went)
  Card 3: The Lineup - How you deployed your roster in battle
  Card 4: The Legend - The story of your season, where fate and folly intertwined

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

    def calculate_team_stats_from_weekly_data(self, team_key: str) -> Dict:
        """
        Calculate team stats (PF, PA, Record) from weekly data instead of team summary.
        This ensures accuracy even if team summary data is stale.

        Args:
            team_key: Team key

        Returns:
            Dict with wins, losses, ties, points_for, points_against
        """
        regular_season_weeks = self.get_regular_season_weeks()

        wins = 0
        losses = 0
        ties = 0
        points_for = 0.0
        points_against = 0.0

        for week in regular_season_weeks:
            week_key = f'week_{week}'

            if week_key not in self.weekly_data.get(team_key, {}):
                continue

            week_data = self.weekly_data[team_key][week_key]
            team_score = week_data.get('actual_points', 0)
            opp_score = week_data.get('opponent_points', 0)

            # Accumulate points
            points_for += team_score
            points_against += opp_score

            # Determine result
            if team_score > opp_score:
                wins += 1
            elif team_score < opp_score:
                losses += 1
            else:
                ties += 1

        return {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'points_for': round(points_for, 2),
            'points_against': round(points_against, 2)
        }

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
        Generate all 4 cards for all managers

        Two-pass approach:
        1. Generate Cards 2-4 for all teams
        2. Assign archetypes at league level (max 3 per archetype)
        3. Generate Card 1 for all teams with assigned archetypes

        Returns:
            Dict mapping manager names to their card data
        """
        results = {}
        temp_cards = {}

        # PASS 1: Generate The Ledger, The Lineup, and The Legend for all teams
        print("\n=== PASS 1: Generating The Ledger, The Lineup, and The Legend ===")
        for team_key, team in self.teams.items():
            manager_name = team['manager_name']
            print(f"\n{manager_name}...")

            cards = {
                'manager_id': team_key,
                'manager_name': manager_name,
                'season': self.league['season'],
                'league': self.league['name'],
                'cards': {}
            }

            # Generate cards in order 2→3→4 (Card 1 comes later)
            try:
                cards['cards']['card_2_ledger'] = self.calculate_card_2(team_key)
                print(f"  ✓ The Ledger")
            except Exception as e:
                print(f"  ✗ The Ledger failed: {e}")
                cards['cards']['card_2_ledger'] = {'error': str(e)}

            try:
                cards['cards']['card_3_lineups'] = self.calculate_card_3(team_key)
                print(f"  ✓ The Lineup")
            except Exception as e:
                print(f"  ✗ The Lineup failed: {e}")
                cards['cards']['card_3_lineups'] = {'error': str(e)}

            try:
                cards['cards']['card_4_story'] = self.calculate_card_4(team_key, cards['cards'])
                print(f"  ✓ The Legend")
            except Exception as e:
                print(f"  ✗ The Legend failed: {e}")
                cards['cards']['card_4_story'] = {'error': str(e)}

            temp_cards[team_key] = cards

        # PASS 2: Assign archetypes at league level (max 3 per archetype)
        print("\n=== PASS 2: Assigning archetypes (max 3 per archetype) ===")
        from archetypes import assign_archetypes_for_league

        # Build other_cards_by_team dict for archetype assignment
        other_cards_by_team = {}
        for team_key, cards in temp_cards.items():
            other_cards_by_team[team_key] = cards['cards']

        # Assign archetypes across league with capacity constraints
        team_keys = list(self.teams.keys())
        archetype_assignments = assign_archetypes_for_league(self, team_keys, other_cards_by_team)

        # Print archetype distribution
        from collections import Counter
        archetype_counts = Counter(a['name'] for a in archetype_assignments.values())
        print("\nArchetype distribution:")
        for archetype_name, count in sorted(archetype_counts.items()):
            print(f"  {archetype_name}: {count} team(s)")

        # PASS 3: Generate The Leader for all teams with assigned archetypes
        print("\n=== PASS 3: Generating The Leader for all teams ===")
        for team_key, team in self.teams.items():
            manager_name = team['manager_name']
            cards = temp_cards[team_key]
            assigned_archetype = archetype_assignments[team_key]

            print(f"\nGenerating The Leader for {manager_name} ({assigned_archetype['name']})...")

            # Generate The Leader with assigned archetype
            try:
                cards['cards']['card_1_overview'] = self.calculate_card_1(
                    team_key,
                    cards['cards'],
                    assigned_archetype=assigned_archetype
                )
                print(f"  ✓ The Leader")
            except Exception as e:
                print(f"  ✗ The Leader failed: {e}")
                cards['cards']['card_1_overview'] = {'error': str(e)}

            cards['generated_at'] = datetime.now().isoformat()
            results[manager_name] = cards

        return results

    def calculate_card_1(self, team_key: str, other_cards: Dict = None, assigned_archetype: Dict = None) -> Dict:
        """Card 1: The Leader - How you played and stacked up against your rivals"""
        from card_1_overview import calculate_card_1_overview
        return calculate_card_1_overview(self, team_key, other_cards or {}, assigned_archetype)

    def calculate_card_2(self, team_key: str) -> Dict:
        """Card 2: The Ledger - Where your points came from (and where they went)"""
        from card_2_ledger import calculate_card_2_ledger
        return calculate_card_2_ledger(self, team_key)

    def calculate_card_3(self, team_key: str) -> Dict:
        """Card 3: The Lineup - How you deployed your roster in battle"""
        from card_3_lineups import calculate_card_3_lineups
        return calculate_card_3_lineups(self, team_key)

    def calculate_card_4(self, team_key: str, other_cards: Dict = None) -> Dict:
        """Card 4: The Legend - The story of your season, where fate and folly intertwined"""
        from card_4_story import calculate_card_4_story
        return calculate_card_4_story(self, team_key, other_cards)

    def calculate_spider_chart(self, team_key: str, all_cards: Dict) -> Dict:
        """
        Calculate 6-dimension spider chart for manager profile

        The Six Faces of Your Season:
        1. Draft - Preparation quality
        2. Lineups - Decision quality
        3. Waivers - Activity effectiveness
        4. Consistency - Week-to-week stability
        5. Luck - Schedule fortune
        6. Risk - Boom/bust tolerance

        Args:
            team_key: Team key
            all_cards: Dict containing Cards 1-5 data

        Returns:
            Dict with spider chart dimensions, percentiles, interpretation
        """
        import statistics

        team = self.teams[team_key]
        card_1 = all_cards.get('card_1_draft', self.calculate_card_1(team_key))
        card_2 = all_cards.get('card_2_identity', self.calculate_card_2(team_key))
        card_3 = all_cards.get('card_3_inflection', self.calculate_card_3(team_key))
        card_4 = all_cards.get('card_4_ecosystem', self.calculate_card_4(team_key))
        card_5 = all_cards.get('card_5_accounting', self.calculate_card_5(team_key, all_cards))

        num_teams = len(self.teams)
        regular_season_weeks = self.get_regular_season_weeks()

        # ====================
        # DIMENSION 1: DRAFT
        # ====================
        # Use VOR-based draft ranking
        if 'vor_analysis' in card_1:
            draft_rank = card_1.get('rank', num_teams // 2)
            draft_percentile = ((num_teams - draft_rank + 1) / num_teams) * 100
            draft_score = draft_percentile
        else:
            # Fallback to grade-based
            grade_map = {'A': 90, 'B': 75, 'C': 50, 'D': 30, 'F': 15}
            draft_score = grade_map.get(card_1.get('grade', 'C'), 50)

        # ====================
        # DIMENSION 2: LINEUPS
        # ====================
        lineup_efficiency = card_2['efficiency']['lineup_efficiency_pct']
        preventable_losses = card_3['insights'].get('preventable_losses', 0)

        # Penalty for preventable losses
        lineup_score = lineup_efficiency - (preventable_losses * 5)
        lineup_score = max(0, min(100, lineup_score))

        # ====================
        # DIMENSION 3: WAIVERS
        # ====================
        if 'waiver_efficiency' in card_4:
            efficiency_rate = card_4['waiver_efficiency']['efficiency_rate']
            transactions_per_week = card_2['archetype']['transactions_per_week']

            waiver_score = efficiency_rate

            # Bonus for high activity + high efficiency
            if transactions_per_week >= 2 and efficiency_rate >= 60:
                waiver_score += 10
            elif transactions_per_week >= 1 and efficiency_rate >= 50:
                waiver_score += 5

            # Penalty for inefficient churning
            if efficiency_rate < 30 and transactions_per_week >= 2:
                waiver_score *= 0.8

            waiver_score = max(0, min(100, waiver_score))
        else:
            # Fallback to transaction count percentile
            waiver_score = min(100, transactions_per_week * 15)

        # ====================
        # DIMENSION 4: CONSISTENCY
        # ====================
        # Calculate coefficient of variation for manager
        weekly_scores = []
        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key in self.weekly_data.get(team_key, {}):
                week_data = self.weekly_data[team_key][week_key]
                weekly_scores.append(week_data.get('actual_points', 0))

        if len(weekly_scores) >= 3:
            mean_score = statistics.mean(weekly_scores)
            std_dev = statistics.stdev(weekly_scores)
            manager_cv = std_dev / mean_score if mean_score > 0 else 0

            # Calculate league average CV
            all_cvs = []
            for tk in self.teams.keys():
                tk_scores = []
                for week in regular_season_weeks:
                    week_key = f'week_{week}'
                    if week_key in self.weekly_data.get(tk, {}):
                        tk_scores.append(self.weekly_data[tk][week_key].get('actual_points', 0))

                if len(tk_scores) >= 3:
                    tk_mean = statistics.mean(tk_scores)
                    tk_std = statistics.stdev(tk_scores)
                    tk_cv = tk_std / tk_mean if tk_mean > 0 else 0
                    all_cvs.append(tk_cv)

            league_avg_cv = statistics.mean(all_cvs) if all_cvs else 0.15

            # Lower CV = more consistent = higher score
            consistency_score = 100 - ((manager_cv / league_avg_cv) * 50)
            consistency_score = max(0, min(100, consistency_score))
        else:
            consistency_score = 50  # Default if not enough data

        # ====================
        # DIMENSION 5: LUCK
        # ====================
        actual_wins = card_5['actual_record']['wins']
        actual_losses = card_5['actual_record']['losses']

        # Calculate expected wins from points-for
        # Simple method: How many teams would you beat each week on average?
        expected_wins = 0
        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key not in self.weekly_data.get(team_key, {}):
                continue

            manager_score = self.weekly_data[team_key][week_key].get('actual_points', 0)

            # Count how many teams this score would beat this week
            teams_beaten = 0
            for tk in self.teams.keys():
                if tk == team_key:
                    continue
                if week_key in self.weekly_data.get(tk, {}):
                    opponent_score = self.weekly_data[tk][week_key].get('actual_points', 0)
                    if manager_score > opponent_score:
                        teams_beaten += 1

            # Expected win probability = teams beaten / (total teams - 1)
            expected_wins += teams_beaten / (num_teams - 1)

        win_luck = actual_wins - expected_wins

        # Convert to 0-100 scale (range typically -4 to +4)
        luck_score = 50 + (win_luck * 12.5)
        luck_score = max(0, min(100, luck_score))

        # ====================
        # DIMENSION 6: RISK TOLERANCE
        # ====================
        # Calculate average volatility of started players
        risk_scores_by_week = []

        for week in list(regular_season_weeks)[:min(len(list(regular_season_weeks)), 10)]:  # Sample first 10 weeks
            week_key = f'week_{week}'
            if week_key not in self.weekly_data.get(team_key, {}):
                continue

            starters = self.weekly_data[team_key][week_key].get('roster', {}).get('starters', [])

            week_risk = []
            for player in starters:
                player_id = str(player.get('player_id'))

                # Get player's weekly scores for CV calculation
                player_weeks = self.player_points_by_week.get(player_id, {})
                player_scores = [pts for pts in player_weeks.values() if pts > 0]

                if len(player_scores) >= 3:
                    p_mean = statistics.mean(player_scores)
                    p_std = statistics.stdev(player_scores)
                    player_cv = p_std / p_mean if p_mean > 0 else 0
                    week_risk.append(player_cv)

            if week_risk:
                risk_scores_by_week.append(statistics.mean(week_risk))

        if risk_scores_by_week:
            manager_avg_risk = statistics.mean(risk_scores_by_week)

            # Calculate league average risk
            league_risks = []
            for tk in list(self.teams.keys())[:num_teams]:  # All teams
                tk_risks = []
                for week in list(regular_season_weeks)[:5]:  # Sample 5 weeks
                    week_key = f'week_{week}'
                    if week_key not in self.weekly_data.get(tk, {}):
                        continue

                    starters = self.weekly_data[tk][week_key].get('roster', {}).get('starters', [])
                    for player in starters:
                        player_id = str(player.get('player_id'))
                        player_weeks = self.player_points_by_week.get(player_id, {})
                        player_scores = [pts for pts in player_weeks.values() if pts > 0]

                        if len(player_scores) >= 3:
                            p_mean = statistics.mean(player_scores)
                            p_std = statistics.stdev(player_scores)
                            player_cv = p_std / p_mean if p_mean > 0 else 0
                            tk_risks.append(player_cv)

                if tk_risks:
                    league_risks.append(statistics.mean(tk_risks))

            league_avg_risk = statistics.mean(league_risks) if league_risks else 0.25

            # Convert to 0-100 (higher CV = higher risk tolerance)
            risk_score = (manager_avg_risk / league_avg_risk) * 50
            risk_score = max(0, min(100, risk_score))
        else:
            risk_score = 50  # Default

        # ====================
        # AGGREGATE & INTERPRET
        # ====================
        dimensions = {
            'draft': round(draft_score, 1),
            'lineups': round(lineup_score, 1),
            'waivers': round(waiver_score, 1),
            'consistency': round(consistency_score, 1),
            'luck': round(luck_score, 1),
            'risk': round(risk_score, 1)
        }

        # Calculate percentile ranks (position in league relative to other managers)
        # For each dimension, calculate all teams' scores and rank this manager
        percentile_ranks = {}

        for dimension_name in dimensions.keys():
            # Get scores for all teams in this dimension
            all_scores = []

            for tk in self.teams.keys():
                # Calculate this dimension for this team
                # We need to recalculate minimally to get comparative scores
                if dimension_name == 'draft':
                    tk_card_1 = all_cards.get('card_1_draft') if tk == team_key else self.calculate_card_1(tk)
                    if 'vor_analysis' in tk_card_1:
                        tk_rank = tk_card_1.get('rank', num_teams // 2)
                        tk_score = ((num_teams - tk_rank + 1) / num_teams) * 100
                    else:
                        grade_map = {'A': 90, 'B': 75, 'C': 50, 'D': 30, 'F': 15}
                        tk_score = grade_map.get(tk_card_1.get('grade', 'C'), 50)
                    all_scores.append((tk, tk_score))

                elif dimension_name == 'lineups':
                    tk_card_2 = all_cards.get('card_2_identity') if tk == team_key else self.calculate_card_2(tk)
                    tk_card_3 = all_cards.get('card_3_inflection') if tk == team_key else self.calculate_card_3(tk)
                    tk_efficiency = tk_card_2['efficiency']['lineup_efficiency_pct']
                    tk_preventable = tk_card_3['insights'].get('preventable_losses', 0)
                    tk_score = max(0, min(100, tk_efficiency - (tk_preventable * 5)))
                    all_scores.append((tk, tk_score))

                elif dimension_name == 'waivers':
                    tk_card_2 = all_cards.get('card_2_identity') if tk == team_key else self.calculate_card_2(tk)
                    tk_card_4 = all_cards.get('card_4_ecosystem') if tk == team_key else self.calculate_card_4(tk)
                    if 'waiver_efficiency' in tk_card_4:
                        tk_eff_rate = tk_card_4['waiver_efficiency']['efficiency_rate']
                        tk_trans_per_week = tk_card_2['archetype']['transactions_per_week']
                        tk_score = tk_eff_rate
                        if tk_trans_per_week >= 2 and tk_eff_rate >= 60:
                            tk_score += 10
                        elif tk_trans_per_week >= 1 and tk_eff_rate >= 50:
                            tk_score += 5
                        if tk_eff_rate < 30 and tk_trans_per_week >= 2:
                            tk_score *= 0.8
                        tk_score = max(0, min(100, tk_score))
                    else:
                        tk_score = min(100, tk_card_2['archetype']['transactions_per_week'] * 15)
                    all_scores.append((tk, tk_score))

                # For consistency, luck, and risk: calculate for all teams
                elif dimension_name == 'consistency':
                    # Calculate coefficient of variation for this team
                    tk_weekly_scores = []
                    for week in regular_season_weeks:
                        week_key = f'week_{week}'
                        if week_key in self.weekly_data.get(tk, {}):
                            tk_weekly_scores.append(self.weekly_data[tk][week_key].get('actual_points', 0))

                    if len(tk_weekly_scores) >= 3:
                        tk_mean = statistics.mean(tk_weekly_scores)
                        tk_std = statistics.stdev(tk_weekly_scores)
                        tk_cv = tk_std / tk_mean if tk_mean > 0 else 0

                        # Lower CV = more consistent = higher score
                        tk_score = 100 - ((tk_cv / league_avg_cv) * 50) if 'league_avg_cv' in locals() else 50
                        tk_score = max(0, min(100, tk_score))
                    else:
                        tk_score = 50
                    all_scores.append((tk, tk_score))

                elif dimension_name == 'luck':
                    # Calculate expected wins vs actual wins for this team
                    tk_team = self.teams[tk]
                    tk_actual_wins = int(tk_team['wins'])

                    tk_expected_wins = 0
                    for week in regular_season_weeks:
                        week_key = f'week_{week}'
                        if week_key not in self.weekly_data.get(tk, {}):
                            continue

                        tk_score_week = self.weekly_data[tk][week_key].get('actual_points', 0)

                        # Count how many teams this score would beat this week
                        teams_beaten = 0
                        for other_tk in self.teams.keys():
                            if other_tk == tk:
                                continue
                            if week_key in self.weekly_data.get(other_tk, {}):
                                other_score = self.weekly_data[other_tk][week_key].get('actual_points', 0)
                                if tk_score_week > other_score:
                                    teams_beaten += 1

                        tk_expected_wins += teams_beaten / (num_teams - 1)

                    tk_win_luck = tk_actual_wins - tk_expected_wins
                    tk_luck_score = 50 + (tk_win_luck * 12.5)
                    tk_luck_score = max(0, min(100, tk_luck_score))
                    all_scores.append((tk, tk_luck_score))

                elif dimension_name == 'risk':
                    # Calculate average player volatility for this team
                    tk_risk_scores = []

                    for week in list(regular_season_weeks)[:min(len(list(regular_season_weeks)), 10)]:
                        week_key = f'week_{week}'
                        if week_key not in self.weekly_data.get(tk, {}):
                            continue

                        starters = self.weekly_data[tk][week_key].get('roster', {}).get('starters', [])

                        week_risk = []
                        for player in starters:
                            player_id = str(player.get('player_id'))
                            player_weeks = self.player_points_by_week.get(player_id, {})
                            player_scores = [pts for pts in player_weeks.values() if pts > 0]

                            if len(player_scores) >= 3:
                                p_mean = statistics.mean(player_scores)
                                p_std = statistics.stdev(player_scores)
                                player_cv = p_std / p_mean if p_mean > 0 else 0
                                week_risk.append(player_cv)

                        if week_risk:
                            tk_risk_scores.append(statistics.mean(week_risk))

                    if tk_risk_scores:
                        tk_avg_risk = statistics.mean(tk_risk_scores)
                        tk_risk_score = (tk_avg_risk / league_avg_risk) * 50 if 'league_avg_risk' in locals() else 50
                        tk_risk_score = max(0, min(100, tk_risk_score))
                    else:
                        tk_risk_score = 50
                    all_scores.append((tk, tk_risk_score))

            # For dimensions we couldn't calculate for all teams (consistency/luck/risk),
            # use a simpler percentile estimate based on the score itself
            if len(all_scores) < num_teams:
                # Estimate: score already represents relative performance (0-100)
                # So percentile = score (this is the old behavior, but only for these 3)
                percentile_ranks[dimension_name] = round(dimensions[dimension_name], 1)
            else:
                # Sort scores ascending
                all_scores.sort(key=lambda x: x[1])

                # Find this team's rank (1-based)
                team_rank = next((i + 1 for i, (tk, _) in enumerate(all_scores) if tk == team_key), num_teams // 2)

                # Convert to percentile (higher is better)
                percentile = ((team_rank - 1) / (num_teams - 1)) * 100 if num_teams > 1 else 50.0
                percentile_ranks[dimension_name] = round(percentile, 1)

        # Interpretation grades
        def get_grade(score):
            if score >= 80:
                return 'Elite'
            elif score >= 65:
                return 'Strong'
            elif score >= 50:
                return 'Average'
            elif score >= 35:
                return 'Weak'
            else:
                return 'Poor'

        interpretation = {
            'draft': get_grade(draft_score),
            'lineups': get_grade(lineup_score),
            'waivers': get_grade(waiver_score),
            'consistency': get_grade(consistency_score),
            'luck': get_grade(luck_score),
            'risk': get_grade(risk_score)
        }

        # Overall score (average)
        overall_score = statistics.mean(dimensions.values())

        # Identify strengths (top 2) and weaknesses (bottom 2)
        sorted_dims = sorted(dimensions.items(), key=lambda x: x[1], reverse=True)
        strengths = [dim[0].title() for dim in sorted_dims[:2]]
        weaknesses = [dim[0].title() for dim in sorted_dims[-2:]]

        return {
            'manager_name': team['manager_name'],
            'dimensions': dimensions,
            'percentile_ranks': percentile_ranks,
            'interpretation': interpretation,
            'overall_score': round(overall_score, 1),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'league_averages': {
                'draft': 50.0,
                'lineups': 50.0,
                'waivers': 50.0,
                'consistency': 50.0,
                'luck': 50.0,
                'risk': 50.0
            },
            'profile_summary': self._generate_profile_summary(
                dimensions, interpretation, strengths, weaknesses
            )
        }

    def _generate_profile_summary(self, dimensions: Dict, interpretation: Dict,
                                   strengths: List, weaknesses: List) -> str:
        """Generate Reckoning-style profile summary"""

        # Determine archetype based on dimensions
        if dimensions['risk'] >= 65 and dimensions['draft'] >= 70:
            archetype = "The Aggressive Drafter"
            description = "You dominate the draft room and chase upside all season."
        elif dimensions['waivers'] >= 70 and dimensions['lineups'] >= 70:
            archetype = "The Active Manager"
            description = "You win through constant optimization and smart pickups."
        elif dimensions['consistency'] >= 70 and dimensions['risk'] <= 40:
            archetype = "The Steady Hand"
            description = "You trust your team and ride with floor plays. Boring but stable."
        elif dimensions['draft'] >= 75 and dimensions['waivers'] <= 40:
            archetype = "The Draft-and-Hold"
            description = "You trust your draft and rarely tinker. For better or worse."
        elif dimensions['luck'] <= 35:
            archetype = "The Cursed"
            description = "Fortune has abandoned you. The buzzsaws came for you."
        elif dimensions['luck'] >= 70:
            archetype = "The Fortunate"
            description = "The schedule smiled upon you. Easy opponents, lucky breaks."
        else:
            archetype = "The Balanced Manager"
            description = "No clear identity. A mixed bag of decisions."

        summary = f"{archetype}: {description}\n\n"
        summary += f"Strengths: {', '.join(strengths)}. "
        summary += f"Weaknesses: {', '.join(weaknesses)}."

        return summary


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
