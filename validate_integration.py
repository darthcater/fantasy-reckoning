#!/usr/bin/env python3
"""
Integration Validation Script

Validates that a data file (from any platform) meets all requirements
for the Fantasy Reckoning card generator.

Usage:
    python validate_integration.py <data_file.json>
"""

import json
import sys


def validate_data(filepath: str) -> bool:
    """Run all validation tests on a data file."""

    print("=" * 60)
    print("FANTASY RECKONING - DATA VALIDATION")
    print("=" * 60)
    print(f"File: {filepath}\n")

    try:
        with open(filepath, 'r') as f:
            d = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load file: {e}")
        return False

    results = []

    # Test 1: Week Coverage
    print("[Test 1] Week Coverage")
    weekly_data = d.get('weekly_data', {})
    current_week = d.get('league', {}).get('current_week', 0)
    first_team = list(weekly_data.values())[0] if weekly_data else {}
    actual_weeks = len(first_team)

    print(f"  Weeks per team: {actual_weeks}")
    print(f"  current_week in metadata: {current_week}")

    status1 = actual_weeks >= 14 and current_week >= 14
    if not status1:
        print(f"  ISSUE: Need at least 14 weeks of data")
    print(f"  Status: {'PASS' if status1 else 'FAIL'}\n")
    results.append(("Week Coverage", status1))

    # Test 2: Roster Completeness
    print("[Test 2] Roster Completeness")
    first_week = list(first_team.values())[0] if first_team else {}
    roster = first_week.get('roster', {})
    starters = roster.get('starters', [])
    bench = roster.get('bench', [])
    has_bench = len(bench) > 0
    bench_has_points = all(p.get('actual_points') is not None for p in bench) if bench else False

    print(f"  Starters: {len(starters)}")
    print(f"  Bench: {len(bench)}")
    print(f"  Bench has points: {bench_has_points}")

    status2 = has_bench and bench_has_points
    if not status2:
        print(f"  ISSUE: Need bench players with points for lineup efficiency calculation")
    print(f"  Status: {'PASS' if status2 else 'FAIL'}\n")
    results.append(("Roster Completeness", status2))

    # Test 3: Transaction Integrity
    print("[Test 3] Transaction Integrity")
    transactions = d.get('transactions', [])
    trades = [t for t in transactions if t.get('type') == 'trade']
    print(f"  Total transactions: {len(transactions)}")
    print(f"  Trades: {len(trades)}")

    trade_valid = True
    for trade in trades:
        for player in trade.get('players', []):
            if player['type'] == 'add' and player.get('source_team_key') is None:
                trade_valid = False
                print(f"    ISSUE: {player['player_name']} add missing source_team_key")
            if player['type'] == 'drop' and player.get('destination_team_key') is None:
                trade_valid = False
                print(f"    ISSUE: {player['player_name']} drop missing destination_team_key")

    status3 = trade_valid
    print(f"  Status: {'PASS' if status3 else 'FAIL'}\n")
    results.append(("Transaction Integrity", status3))

    # Test 4: Points Population
    print("[Test 4] Points Population")
    missing_points = 0
    total_players = 0
    for player in starters + bench:
        total_players += 1
        if player.get('actual_points') is None:
            missing_points += 1
            print(f"    ISSUE: Missing points for {player.get('player_name')}")

    status4 = missing_points == 0
    print(f"  Players checked: {total_players}")
    print(f"  Missing points: {missing_points}")
    print(f"  Status: {'PASS' if status4 else 'FAIL'}\n")
    results.append(("Points Population", status4))

    # Test 5: Draft Data
    print("[Test 5] Draft Data")
    draft = d.get('draft', [])
    print(f"  Total picks: {len(draft)}")

    has_round = all('round' in p for p in draft) if draft else False
    has_cost = all('cost' in p for p in draft) if draft else False
    print(f"  Has round field: {has_round}")
    print(f"  Has cost field: {has_cost}")

    if draft:
        sample = draft[0]
        print(f"  Sample: {sample.get('player_name')} Rd{sample.get('round')} ${sample.get('cost')}")

    status5 = len(draft) > 0 and (has_round or has_cost)
    if not status5:
        print(f"  ISSUE: Draft data missing or incomplete")
    print(f"  Status: {'PASS' if status5 else 'FAIL'}\n")
    results.append(("Draft Data", status5))

    # Test 5b: Keeper/Dynasty Detection (informational)
    print("[Test 5b] Keeper/Dynasty Detection")
    keeper_count = sum(1 for p in draft if p.get('is_keeper'))
    league_type = d.get('league', {}).get('league_type', 'redraft')
    league_name = d.get('league', {}).get('name', '').lower()

    detected_type = 'redraft'
    if 'dynasty' in league_name:
        detected_type = 'dynasty'
    elif keeper_count > 0 or 'keeper' in league_name:
        detected_type = 'keeper'

    print(f"  Keeper picks: {keeper_count}")
    print(f"  League type (from metadata): {league_type}")
    print(f"  League type (detected): {detected_type}")

    if keeper_count > 0:
        print(f"  NOTE: Keeper picks will be excluded from Best Value/Bust calculations")

    # This is informational, always passes
    print(f"  Status: INFO\n")

    # Test 6: League Metadata
    print("[Test 6] League Metadata")
    league = d.get('league', {})
    required_fields = ['name', 'season', 'num_teams', 'current_week']
    missing_fields = [f for f in required_fields if f not in league]

    print(f"  League name: {league.get('name', 'MISSING')}")
    print(f"  Season: {league.get('season', 'MISSING')}")
    print(f"  Num teams: {league.get('num_teams', 'MISSING')}")

    status6 = len(missing_fields) == 0
    if missing_fields:
        print(f"  ISSUE: Missing fields: {missing_fields}")
    print(f"  Status: {'PASS' if status6 else 'FAIL'}\n")
    results.append(("League Metadata", status6))

    # Test 7: Teams Data
    print("[Test 7] Teams Data")
    teams = d.get('teams', [])
    print(f"  Teams count: {len(teams)}")

    if teams:
        sample_team = teams[0]
        print(f"  Sample team keys: {list(sample_team.keys())[:5]}")
        has_team_key = all('team_key' in t for t in teams)
        has_name = all('team_name' in t or 'name' in t for t in teams)
        print(f"  All have team_key: {has_team_key}")
        print(f"  All have team_name: {has_name}")
        status7 = has_team_key and has_name
    else:
        status7 = False
        print(f"  ISSUE: No teams data")

    print(f"  Status: {'PASS' if status7 else 'FAIL'}\n")
    results.append(("Teams Data", status7))

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_pass = all(passed for _, passed in results)
    for name, passed in results:
        status_str = "PASS" if passed else "FAIL"
        print(f"  {name}: {status_str}")

    print(f"\nOverall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")

    return all_pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_integration.py <data_file.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    success = validate_data(filepath)
    sys.exit(0 if success else 1)
