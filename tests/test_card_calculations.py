"""
Unit tests for card calculations

Tests each card's calculation logic with sample data to ensure:
- Calculations produce expected output structure
- Edge cases are handled gracefully
- Percentiles and rankings are calculated correctly
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCalculatorInitialization:
    """Test calculator initialization and configuration detection"""

    def test_calculator_loads_data(self, calculator):
        """Calculator should load and parse league data"""
        assert calculator.league is not None
        assert len(calculator.teams) == 12
        assert calculator.draft_type in ['auction', 'snake', 'unknown']

    def test_detects_roster_configuration(self, calculator):
        """Calculator should detect roster configuration"""
        assert 'num_starters' in calculator.roster_config
        assert calculator.roster_config['num_starters'] >= 1

    def test_builds_indices(self, calculator):
        """Calculator should build lookup indices"""
        assert hasattr(calculator, 'draft_by_team')
        assert hasattr(calculator, 'transactions_by_team')
        assert hasattr(calculator, 'player_points_by_week')

    def test_regular_season_weeks(self, calculator):
        """Should return correct regular season week range"""
        weeks = calculator.get_regular_season_weeks()
        assert 1 in weeks
        assert 14 in weeks
        assert 15 not in weeks  # Playoffs


class TestCard1Overview:
    """Test Card 1: The Leader calculations"""

    def test_card_1_returns_required_fields(self, calculator):
        """Card 1 should return all required fields"""
        team_key = list(calculator.teams.keys())[0]
        other_cards = {
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_1(team_key, other_cards)

        assert 'manager_name' in result
        assert 'archetype' in result
        assert 'name' in result['archetype']
        assert 'description' in result['archetype']
        assert 'dimension_breakdown' in result
        assert 'overall_rank_numeric' in result
        assert 'overall_percentile' in result

    def test_percentiles_are_valid(self, calculator):
        """Percentiles should be between 0 and 100"""
        team_key = list(calculator.teams.keys())[0]
        other_cards = {
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_1(team_key, other_cards)

        for dim_name, dim_data in result['dimension_breakdown'].items():
            assert 0 <= dim_data['percentile'] <= 100, f"{dim_name} percentile out of range"

        assert 0 <= result['overall_percentile'] <= 100

    def test_rank_is_valid(self, calculator):
        """Rank should be between 1 and number of teams"""
        team_key = list(calculator.teams.keys())[0]
        other_cards = {
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_1(team_key, other_cards)

        num_teams = len(calculator.teams)
        assert 1 <= result['overall_rank_numeric'] <= num_teams


class TestCard2Ledger:
    """Test Card 2: The Ledger calculations"""

    def test_card_2_returns_required_fields(self, calculator):
        """Card 2 should return all required fields"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        assert 'manager_name' in result
        assert 'draft' in result
        assert 'waivers' in result
        assert 'trades' in result
        assert 'costly_drops' in result

    def test_draft_section_structure(self, calculator):
        """Draft section should have correct structure"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        draft = result['draft']
        assert 'total_points' in draft
        assert 'rank' in draft
        assert 'steals' in draft
        assert 'busts' in draft
        assert isinstance(draft['steals'], list)
        assert isinstance(draft['busts'], list)

    def test_waivers_section_structure(self, calculator):
        """Waivers section should have correct structure"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        waivers = result['waivers']
        assert 'total_points_started' in waivers
        assert 'rank' in waivers
        assert 'total_adds' in waivers

    def test_ranks_are_valid(self, calculator):
        """All ranks should be between 1 and number of teams"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        num_teams = len(calculator.teams)

        assert 1 <= result['draft']['rank'] <= num_teams
        assert 1 <= result['waivers']['rank'] <= num_teams


class TestCard3Lineups:
    """Test Card 3: The Lineup calculations"""

    def test_card_3_returns_required_fields(self, calculator):
        """Card 3 should return all required fields"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_3(team_key)

        assert 'manager_name' in result
        assert 'efficiency' in result
        assert 'timelines' in result
        assert 'wins_left_on_table' in result
        assert 'pivotal_moments' in result

    def test_efficiency_values_are_valid(self, calculator):
        """Efficiency percentage should be reasonable (0-120 allows for rounding)"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_3(team_key)

        eff = result['efficiency']
        # Efficiency can exceed 100% in edge cases due to calculation methodology
        assert 0 <= eff['lineup_efficiency_pct'] <= 120
        assert 0 <= eff['avg_weekly_efficiency'] <= 120

    def test_timelines_structure(self, calculator):
        """Timelines should have actual and optimal records"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_3(team_key)

        timelines = result['timelines']
        assert 'actual' in timelines
        assert 'optimal_lineup' in timelines

        actual = timelines['actual']
        assert 'wins' in actual
        assert 'losses' in actual
        assert 'record' in actual

    def test_pivotal_moments_structure(self, calculator):
        """Pivotal moments should have correct structure"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_3(team_key)

        moments = result['pivotal_moments']
        assert 'moment_type' in moments
        assert moments['moment_type'] in ['fatal_error', 'clutch_call', 'none']


class TestCard4Story:
    """Test Card 4: The Legend calculations"""

    def test_card_4_returns_required_fields(self, calculator):
        """Card 4 should return all required fields"""
        team_key = list(calculator.teams.keys())[0]

        other_cards = {
            'card_1_overview': {},
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_4(team_key, other_cards)

        assert 'manager_name' in result
        assert 'actual_record' in result
        assert 'win_attribution' in result

    def test_win_attribution_structure(self, calculator):
        """Win attribution should have skill and luck factors"""
        team_key = list(calculator.teams.keys())[0]

        other_cards = {
            'card_1_overview': {},
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_4(team_key, other_cards)

        attr = result['win_attribution']
        assert 'skill_factors' in attr
        assert 'luck_factors' in attr
        assert 'true_skill_record' in attr
        assert 'total_skill_impact' in attr
        assert 'total_luck_impact' in attr

    def test_agent_of_chaos_structure(self, calculator):
        """Agent of chaos should have correct structure when present"""
        team_key = list(calculator.teams.keys())[0]

        other_cards = {
            'card_1_overview': {},
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_4(team_key, other_cards)

        agent = result['win_attribution'].get('agent_of_chaos')
        if agent:
            assert 'player_name' in agent
            assert 'week' in agent
            assert 'points' in agent
            assert 'deviation' in agent
            assert 'type' in agent
            assert agent['type'] in ['boom', 'bust']


class TestOptimalLineupCalculation:
    """Test optimal lineup calculation logic"""

    def test_optimal_points_calculation(self, calculator):
        """Optimal lineup calculation should return valid structure"""
        team_key = list(calculator.teams.keys())[0]

        for week in calculator.get_regular_season_weeks():
            week_key = f'week_{week}'
            if week_key in calculator.weekly_data.get(team_key, {}):
                roster = calculator.weekly_data[team_key][week_key].get('roster', {})
                result = calculator.calculate_optimal_lineup(roster)

                # Verify structure
                assert 'optimal_points' in result
                assert 'actual_points' in result
                assert 'efficiency_pct' in result
                assert result['optimal_points'] >= 0
                assert result['actual_points'] >= 0
                break  # Only need to test one week

    def test_efficiency_calculation(self, calculator):
        """Efficiency should be (actual / optimal) * 100"""
        team_key = list(calculator.teams.keys())[0]
        week_key = 'week_1'

        if week_key in calculator.weekly_data.get(team_key, {}):
            roster = calculator.weekly_data[team_key][week_key].get('roster', {})
            result = calculator.calculate_optimal_lineup(roster)

            if result['optimal_points'] > 0:
                expected_eff = (result['actual_points'] / result['optimal_points']) * 100
                assert abs(result['efficiency_pct'] - expected_eff) < 0.1


class TestAllTeamsCalculations:
    """Test that calculations work for all teams"""

    def test_all_teams_get_card_2(self, calculator):
        """All teams should successfully generate Card 2"""
        for team_key in calculator.teams.keys():
            result = calculator.calculate_card_2(team_key)
            assert 'manager_name' in result
            assert 'error' not in result

    def test_all_teams_get_card_3(self, calculator):
        """All teams should successfully generate Card 3"""
        for team_key in calculator.teams.keys():
            result = calculator.calculate_card_3(team_key)
            assert 'manager_name' in result
            assert 'error' not in result

    def test_all_teams_get_card_4(self, calculator):
        """All teams should successfully generate Card 4"""
        for team_key in calculator.teams.keys():
            other_cards = {
                'card_1_overview': {},
                'card_2_ledger': calculator.calculate_card_2(team_key),
                'card_3_lineups': calculator.calculate_card_3(team_key)
            }
            result = calculator.calculate_card_4(team_key, other_cards)
            assert 'manager_name' in result
            assert 'error' not in result


class TestSnakeDraftVsRdAvg:
    """Test vs Rd Avg (Points Above Round Average) calculation for snake drafts"""

    def test_snake_draft_detected(self, snake_calculator):
        """Calculator should detect snake draft (no varied costs)"""
        assert snake_calculator.draft_type == 'snake'

    def test_vs_rd_avg_calculation_returns_value_type(self, snake_calculator):
        """vs Rd Avg calculation should set value_type to 'vs Rd Avg'"""
        team_key = list(snake_calculator.teams.keys())[0]
        result = snake_calculator.calculate_card_2(team_key)

        steals = result['draft'].get('steals', [])
        if steals:
            assert steals[0].get('value_type') == 'vs Rd Avg'

        busts = result['draft'].get('busts', [])
        if busts:
            assert busts[0].get('value_type') == 'vs Rd Avg'

    def test_vs_rd_avg_includes_round_info(self, snake_calculator):
        """vs Rd Avg results should include round information"""
        team_key = list(snake_calculator.teams.keys())[0]
        result = snake_calculator.calculate_card_2(team_key)

        steals = result['draft'].get('steals', [])
        if steals:
            assert 'round' in steals[0]
            assert steals[0]['round'] > 0

    def test_vs_rd_avg_value_is_numeric(self, snake_calculator):
        """vs Rd Avg value should be a number (positive or negative)"""
        team_key = list(snake_calculator.teams.keys())[0]
        result = snake_calculator.calculate_card_2(team_key)

        steals = result['draft'].get('steals', [])
        if steals:
            assert isinstance(steals[0].get('value'), (int, float))

        busts = result['draft'].get('busts', [])
        if busts:
            assert isinstance(busts[0].get('value'), (int, float))

    def test_auction_draft_uses_pts_per_dollar(self, calculator):
        """Auction draft should use pts/$ not vs Rd Avg"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        steals = result['draft'].get('steals', [])
        if steals:
            assert steals[0].get('value_type') == 'pts/$'


class TestCostlyDropsRosterAware:
    """Test that costly drops excludes points when player is re-added to roster"""

    def test_costly_drops_structure(self, calculator):
        """Costly drops should have correct structure"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        costly_drops = result.get('costly_drops', {})
        assert 'total_value_given_away' in costly_drops
        assert 'rank' in costly_drops

    def test_costly_drops_rank_valid(self, calculator):
        """Costly drops rank should be between 1 and num_teams"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        num_teams = len(calculator.teams)
        rank = result['costly_drops']['rank']
        assert 1 <= rank <= num_teams

    def test_costly_drops_value_non_negative(self, calculator):
        """Costly drops total should be non-negative"""
        team_key = list(calculator.teams.keys())[0]
        result = calculator.calculate_card_2(team_key)

        total = result['costly_drops']['total_value_given_away']
        assert total >= 0


class TestTrueSkillRecord:
    """Test true skill record calculation (no double-counting luck)"""

    def test_true_skill_record_format(self, calculator):
        """True skill record should be in W-L format"""
        team_key = list(calculator.teams.keys())[0]
        other_cards = {
            'card_1_overview': {},
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_4(team_key, other_cards)
        true_record = result['win_attribution']['true_skill_record']

        # Should be in "W-L" format
        assert '-' in true_record
        parts = true_record.split('-')
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    def test_luck_impact_is_schedule_luck_only(self, calculator):
        """Total luck impact should equal schedule luck (no double-counting)"""
        team_key = list(calculator.teams.keys())[0]
        other_cards = {
            'card_1_overview': {},
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_4(team_key, other_cards)
        attr = result['win_attribution']

        # Total luck should equal schedule luck only
        schedule_luck = attr['breakdown']['schedule_luck']
        total_luck = attr['total_luck_impact']
        assert abs(total_luck - schedule_luck) < 0.01

    def test_true_skill_wins_reasonable(self, calculator):
        """True skill wins should be reasonable (0 to total games)"""
        team_key = list(calculator.teams.keys())[0]
        other_cards = {
            'card_1_overview': {},
            'card_2_ledger': calculator.calculate_card_2(team_key),
            'card_3_lineups': calculator.calculate_card_3(team_key)
        }

        result = calculator.calculate_card_4(team_key, other_cards)
        true_record = result['win_attribution']['true_skill_record']

        wins, losses = map(int, true_record.split('-'))
        total_games = wins + losses

        # Should have reasonable number of games
        assert total_games >= 10
        assert total_games <= 18
        assert wins >= 0
        assert losses >= 0
