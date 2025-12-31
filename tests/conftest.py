"""
Pytest fixtures for Fantasy Reckoning tests

Provides sample data structures that mimic Yahoo Fantasy API responses.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime


@pytest.fixture
def sample_league():
    """Sample league configuration"""
    return {
        'league_key': '461.l.123456',
        'name': 'Test League',
        'season': 2025,
        'num_teams': 12,
        'current_week': 14,
        'playoff_start_week': 15,
        'scoring_type': 'head',
        'roster_positions': {
            'QB': 1,
            'RB': 2,
            'WR': 2,
            'TE': 1,
            'FLEX': 1,
            'K': 1,
            'DEF': 1,
            'BN': 6
        }
    }


@pytest.fixture
def sample_teams():
    """Sample team data for 12-team league"""
    teams = []
    for i in range(1, 13):
        teams.append({
            'team_key': f'461.l.123456.t.{i}',
            'team_name': f'Team {i}',
            'manager_name': f'Manager {i}',
            'wins': 7 + (i % 5) - 2,  # Vary wins 5-9
            'losses': 14 - (7 + (i % 5) - 2),
            'ties': 0,
            'points_for': 1400 + (i * 20),
            'points_against': 1350 + (i * 15),
            'standing': i
        })
    return teams


@pytest.fixture
def sample_draft():
    """Sample auction draft data"""
    draft_picks = []
    players = [
        ('Josh Allen', 'QB', 45),
        ('Christian McCaffrey', 'RB', 65),
        ('Tyreek Hill', 'WR', 52),
        ('Travis Kelce', 'TE', 38),
        ('Saquon Barkley', 'RB', 48),
        ('Ja\'Marr Chase', 'WR', 45),
        ('CeeDee Lamb', 'WR', 47),
        ('Davante Adams', 'WR', 35),
        ('Derrick Henry', 'RB', 42),
        ('Lamar Jackson', 'QB', 40),
        ('George Kittle', 'TE', 25),
        ('Bryce Young', 'QB', 2),  # Late round steal
    ]

    for i, (name, pos, cost) in enumerate(players):
        for team_num in range(1, 13):
            draft_picks.append({
                'player_id': str(1000 + i * 12 + team_num),
                'player_name': f'{name}' if team_num == 1 else f'Player {i * 12 + team_num}',
                'team_key': f'461.l.123456.t.{team_num}',
                'cost': cost if team_num == 1 else max(1, cost - 10),
                'round': (i // 12) + 1,
                'pick': i + 1
            })

    return draft_picks


@pytest.fixture
def sample_weekly_data():
    """Sample weekly matchup data"""
    weekly_data = {}

    for team_num in range(1, 13):
        team_key = f'461.l.123456.t.{team_num}'
        weekly_data[team_key] = {}

        for week in range(1, 15):
            # Generate opponent (simple round-robin)
            opponent_num = ((team_num + week - 2) % 12) + 1
            if opponent_num == team_num:
                opponent_num = (opponent_num % 12) + 1

            team_score = 100 + (team_num * 2) + (week * 1.5) + ((week * team_num) % 20)
            opp_score = 100 + (opponent_num * 2) + (week * 1.5) + ((week * opponent_num) % 20)

            # Build roster
            starters = []
            bench = []

            positions = ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'FLEX', 'K', 'DEF']
            for pos_idx, pos in enumerate(positions):
                player_id = str(1000 + team_num * 100 + pos_idx)
                actual_pts = 8 + (pos_idx * 2) + ((week + pos_idx) % 10)
                starters.append({
                    'player_id': player_id,
                    'player_name': f'Starter {pos_idx + 1}',
                    'selected_position': pos,
                    'eligible_positions': [pos] if pos not in ['FLEX'] else ['RB', 'WR', 'TE'],
                    'actual_points': actual_pts,
                    'projected_points': actual_pts - 2 + (pos_idx % 5)
                })

            # Bench players
            for bench_idx in range(6):
                player_id = str(2000 + team_num * 100 + bench_idx)
                bench_pts = 5 + (bench_idx * 1.5) + ((week + bench_idx) % 8)
                bench.append({
                    'player_id': player_id,
                    'player_name': f'Bench {bench_idx + 1}',
                    'selected_position': 'BN',
                    'eligible_positions': ['RB', 'WR'][bench_idx % 2:bench_idx % 2 + 1] or ['WR'],
                    'actual_points': bench_pts,
                    'projected_points': bench_pts - 1
                })

            weekly_data[team_key][f'week_{week}'] = {
                'week': week,
                'actual_points': team_score,
                'projected_points': team_score - 5,
                'opponent_id': f'461.l.123456.t.{opponent_num}',
                'opponent_points': opp_score,
                'result': 'W' if team_score > opp_score else 'L',
                'roster': {
                    'starters': starters,
                    'bench': bench
                }
            }

    return weekly_data


@pytest.fixture
def sample_transactions():
    """Sample waiver/trade transactions"""
    transactions = []

    # Base timestamp for Week 2 (mid-September 2025)
    base_ts = int(datetime(2025, 9, 15).timestamp())

    # Add some waiver pickups
    for i in range(20):
        team_num = (i % 12) + 1
        # Spread transactions across weeks 2-8
        trans_ts = base_ts + (i // 3) * 7 * 24 * 3600
        transactions.append({
            'transaction_id': str(5000 + i),
            'type': 'add/drop',
            'timestamp': trans_ts,
            'players': [
                {
                    'player_id': str(3000 + i),
                    'player_name': f'Waiver Add {i}',
                    'type': 'add',
                    'destination_team_key': f'461.l.123456.t.{team_num}'
                }
            ]
        })

    # Add a trade (Week 6)
    trade_ts = int(datetime(2025, 10, 15).timestamp())
    transactions.append({
        'transaction_id': '6000',
        'type': 'trade',
        'timestamp': trade_ts,
        'players': [
            {
                'player_id': '3100',
                'player_name': 'Traded Player A',
                'type': 'add',
                'source_team_key': '461.l.123456.t.1',
                'destination_team_key': '461.l.123456.t.2'
            },
            {
                'player_id': '3101',
                'player_name': 'Traded Player B',
                'type': 'add',
                'source_team_key': '461.l.123456.t.2',
                'destination_team_key': '461.l.123456.t.1'
            }
        ]
    })

    return transactions


@pytest.fixture
def sample_league_data(sample_league, sample_teams, sample_draft, sample_weekly_data, sample_transactions):
    """Complete sample league data structure"""
    return {
        'league': sample_league,
        'teams': sample_teams,
        'draft': sample_draft,
        'weekly_data': sample_weekly_data,
        'transactions': sample_transactions
    }


@pytest.fixture
def sample_snake_draft():
    """Sample snake draft data (no costs, uses rounds)"""
    draft_picks = []
    players = [
        ('Christian McCaffrey', 'RB', 1),
        ('Tyreek Hill', 'WR', 2),
        ('Travis Kelce', 'TE', 3),
        ('Josh Allen', 'QB', 4),
        ('Saquon Barkley', 'RB', 5),
        ('Ja\'Marr Chase', 'WR', 6),
        ('CeeDee Lamb', 'WR', 7),
        ('Davante Adams', 'WR', 8),
        ('Derrick Henry', 'RB', 9),
        ('Late Round Steal', 'RB', 10),  # Late round player who outperforms
    ]

    overall_pick = 0
    for rnd in range(1, 11):
        for team_num in range(1, 13):
            overall_pick += 1
            player_idx = (rnd - 1) % len(players)
            name = players[player_idx][0] if team_num == 1 else f'Player R{rnd}T{team_num}'

            draft_picks.append({
                'player_id': str(1000 + overall_pick),
                'player_name': name,
                'team_key': f'461.l.123456.t.{team_num}',
                'cost': 0,  # Snake draft - no cost
                'round': rnd,
                'pick': team_num,
                'overall_pick': overall_pick
            })

    return draft_picks


@pytest.fixture
def sample_snake_league_data(sample_league, sample_teams, sample_snake_draft, sample_weekly_data, sample_transactions):
    """Complete sample league data structure with snake draft"""
    return {
        'league': sample_league,
        'teams': sample_teams,
        'draft': sample_snake_draft,
        'weekly_data': sample_weekly_data,
        'transactions': sample_transactions
    }


@pytest.fixture
def sample_snake_league_file(sample_snake_league_data):
    """Create a temporary snake draft league file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_snake_league_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def snake_calculator(sample_snake_league_file):
    """Initialize calculator with snake draft data"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from fantasy_wrapped_calculator import FantasyWrappedCalculator
    return FantasyWrappedCalculator(data_file=sample_snake_league_file)


@pytest.fixture
def sample_costly_drops_transactions():
    """Transactions with drop/re-add scenario for testing roster-aware costly drops"""
    transactions = []

    # Base timestamp for Week 2
    base_ts = int(datetime(2025, 9, 15).timestamp())
    week_duration = 7 * 24 * 3600

    # Team 1 drops player 3001 in week 3
    transactions.append({
        'transaction_id': '5001',
        'type': 'add/drop',
        'timestamp': base_ts + 2 * week_duration,  # Week 3
        'players': [
            {
                'player_id': '3001',
                'player_name': 'Dropped Player',
                'type': 'drop',
                'source_team_key': '461.l.123456.t.1'
            }
        ]
    })

    # Team 1 re-adds same player 3001 in week 8
    transactions.append({
        'transaction_id': '5002',
        'type': 'add/drop',
        'timestamp': base_ts + 7 * week_duration,  # Week 8
        'players': [
            {
                'player_id': '3001',
                'player_name': 'Dropped Player',
                'type': 'add',
                'destination_team_key': '461.l.123456.t.1'
            }
        ]
    })

    return transactions


@pytest.fixture
def sample_league_file(sample_league_data):
    """Create a temporary league data file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_league_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def calculator(sample_league_file):
    """Initialize calculator with sample data"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from fantasy_wrapped_calculator import FantasyWrappedCalculator
    return FantasyWrappedCalculator(data_file=sample_league_file)
