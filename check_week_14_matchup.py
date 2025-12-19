"""
Check Week 14 matchup data for Dobbs' Decision vs Straight Kash Patel Homie
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator

calc = FantasyWrappedCalculator('league_908221_2025.json')

# Find team keys
dobbs_key = None
kash_key = None

for tk, team in calc.teams.items():
    if team['team_name'] == "Dobbs' Decision":
        dobbs_key = tk
    if team['team_name'] == "Straight Kash Patel Homie":
        kash_key = tk

print("=" * 80)
print("WEEK 14 MATCHUP INVESTIGATION")
print("=" * 80)
print()

print(f"Dobbs' Decision: {dobbs_key}")
print(f"Straight Kash Patel Homie: {kash_key}")
print()

# Check Week 14 data
week_key = 'week_14'

if week_key in calc.weekly_data.get(dobbs_key, {}):
    dobbs_week_14 = calc.weekly_data[dobbs_key][week_key]
    print("DOBBS' DECISION - Week 14 Data:")
    print(f"  Your Score: {dobbs_week_14.get('actual_points', 0):.2f}")
    print(f"  Opponent ID: {dobbs_week_14.get('opponent_id', 'unknown')}")
    print(f"  Opponent Score (from your data): {dobbs_week_14.get('opponent_points', 0):.2f}")
    print()

if week_key in calc.weekly_data.get(kash_key, {}):
    kash_week_14 = calc.weekly_data[kash_key][week_key]
    print("STRAIGHT KASH PATEL HOMIE - Week 14 Data:")
    print(f"  Their Score: {kash_week_14.get('actual_points', 0):.2f}")
    print(f"  Opponent ID: {kash_week_14.get('opponent_id', 'unknown')}")
    print(f"  Opponent Score (from their data): {kash_week_14.get('opponent_points', 0):.2f}")
    print()

# Check if they actually played each other
if week_key in calc.weekly_data.get(dobbs_key, {}):
    dobbs_opp_id = dobbs_week_14.get('opponent_id', '')
    if dobbs_opp_id == kash_key:
        print("✓ MATCHUP CONFIRMED: You played each other in Week 14")
    else:
        print(f"❌ MISMATCH: Your opponent_id is {dobbs_opp_id}, not {kash_key}")
        opponent_name = calc.teams.get(dobbs_opp_id, {}).get('team_name', 'Unknown')
        print(f"   Your data says you played: {opponent_name}")

print()
print("=" * 80)
print("COMPARISON TO USER'S ACTUAL DATA")
print("=" * 80)
print()
print("User confirmed Week 14:")
print("  Dobbs' Decision: 106.66 points")
print("  Straight Kash Patel Homie: 103.44 points")
print()

if week_key in calc.weekly_data.get(dobbs_key, {}):
    dobbs_actual = dobbs_week_14.get('actual_points', 0)
    dobbs_opp_pts = dobbs_week_14.get('opponent_points', 0)

    dobbs_match = '✓' if abs(dobbs_actual - 106.66) < 0.01 else '❌'
    opp_diff = abs(dobbs_opp_pts - 103.44)
    opp_match = '✓' if opp_diff < 0.01 else f'❌ (off by {opp_diff:.2f})'

    print("Our data shows:")
    print(f"  Dobbs' Decision: {dobbs_actual:.2f} points {dobbs_match}")
    print(f"  Opponent (from Dobbs data): {dobbs_opp_pts:.2f} points {opp_match}")

if week_key in calc.weekly_data.get(kash_key, {}):
    kash_actual = kash_week_14.get('actual_points', 0)
    kash_diff = abs(kash_actual - 103.44)
    kash_match = '✓' if kash_diff < 0.01 else f'❌ (off by {kash_diff:.2f})'
    print(f"  Straight Kash (actual): {kash_actual:.2f} points {kash_match}")

print()
print("DIAGNOSIS:")
if week_key in calc.weekly_data.get(kash_key, {}):
    kash_actual = kash_week_14.get('actual_points', 0)
    if abs(kash_actual - 103.44) < 0.01:
        print(f"  ✓ Straight Kash's actual score is correct: {kash_actual:.2f}")
        print(f"  ❌ But Dobbs' opponent_points field shows: {dobbs_week_14.get('opponent_points', 0):.2f}")
        print(f"  → opponent_points field is stale/incorrect")
        print(f"  → SOLUTION: Always cross-reference opponent's actual_points, not opponent_points field")
    else:
        print(f"  ❌ Even Straight Kash's actual_points is wrong: {kash_actual:.2f} vs 103.44")
        print(f"  → Data may have been pulled mid-scoring or stat corrections applied")
