"""
Sleeper Fantasy Football Data Puller
Pulls league data from Sleeper API and outputs Yahoo-compatible JSON format
for use with fantasy_wrapped_calculator.py

No authentication required - just need league_id
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional


# Sleeper API base URL
SLEEPER_API_BASE = "https://api.sleeper.app/v1"

# Player cache file (Sleeper player database is ~5MB, cache it)
PLAYER_CACHE_FILE = "sleeper_players_cache.json"
PLAYER_CACHE_MAX_AGE_HOURS = 24


class SleeperDataPuller:
    """Pulls fantasy football data from Sleeper API"""

    def __init__(self, league_id: str, work_dir: str = None):
        """
        Initialize the Sleeper data puller.

        Args:
            league_id: Sleeper league ID
            work_dir: Directory for output files (default: current directory)
        """
        self.league_id = league_id
        self.work_dir = work_dir or os.getcwd()

        # Data caches
        self.league_data = None
        self.users = {}  # user_id -> user info
        self.rosters = []  # List of roster objects
        self.roster_to_user = {}  # roster_id -> user_id
        self.players_db = {}  # player_id -> player info
        self.scoring_settings = {}  # League scoring settings

    def _api_call(self, endpoint: str) -> Optional[Dict]:
        """Make API call to Sleeper with error handling"""
        url = f"{SLEEPER_API_BASE}{endpoint}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None

    def _get_team_key(self, roster_id: int) -> str:
        """Generate Yahoo-compatible team key from roster_id"""
        return f"sleeper.l.{self.league_id}.t.{roster_id}"

    def _convert_roster_positions(self, positions: List[str]) -> Dict[str, int]:
        """Convert Sleeper's roster_positions list to Yahoo-style dict format.

        Sleeper: ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'FLEX', 'K', 'DEF', 'BN', 'BN', ...]
        Yahoo:   {'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'W/R/T': 1, 'K': 1, 'DEF': 1, 'BN': 6}
        """
        from collections import Counter
        counts = Counter(positions)

        # Map Sleeper position names to Yahoo equivalents
        result = {}
        for pos, count in counts.items():
            if pos == 'FLEX':
                result['W/R/T'] = result.get('W/R/T', 0) + count
            elif pos == 'SUPER_FLEX':
                result['Q/W/R/T'] = result.get('Q/W/R/T', 0) + count
            elif pos == 'REC_FLEX':
                result['W/T'] = result.get('W/T', 0) + count
            elif pos == 'IDP_FLEX':
                result['D'] = result.get('D', 0) + count
            else:
                result[pos] = count

        return result

    def _map_injury_status(self, status: Optional[str]) -> str:
        """Map Sleeper injury status to Yahoo format"""
        if not status:
            return ""
        status_map = {
            "Questionable": "Q",
            "Doubtful": "D",
            "Out": "O",
            "IR": "IR",
            "PUP": "O",
            "Sus": "O",
            "COV": "O",
        }
        return status_map.get(status, "")

    def _load_players_cache(self) -> bool:
        """Load players from cache if fresh enough"""
        cache_path = os.path.join(self.work_dir, PLAYER_CACHE_FILE)
        if not os.path.exists(cache_path):
            return False

        # Check cache age
        cache_mtime = os.path.getmtime(cache_path)
        age_hours = (time.time() - cache_mtime) / 3600
        if age_hours > PLAYER_CACHE_MAX_AGE_HOURS:
            return False

        try:
            with open(cache_path, 'r') as f:
                self.players_db = json.load(f)
            print(f"✓ Loaded {len(self.players_db)} players from cache")
            return True
        except Exception as e:
            print(f"Cache load failed: {e}")
            return False

    def _save_players_cache(self):
        """Save players database to cache"""
        cache_path = os.path.join(self.work_dir, PLAYER_CACHE_FILE)
        try:
            with open(cache_path, 'w') as f:
                json.dump(self.players_db, f)
            print(f"✓ Saved {len(self.players_db)} players to cache")
        except Exception as e:
            print(f"Cache save failed: {e}")

    def fetch_players_database(self):
        """Fetch all NFL players (large request, ~5MB)"""
        if self._load_players_cache():
            return

        print("Fetching Sleeper players database (this may take a moment)...")
        players = self._api_call("/players/nfl")
        if players:
            self.players_db = players
            self._save_players_cache()
        else:
            print("Warning: Failed to fetch players database")

    def get_nfl_state(self) -> Dict:
        """Get current NFL state (week, season, etc.)"""
        state = self._api_call("/state/nfl")
        return state or {"week": 1, "season": 2025}

    def get_league_metadata(self) -> Dict:
        """Fetch league settings and metadata"""
        print(f"Fetching league {self.league_id}...")
        self.league_data = self._api_call(f"/league/{self.league_id}")

        if not self.league_data:
            raise ValueError(f"Could not fetch league {self.league_id}")

        self.scoring_settings = self.league_data.get('scoring_settings', {})

        # Determine playoff start week from settings
        settings = self.league_data.get('settings', {})
        playoff_week_start = settings.get('playoff_week_start', 15)

        metadata = {
            "league_id": self.league_id,
            "name": self.league_data.get('name', 'Unknown League'),
            "season": int(self.league_data.get('season', 2025)),
            "num_teams": self.league_data.get('total_rosters', 0),
            "playoff_start_week": playoff_week_start,
            "scoring_type": "head",  # Sleeper is head-to-head
            "current_week": self.get_nfl_state().get('week', 1),
            "roster_positions": self._convert_roster_positions(self.league_data.get('roster_positions', [])),
            "waiver_type": settings.get('waiver_type', 0),
            "waiver_rule": "normal",
            "faab_budget": settings.get('waiver_budget', 100),
            "stat_categories": {},
            "stat_modifiers": {"stats": []},
        }

        print(f"✓ League: {metadata['name']} ({metadata['num_teams']} teams)")
        return metadata

    def get_users(self) -> Dict:
        """Fetch league users (managers)"""
        users_list = self._api_call(f"/league/{self.league_id}/users")
        if users_list:
            for user in users_list:
                user_id = user.get('user_id')
                self.users[user_id] = {
                    'user_id': user_id,
                    'display_name': user.get('display_name', 'Unknown'),
                    'team_name': user.get('metadata', {}).get('team_name', ''),
                }
        print(f"✓ Loaded {len(self.users)} users")
        return self.users

    def get_rosters(self) -> List[Dict]:
        """Fetch all rosters (teams) with standings"""
        self.rosters = self._api_call(f"/league/{self.league_id}/rosters") or []

        # Build roster_id -> user_id mapping
        for roster in self.rosters:
            roster_id = roster.get('roster_id')
            owner_id = roster.get('owner_id')
            self.roster_to_user[roster_id] = owner_id

        print(f"✓ Loaded {len(self.rosters)} rosters")
        return self.rosters

    def get_all_teams(self) -> List[Dict]:
        """Get all teams in Yahoo-compatible format"""
        if not self.rosters:
            self.get_rosters()
        if not self.users:
            self.get_users()

        teams = []
        for roster in self.rosters:
            roster_id = roster.get('roster_id')
            owner_id = roster.get('owner_id')
            user_info = self.users.get(owner_id, {})
            settings = roster.get('settings', {})

            team_key = self._get_team_key(roster_id)

            teams.append({
                "team_id": team_key,
                "team_key": team_key,
                "team_name": user_info.get('team_name') or user_info.get('display_name', f'Team {roster_id}'),
                "manager_name": user_info.get('display_name', 'Unknown'),
                "final_standing": settings.get('rank', roster_id),
                "wins": settings.get('wins', 0),
                "losses": settings.get('losses', 0),
                "ties": settings.get('ties', 0),
                "points_for": settings.get('fpts', 0) + settings.get('fpts_decimal', 0) / 100,
                "points_against": settings.get('fpts_against', 0) + settings.get('fpts_against_decimal', 0) / 100,
                "auction_budget_total": 0,  # Sleeper doesn't expose this directly
                "auction_budget_spent": 0,
                "faab_balance": roster.get('settings', {}).get('waiver_budget_used', 0),
            })

        return teams

    def get_player_info(self, player_id: str) -> Dict:
        """Get player info from database"""
        if not self.players_db:
            self.fetch_players_database()

        player = self.players_db.get(str(player_id), {})
        return {
            "player_id": player_id,
            "player_name": f"{player.get('first_name', '')} {player.get('last_name', '')}".strip() or f"Player {player_id}",
            "position": player.get('position', 'Unknown'),
            "team": player.get('team', ''),
            "status": self._map_injury_status(player.get('injury_status')),
            "eligible_positions": player.get('fantasy_positions', []),
        }

    def get_weekly_matchups(self, week: int) -> List[Dict]:
        """Fetch matchups for a specific week"""
        matchups = self._api_call(f"/league/{self.league_id}/matchups/{week}")
        return matchups or []

    def get_weekly_data(self, num_weeks: int) -> Dict:
        """
        Fetch weekly data for all teams across all weeks.

        Returns Yahoo-compatible weekly_data structure.
        """
        print(f"Fetching weekly data for {num_weeks} weeks...")

        if not self.players_db:
            self.fetch_players_database()

        weekly_data = {}

        # Initialize structure for each team
        for roster in self.rosters:
            team_key = self._get_team_key(roster.get('roster_id'))
            weekly_data[team_key] = {}

        for week in range(1, num_weeks + 1):
            print(f"  Week {week}...", end=" ")
            matchups = self.get_weekly_matchups(week)

            if not matchups:
                print("no data")
                continue

            # Group matchups by matchup_id to find opponents
            matchup_groups = {}
            for m in matchups:
                mid = m.get('matchup_id')
                if mid not in matchup_groups:
                    matchup_groups[mid] = []
                matchup_groups[mid].append(m)

            # Process each matchup
            for matchup in matchups:
                roster_id = matchup.get('roster_id')
                team_key = self._get_team_key(roster_id)
                matchup_id = matchup.get('matchup_id')

                # Find opponent in same matchup
                opponent_data = None
                for m in matchup_groups.get(matchup_id, []):
                    if m.get('roster_id') != roster_id:
                        opponent_data = m
                        break

                actual_points = matchup.get('points', 0) or 0
                opponent_points = opponent_data.get('points', 0) if opponent_data else 0
                opponent_key = self._get_team_key(opponent_data.get('roster_id')) if opponent_data else None

                # Determine result
                if actual_points > opponent_points:
                    result = "W"
                elif actual_points < opponent_points:
                    result = "L"
                else:
                    result = "T"

                # Build roster with player info
                starters = matchup.get('starters', []) or []
                all_players = matchup.get('players', []) or []
                bench_players = [p for p in all_players if p not in starters]

                # Get player points from matchup if available
                players_points = matchup.get('players_points', {})

                # Build starters list
                starters_list = []
                roster_positions = self.league_data.get('roster_positions', [])

                for i, player_id in enumerate(starters):
                    if not player_id:
                        continue
                    player_info = self.get_player_info(player_id)

                    # Determine selected position from roster slot
                    selected_pos = roster_positions[i] if i < len(roster_positions) else player_info['position']

                    # Get player points if available
                    player_pts = players_points.get(str(player_id), 0) if players_points else 0

                    starters_list.append({
                        "player_id": player_id,
                        "player_name": player_info['player_name'],
                        "position": player_info['position'],
                        "selected_position": selected_pos,
                        "eligible_positions": player_info['eligible_positions'] or [player_info['position']],
                        "status": player_info['status'],
                        "actual_points": player_pts,
                        "stats_detail": {},
                    })

                # Build bench list
                bench_list = []
                for player_id in bench_players:
                    if not player_id:
                        continue
                    player_info = self.get_player_info(player_id)
                    player_pts = players_points.get(str(player_id), 0) if players_points else 0

                    bench_list.append({
                        "player_id": player_id,
                        "player_name": player_info['player_name'],
                        "position": player_info['position'],
                        "selected_position": "BN",
                        "eligible_positions": player_info['eligible_positions'] or [player_info['position']],
                        "status": player_info['status'],
                        "actual_points": player_pts,
                        "stats_detail": {},
                    })

                # Calculate totals
                total_starter_points = sum(p.get('actual_points', 0) for p in starters_list)
                total_bench_points = sum(p.get('actual_points', 0) for p in bench_list)

                weekly_data[team_key][f"week_{week}"] = {
                    "week": week,
                    "actual_points": actual_points,
                    "projected_points": 0,  # Sleeper doesn't provide projections in matchup
                    "opponent_id": opponent_key,
                    "opponent_points": opponent_points,
                    "result": result,
                    "roster": {
                        "starters": starters_list,
                        "bench": bench_list,
                        "total_starter_points": total_starter_points,
                        "total_bench_points": total_bench_points,
                    },
                    "bench_points": total_bench_points,
                }

            print("done")

        return weekly_data

    def get_transactions(self) -> List[Dict]:
        """Fetch all transactions for the season"""
        print("Fetching transactions...")
        all_transactions = []

        # Sleeper transactions are fetched by round (week)
        for week in range(1, 18):
            txns = self._api_call(f"/league/{self.league_id}/transactions/{week}")
            if txns:
                all_transactions.extend(txns)

        # Convert to Yahoo-compatible format
        yahoo_transactions = []
        for txn in all_transactions:
            txn_type = txn.get('type', 'unknown')

            # Map transaction type
            if txn_type == 'free_agent':
                yahoo_type = 'add'
            elif txn_type == 'waiver':
                yahoo_type = 'add'
            elif txn_type == 'trade':
                yahoo_type = 'trade'
            else:
                yahoo_type = txn_type

            # Build players list
            players = []
            adds = txn.get('adds') or {}
            drops = txn.get('drops') or {}

            # For trades, build a map of player_id -> source roster_id from drops
            drop_sources = {}
            if txn_type == 'trade':
                drop_sources = {player_id: roster_id for player_id, roster_id in drops.items()}

            for player_id, roster_id in adds.items():
                player_info = self.get_player_info(player_id)
                team_key = self._get_team_key(roster_id)
                user_info = self.users.get(self.roster_to_user.get(roster_id), {})

                # For trades, get source team from drops; otherwise it's waivers/FA
                if txn_type == 'trade' and player_id in drop_sources:
                    source_roster_id = drop_sources[player_id]
                    source_team_key = self._get_team_key(source_roster_id)
                    source_user_info = self.users.get(self.roster_to_user.get(source_roster_id), {})
                    source_type = "team"
                    source_team_name = source_user_info.get('display_name', 'Unknown')
                else:
                    source_type = "waivers" if txn_type == 'waiver' else "freeagents"
                    source_team_key = None
                    source_team_name = None

                players.append({
                    "player_name": player_info['player_name'],
                    "player_id": player_id,
                    "position": player_info['position'],
                    "type": "add",
                    "source_type": source_type,
                    "source_team_key": source_team_key,
                    "source_team_name": source_team_name,
                    "destination_team_key": team_key,
                    "destination_team_name": user_info.get('display_name', 'Unknown'),
                })

            for player_id, roster_id in drops.items():
                player_info = self.get_player_info(player_id)
                team_key = self._get_team_key(roster_id)
                user_info = self.users.get(self.roster_to_user.get(roster_id), {})

                # For trades, get destination team from adds
                if txn_type == 'trade' and player_id in adds:
                    dest_roster_id = adds[player_id]
                    dest_team_key = self._get_team_key(dest_roster_id)
                    dest_user_info = self.users.get(self.roster_to_user.get(dest_roster_id), {})
                    dest_team_name = dest_user_info.get('display_name', 'Unknown')
                else:
                    dest_team_key = None
                    dest_team_name = None

                players.append({
                    "player_name": player_info['player_name'],
                    "player_id": player_id,
                    "position": player_info['position'],
                    "type": "drop",
                    "source_type": "team",
                    "source_team_key": team_key,
                    "source_team_name": user_info.get('display_name', 'Unknown'),
                    "destination_team_key": dest_team_key,
                    "destination_team_name": dest_team_name,
                })

            # Get FAAB bid
            waiver_budget = txn.get('settings', {}).get('waiver_bid') if txn.get('settings') else None

            yahoo_transactions.append({
                "transaction_id": txn.get('transaction_id', ''),
                "type": yahoo_type,
                "timestamp": txn.get('created', 0) // 1000,  # Sleeper uses milliseconds
                "status": txn.get('status', 'complete'),
                "faab_bid": waiver_budget,
                "players": players,
            })

        print(f"✓ Loaded {len(yahoo_transactions)} transactions")
        return yahoo_transactions

    def get_draft_results(self) -> List[Dict]:
        """Fetch draft results"""
        print("Fetching draft results...")

        # First get drafts for this league
        drafts = self._api_call(f"/league/{self.league_id}/drafts")
        if not drafts:
            print("No draft data found")
            return []

        # Get the first (usually only) draft
        draft_id = drafts[0].get('draft_id') if drafts else None
        if not draft_id:
            return []

        # Fetch draft picks
        picks = self._api_call(f"/draft/{draft_id}/picks")
        if not picks:
            return []

        # Get draft settings for auction detection and league type
        draft_info = self._api_call(f"/draft/{draft_id}")
        is_auction = draft_info.get('type') == 'auction' if draft_info else False

        # Count keeper picks for league type detection
        keeper_count = sum(1 for p in picks if p.get('is_keeper'))

        # Convert to Yahoo format
        yahoo_draft = []
        for pick in picks:
            player_id = pick.get('player_id')
            player_info = self.get_player_info(player_id) if player_id else {}
            roster_id = pick.get('roster_id')

            yahoo_draft.append({
                "round": pick.get('round', 0),
                "pick": pick.get('draft_slot', 0),
                "overall_pick": pick.get('pick_no', 0),
                "team_id": self._get_team_key(roster_id),
                "team_key": self._get_team_key(roster_id),
                "player_id": str(player_id) if player_id else "",
                "player_name": player_info.get('player_name', 'Unknown'),
                "position": player_info.get('position', 'Unknown'),
                "cost": pick.get('metadata', {}).get('amount', 0) if is_auction else 0,
                "is_keeper": bool(pick.get('is_keeper')),  # Keeper pick flag
            })

        if keeper_count > 0:
            print(f"✓ Loaded {len(yahoo_draft)} draft picks ({keeper_count} keepers detected)")
        else:
            print(f"✓ Loaded {len(yahoo_draft)} draft picks")

        return yahoo_draft

    def pull_complete_season_data(self) -> Dict:
        """
        Pull all data and return Yahoo-compatible JSON structure.
        """
        print("\n" + "=" * 60)
        print("SLEEPER DATA PULLER")
        print("=" * 60)

        # Fetch all data
        metadata = self.get_league_metadata()
        teams = self.get_all_teams()

        # Determine weeks to fetch
        nfl_state = self.get_nfl_state()
        nfl_season = int(nfl_state.get('season', 2025))
        nfl_week = int(nfl_state.get('week', 17))
        nfl_season_type = nfl_state.get('season_type', 'regular')
        league_season = int(metadata.get('season', 2025))
        playoff_week = int(metadata.get('playoff_start_week', 15))

        # Determine if regular season is complete
        # - League season is in the past, OR
        # - League season is current but we're in postseason/offseason
        regular_season_complete = (
            league_season < nfl_season or
            (league_season == nfl_season and nfl_season_type in ('post', 'off'))
        )

        if regular_season_complete:
            # Completed season - fetch all regular season weeks
            weeks_to_fetch = playoff_week - 1
        else:
            # Current season in progress - fetch up to current week
            weeks_to_fetch = min(nfl_week, playoff_week - 1)

        weekly_data = self.get_weekly_data(weeks_to_fetch)
        transactions = self.get_transactions()
        draft = self.get_draft_results()

        # Update current_week to reflect actual weeks fetched (important for completed seasons)
        metadata['current_week'] = weeks_to_fetch

        # Detect league type based on draft data and league name
        keeper_count = sum(1 for p in draft if p.get('is_keeper'))
        league_name_lower = metadata.get('name', '').lower()

        if 'dynasty' in league_name_lower:
            metadata['league_type'] = 'dynasty'
        elif keeper_count > 0 or 'keeper' in league_name_lower:
            metadata['league_type'] = 'keeper'
            metadata['keeper_count'] = keeper_count
        else:
            metadata['league_type'] = 'redraft'

        # Assemble final structure
        data = {
            "league": metadata,
            "teams": teams,
            "weekly_data": weekly_data,
            "transactions": transactions,
            "draft": draft,
            "generated_at": datetime.now().isoformat(),
        }

        print("\n" + "=" * 60)
        print("DATA PULL COMPLETE")
        print("=" * 60)

        return data

    def save_to_json(self, data: Dict, filename: str = None) -> str:
        """Save data to JSON file"""
        if filename is None:
            filename = f"league_{self.league_id}_{data['league']['season']}.json"

        filepath = os.path.join(self.work_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Saved to {filepath}")
        return filepath


def main():
    """Main execution for testing"""
    import argparse

    parser = argparse.ArgumentParser(description='Sleeper Fantasy Football Data Puller')
    parser.add_argument('--league-id', required=True, help='Sleeper league ID')
    parser.add_argument('--output', help='Output file path (default: league_{id}_{season}.json)')
    parser.add_argument('--work-dir', default='.', help='Output directory (used if --output not specified)')

    args = parser.parse_args()

    # Determine work directory from output path if provided
    work_dir = args.work_dir
    if args.output:
        work_dir = os.path.dirname(args.output) or '.'

    puller = SleeperDataPuller(args.league_id, work_dir)
    data = puller.pull_complete_season_data()

    # Determine output filename
    if args.output:
        output_file = os.path.basename(args.output)
        puller.save_to_json(data, output_file)
    else:
        puller.save_to_json(data)


if __name__ == '__main__':
    main()
