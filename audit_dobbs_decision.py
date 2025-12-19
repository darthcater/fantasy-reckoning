"""
Data Accuracy Audit for Dobbs' Decision
Verify all data against Yahoo standings
"""

import json

# Load league data
with open('league_908221_2025.json', 'r') as f:
    league_data = json.load(f)

# Find Dobbs' Decision team
dobbs_team = None
for team in league_data['teams']:
    if team['team_name'] == "Dobbs' Decision":
        dobbs_team = team
        break

if not dobbs_team:
    print("ERROR: Could not find Dobbs' Decision in league data")
    exit(1)

print("=" * 80)
print("DATA AUDIT: Dobbs' Decision")
print("=" * 80)
print()

# Basic Team Info
print("TEAM INFORMATION:")
print(f"  Team Name: {dobbs_team['team_name']}")
print(f"  Manager: {dobbs_team['manager_name']}")
print(f"  Team Key: {dobbs_team['team_key']}")
print(f"  Final Standing: {dobbs_team['final_standing']}")
print()

# Record
print("RECORD:")
print(f"  Wins: {dobbs_team['wins']}")
print(f"  Losses: {dobbs_team['losses']}")
print(f"  Ties: {dobbs_team['ties']}")
print(f"  Record: {dobbs_team['wins']}-{dobbs_team['losses']}-{dobbs_team['ties']}")
print()

# Points
print("POINTS:")
print(f"  Points For (PF): {dobbs_team['points_for']:.2f}")
print(f"  Points Against (PA): {dobbs_team['points_against']:.2f}")
print()

# FAAB Budget
print("FAAB BUDGET:")
print(f"  Total Budget: ${dobbs_team['auction_budget_total']}")
print(f"  Auction Spent: ${dobbs_team['auction_budget_spent']}")
print(f"  FAAB Balance: ${dobbs_team['faab_balance']}")
print(f"  FAAB Spent: ${int(dobbs_team['auction_budget_total']) - int(dobbs_team['auction_budget_spent']) - int(dobbs_team['faab_balance'])}")
print()

# Transaction Analysis
team_key = dobbs_team['team_key']
total_adds = 0
fa_adds = 0
waiver_adds = 0
trade_adds = 0
drops = 0

transactions_list = []

for trans in league_data['transactions']:
    for player in trans.get('players', []):
        if player.get('destination_team_key') == team_key:
            trans_type = player.get('type', 'unknown')
            source_type = player.get('source_type', 'unknown')

            if trans_type == 'add':
                total_adds += 1
                if source_type == 'freeagents':
                    fa_adds += 1
                elif source_type == 'waivers':
                    waiver_adds += 1

                transactions_list.append({
                    'id': trans['transaction_id'],
                    'type': trans_type,
                    'source': source_type,
                    'player': player.get('player_name', f"Player {player.get('player_id')}"),
                    'position': player.get('position', '?')
                })
            elif trans_type == 'trade':
                trade_adds += 1
                transactions_list.append({
                    'id': trans['transaction_id'],
                    'type': trans_type,
                    'source': source_type,
                    'player': player.get('player_name', f"Player {player.get('player_id')}"),
                    'position': player.get('position', '?')
                })

        if player.get('source_team_key') == team_key and player.get('type') == 'drop':
            drops += 1

print("TRANSACTION COUNTS:")
print(f"  Total Adds: {total_adds}")
print(f"  - Free Agent Adds: {fa_adds}")
print(f"  - Waiver Wire Adds: {waiver_adds}")
print(f"  - Trade Acquisitions: {trade_adds}")
print(f"  Total Drops: {drops}")
print(f"  Total Moves (Adds + Drops): {total_adds + drops}")
print()

# Show recent transactions
print("ALL TRANSACTIONS (chronological):")
print("-" * 80)
for i, trans in enumerate(reversed(transactions_list), 1):
    print(f"{i:2d}. Trans #{trans['id']}: {trans['type']:5s} | {trans['source']:10s} | {trans['player']:30s} ({trans['position']})")
print()

# Expected vs Actual (from standings table)
print("=" * 80)
print("COMPARISON TO EXPECTED VALUES (from standings)")
print("=" * 80)
print()
print("Based on the standings you provided, Dobbs' Decision should have:")
print("  Expected Record: 6-7-0 ✓ or different?")
print("  Expected PF: ??? (please verify)")
print("  Expected PA: ??? (please verify)")
print("  Expected Waiver Moves: ??? (please verify)")
print("  Expected Total Moves: ??? (please verify)")
print()
print(f"Our data shows:")
print(f"  Actual Record: {dobbs_team['wins']}-{dobbs_team['losses']}-{dobbs_team['ties']}")
print(f"  Actual PF: {dobbs_team['points_for']:.2f}")
print(f"  Actual PA: {dobbs_team['points_against']:.2f}")
print(f"  Actual Waiver Adds: {waiver_adds}")
print(f"  Actual Total Moves: {total_adds + drops}")
print()

# Check weekly data completeness
from fantasy_wrapped_calculator import FantasyWrappedCalculator

calc = FantasyWrappedCalculator('league_908221_2025.json')
weeks_with_data = []
for week in range(1, 15):
    week_key = f'week_{week}'
    if week_key in calc.weekly_data.get(team_key, {}):
        week_data = calc.weekly_data[team_key][week_key]
        weeks_with_data.append(week)

print("WEEKLY DATA COMPLETENESS:")
print(f"  Weeks with data: {len(weeks_with_data)}/14")
print(f"  Weeks present: {weeks_with_data}")
if len(weeks_with_data) < 14:
    missing = [w for w in range(1, 15) if w not in weeks_with_data]
    print(f"  ⚠️  MISSING WEEKS: {missing}")
print()

# Calculate total PF from weekly data
total_pf_from_weeks = 0
for week in weeks_with_data:
    week_key = f'week_{week}'
    week_data = calc.weekly_data[team_key][week_key]
    total_pf_from_weeks += week_data.get('actual_points', 0)

print("PF VERIFICATION:")
print(f"  PF from team data: {dobbs_team['points_for']:.2f}")
print(f"  PF from weekly sum: {total_pf_from_weeks:.2f}")
if abs(dobbs_team['points_for'] - total_pf_from_weeks) > 1:
    print(f"  ⚠️  MISMATCH: Difference of {abs(dobbs_team['points_for'] - total_pf_from_weeks):.2f} points")
else:
    print(f"  ✓ MATCH")
print()

print("=" * 80)
print("PLEASE VERIFY THE FOLLOWING:")
print("=" * 80)
print("1. Is your record 6-7-0 correct?")
print(f"2. Is your PF {dobbs_team['points_for']:.2f} correct?")
print(f"3. Is your PA {dobbs_team['points_against']:.2f} correct?")
print(f"4. Did you make {waiver_adds} waiver wire adds (using FAAB)?")
print(f"5. Did you make {fa_adds} free agent adds (no FAAB)?")
print(f"6. Did you make {total_adds + drops} total moves this season?")
print(f"7. Do you have ${dobbs_team['faab_balance']} FAAB remaining?")
print()
print("Please check your Yahoo league page and confirm each value.")
