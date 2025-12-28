"""
Data Validator for Fantasy Reckoning

Validates Yahoo Fantasy API data structures before processing.
Catches malformed or missing data early to provide clear error messages.
"""

from typing import Dict, List, Tuple, Any, Optional


class ValidationError(Exception):
    """Raised when data validation fails"""
    pass


class DataValidator:
    """Validates league data structure from Yahoo Fantasy API"""

    REQUIRED_LEAGUE_FIELDS = ['name', 'season', 'num_teams', 'current_week']
    REQUIRED_TEAM_FIELDS = ['team_key', 'team_name', 'manager_name']
    REQUIRED_WEEKLY_FIELDS = ['actual_points', 'roster']
    REQUIRED_PLAYER_FIELDS = ['player_id', 'actual_points']

    def __init__(self, data: Dict):
        self.data = data
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validations

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        self._validate_top_level_structure()
        self._validate_league()
        self._validate_teams()
        self._validate_weekly_data()
        self._validate_draft()
        self._validate_transactions()

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_top_level_structure(self):
        """Validate top-level data structure"""
        required_keys = ['league', 'teams', 'weekly_data']

        for key in required_keys:
            if key not in self.data:
                self.errors.append(f"Missing required top-level key: '{key}'")

    def _validate_league(self):
        """Validate league configuration"""
        league = self.data.get('league', {})

        for field in self.REQUIRED_LEAGUE_FIELDS:
            if field not in league:
                self.errors.append(f"Missing required league field: '{field}'")

        # Validate field types
        if 'num_teams' in league:
            if not isinstance(league['num_teams'], int) or league['num_teams'] < 4:
                self.errors.append(f"Invalid num_teams: {league['num_teams']} (must be >= 4)")

        if 'current_week' in league:
            if not isinstance(league['current_week'], int) or league['current_week'] < 1:
                self.errors.append(f"Invalid current_week: {league['current_week']}")

        # Check for optional but important fields
        if 'playoff_start_week' not in league:
            self.warnings.append("No playoff_start_week found, defaulting to week 15")

        if 'scoring_type' not in league:
            self.warnings.append("No scoring_type found, assuming 'head' (head-to-head)")

    def _validate_teams(self):
        """Validate team data"""
        teams = self.data.get('teams', [])

        if not teams:
            self.errors.append("No teams found in data")
            return

        if not isinstance(teams, list):
            self.errors.append("Teams should be a list")
            return

        expected_count = self.data.get('league', {}).get('num_teams', 0)
        if len(teams) != expected_count and expected_count > 0:
            self.warnings.append(f"Expected {expected_count} teams, found {len(teams)}")

        team_keys = set()
        for i, team in enumerate(teams):
            # Check required fields
            for field in self.REQUIRED_TEAM_FIELDS:
                if field not in team:
                    self.errors.append(f"Team {i + 1}: Missing required field '{field}'")

            # Check for duplicate team keys
            team_key = team.get('team_key')
            if team_key:
                if team_key in team_keys:
                    self.errors.append(f"Duplicate team_key: {team_key}")
                team_keys.add(team_key)

    def _validate_weekly_data(self):
        """Validate weekly matchup data"""
        weekly_data = self.data.get('weekly_data', {})

        if not weekly_data:
            self.errors.append("No weekly_data found")
            return

        teams = self.data.get('teams', [])
        team_keys = {t.get('team_key') for t in teams if t.get('team_key')}

        # Check each team has weekly data
        for team_key in team_keys:
            if team_key not in weekly_data:
                self.warnings.append(f"No weekly data for team: {team_key}")
                continue

            team_weeks = weekly_data[team_key]
            if not team_weeks:
                self.warnings.append(f"Empty weekly data for team: {team_key}")
                continue

            # Validate each week
            for week_key, week_data in team_weeks.items():
                self._validate_week(team_key, week_key, week_data)

    def _validate_week(self, team_key: str, week_key: str, week_data: Dict):
        """Validate a single week's data"""
        # Check required fields
        for field in self.REQUIRED_WEEKLY_FIELDS:
            if field not in week_data:
                self.errors.append(f"{team_key} {week_key}: Missing '{field}'")

        # Validate roster structure
        roster = week_data.get('roster', {})
        if roster:
            starters = roster.get('starters', [])
            if not starters:
                self.warnings.append(f"{team_key} {week_key}: No starters found")
            else:
                for player in starters:
                    self._validate_player(team_key, week_key, player)

    def _validate_player(self, team_key: str, week_key: str, player: Dict):
        """Validate player data"""
        for field in self.REQUIRED_PLAYER_FIELDS:
            if field not in player:
                self.errors.append(
                    f"{team_key} {week_key}: Player missing '{field}'"
                )

    def _validate_draft(self):
        """Validate draft data (optional)"""
        draft = self.data.get('draft', [])

        if not draft:
            self.warnings.append("No draft data found (offline/keeper draft?)")
            return

        for i, pick in enumerate(draft):
            if 'player_id' not in pick:
                self.warnings.append(f"Draft pick {i + 1}: Missing player_id")
            if 'team_key' not in pick:
                self.warnings.append(f"Draft pick {i + 1}: Missing team_key")

    def _validate_transactions(self):
        """Validate transaction data (optional)"""
        transactions = self.data.get('transactions', [])

        if not transactions:
            self.warnings.append("No transaction data found")
            return

        for i, trans in enumerate(transactions):
            if 'type' not in trans:
                self.warnings.append(f"Transaction {i + 1}: Missing type")
            if 'players' not in trans:
                self.warnings.append(f"Transaction {i + 1}: Missing players")


def validate_league_data(data: Dict) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate league data

    Args:
        data: League data dictionary

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = DataValidator(data)
    return validator.validate_all()


def validate_and_report(data: Dict, raise_on_error: bool = True) -> bool:
    """
    Validate data and print report

    Args:
        data: League data dictionary
        raise_on_error: If True, raise ValidationError on failure

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If raise_on_error is True and validation fails
    """
    is_valid, errors, warnings = validate_league_data(data)

    if warnings:
        print("\n⚠️  VALIDATION WARNINGS:")
        for w in warnings:
            print(f"  • {w}")

    if errors:
        print("\n❌ VALIDATION ERRORS:")
        for e in errors:
            print(f"  • {e}")

        if raise_on_error:
            raise ValidationError(f"Data validation failed with {len(errors)} error(s)")

    if is_valid:
        print("\n✅ Data validation passed")

    return is_valid
