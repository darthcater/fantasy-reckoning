"""
Tests for data validation module

Ensures the validator catches malformed data before it causes issues
in the calculation pipeline.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_validator import DataValidator, validate_league_data, ValidationError


class TestTopLevelValidation:
    """Test validation of top-level data structure"""

    def test_valid_structure_passes(self, sample_league_data):
        """Valid data should pass validation"""
        is_valid, errors, warnings = validate_league_data(sample_league_data)
        assert is_valid
        assert len(errors) == 0

    def test_missing_league_fails(self):
        """Missing league key should fail"""
        data = {'teams': [], 'weekly_data': {}}
        is_valid, errors, warnings = validate_league_data(data)
        assert not is_valid
        assert any('league' in e for e in errors)

    def test_missing_teams_fails(self):
        """Missing teams key should fail"""
        data = {'league': {}, 'weekly_data': {}}
        is_valid, errors, warnings = validate_league_data(data)
        assert not is_valid
        assert any('teams' in e for e in errors)

    def test_missing_weekly_data_fails(self):
        """Missing weekly_data key should fail"""
        data = {'league': {}, 'teams': []}
        is_valid, errors, warnings = validate_league_data(data)
        assert not is_valid
        assert any('weekly_data' in e for e in errors)


class TestLeagueValidation:
    """Test validation of league configuration"""

    def test_missing_league_name_fails(self, sample_league_data):
        """Missing league name should fail"""
        del sample_league_data['league']['name']
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('name' in e for e in errors)

    def test_missing_season_fails(self, sample_league_data):
        """Missing season should fail"""
        del sample_league_data['league']['season']
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('season' in e for e in errors)

    def test_invalid_num_teams_fails(self, sample_league_data):
        """num_teams < 4 should fail"""
        sample_league_data['league']['num_teams'] = 2
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('num_teams' in e for e in errors)

    def test_missing_playoff_week_warns(self, sample_league_data):
        """Missing playoff_start_week should warn"""
        del sample_league_data['league']['playoff_start_week']
        is_valid, errors, warnings = validate_league_data(sample_league_data)
        assert is_valid  # Still valid, just a warning
        assert any('playoff' in w.lower() for w in warnings)


class TestTeamValidation:
    """Test validation of team data"""

    def test_empty_teams_fails(self, sample_league_data):
        """Empty teams list should fail"""
        sample_league_data['teams'] = []
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('No teams' in e for e in errors)

    def test_missing_team_key_fails(self, sample_league_data):
        """Team missing team_key should fail"""
        del sample_league_data['teams'][0]['team_key']
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('team_key' in e for e in errors)

    def test_missing_manager_name_fails(self, sample_league_data):
        """Team missing manager_name should fail"""
        del sample_league_data['teams'][0]['manager_name']
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('manager_name' in e for e in errors)

    def test_duplicate_team_key_fails(self, sample_league_data):
        """Duplicate team_key should fail"""
        sample_league_data['teams'][1]['team_key'] = sample_league_data['teams'][0]['team_key']
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('Duplicate' in e for e in errors)


class TestWeeklyDataValidation:
    """Test validation of weekly matchup data"""

    def test_empty_weekly_data_fails(self, sample_league_data):
        """Empty weekly_data should fail"""
        sample_league_data['weekly_data'] = {}
        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('weekly_data' in e.lower() for e in errors)

    def test_missing_roster_fails(self, sample_league_data):
        """Week missing roster should fail"""
        team_key = list(sample_league_data['weekly_data'].keys())[0]
        week_key = list(sample_league_data['weekly_data'][team_key].keys())[0]
        del sample_league_data['weekly_data'][team_key][week_key]['roster']

        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('roster' in e for e in errors)

    def test_missing_actual_points_fails(self, sample_league_data):
        """Week missing actual_points should fail"""
        team_key = list(sample_league_data['weekly_data'].keys())[0]
        week_key = list(sample_league_data['weekly_data'][team_key].keys())[0]
        del sample_league_data['weekly_data'][team_key][week_key]['actual_points']

        is_valid, errors, _ = validate_league_data(sample_league_data)
        assert not is_valid
        assert any('actual_points' in e for e in errors)


class TestDraftValidation:
    """Test validation of draft data"""

    def test_missing_draft_warns(self, sample_league_data):
        """Missing draft data should warn (not fail)"""
        del sample_league_data['draft']
        is_valid, errors, warnings = validate_league_data(sample_league_data)
        assert is_valid  # Still valid, just a warning
        assert any('draft' in w.lower() for w in warnings)

    def test_empty_draft_warns(self, sample_league_data):
        """Empty draft list should warn"""
        sample_league_data['draft'] = []
        is_valid, errors, warnings = validate_league_data(sample_league_data)
        assert is_valid
        assert any('draft' in w.lower() for w in warnings)


class TestTransactionValidation:
    """Test validation of transaction data"""

    def test_missing_transactions_warns(self, sample_league_data):
        """Missing transaction data should warn (not fail)"""
        del sample_league_data['transactions']
        is_valid, errors, warnings = validate_league_data(sample_league_data)
        assert is_valid
        assert any('transaction' in w.lower() for w in warnings)


class TestValidatorClass:
    """Test DataValidator class directly"""

    def test_validator_collects_multiple_errors(self):
        """Validator should collect all errors, not stop at first"""
        data = {
            'league': {},  # Missing required fields
            'teams': [],   # Empty
            'weekly_data': {}  # Empty
        }

        validator = DataValidator(data)
        is_valid, errors, warnings = validator.validate_all()

        assert not is_valid
        assert len(errors) > 1  # Should have multiple errors

    def test_validator_separates_errors_and_warnings(self, sample_league_data):
        """Errors and warnings should be separate"""
        # Remove optional field (should warn)
        del sample_league_data['draft']
        # Keep everything else valid

        validator = DataValidator(sample_league_data)
        is_valid, errors, warnings = validator.validate_all()

        assert is_valid  # No errors
        assert len(warnings) > 0  # But has warnings
        assert len(errors) == 0
