"""
Detailed weekly breakdown for Dobbs' Decision
Show each week's scores to identify discrepancy source
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator

# Load calculator
calc = FantasyWrappedCalculator('league_908221_2025.json')

# Find Dobbs' Decision team key
team_key = None
for tk, team in calc.teams.items():
    if team['team_name'] == "Dobbs' Decision":
        team_key = tk
        break

if not team_key:
    print("ERROR: Could not find Dobbs' Decision")
    exit(1)

print("=" * 100)
print("WEEKLY SCORE BREAKDOWN: Dobbs' Decision")
print("=" * 100)
print()

# Show each week's performance
running_total_pf = 0
running_total_pa = 0
running_wins = 0
running_losses = 0

print(f"{'Week':<6} {'Your Score':<12} {'Opp Score':<12} {'Result':<8} {'Running PF':<12} {'Running PA':<12} {'Record':<10}")
print("-" * 100)

for week in range(1, 15):
    week_key = f'week_{week}'

    if week_key not in calc.weekly_data.get(team_key, {}):
        print(f"{week:<6} {'NO DATA':<12} {'NO DATA':<12} {'-':<8} {running_total_pf:<12.2f} {running_total_pa:<12.2f} {running_wins}-{running_losses}")
        continue

    week_data = calc.weekly_data[team_key][week_key]
    your_score = week_data.get('actual_points', 0)
    opp_score = week_data.get('opponent_points', 0)

    # Determine result
    if your_score > opp_score:
        result = "WIN"
        running_wins += 1
    elif your_score < opp_score:
        result = "LOSS"
        running_losses += 1
    else:
        result = "TIE"

    # Update running totals
    running_total_pf += your_score
    running_total_pa += opp_score

    print(f"{week:<6} {your_score:<12.2f} {opp_score:<12.2f} {result:<8} {running_total_pf:<12.2f} {running_total_pa:<12.2f} {running_wins}-{running_losses}")

print("-" * 100)
print()

# Compare to team-level data
team_data = calc.teams[team_key]
team_pf = team_data['points_for']
team_pa = team_data['points_against']
team_record = f"{team_data['wins']}-{team_data['losses']}-{team_data['ties']}"

print("COMPARISON:")
print(f"  Team-level PF:  {team_pf:.2f}")
print(f"  Weekly sum PF:  {running_total_pf:.2f}")
print(f"  Difference:     {abs(team_pf - running_total_pf):.2f} points {'⚠️  MISMATCH' if abs(team_pf - running_total_pf) > 1 else '✓ MATCH'}")
print()
print(f"  Team-level PA:  {team_pa:.2f}")
print(f"  Weekly sum PA:  {running_total_pa:.2f}")
print(f"  Difference:     {abs(team_pa - running_total_pa):.2f} points {'⚠️  MISMATCH' if abs(team_pa - running_total_pa) > 1 else '✓ MATCH'}")
print()
print(f"  Team-level record:  {team_record}")
print(f"  Weekly sum record:  {running_wins}-{running_losses}-0")
print(f"  Difference:         {'⚠️  MISMATCH' if team_record != f'{running_wins}-{running_losses}-0' else '✓ MATCH'}")
print()

# If there's a mismatch, calculate what week 13 PF would be
if abs(team_pf - running_total_pf) > 1:
    week_13_total = 0
    week_13_wins = 0
    week_13_losses = 0

    for week in range(1, 14):  # Weeks 1-13
        week_key = f'week_{week}'
        if week_key in calc.weekly_data.get(team_key, {}):
            week_data = calc.weekly_data[team_key][week_key]
            week_13_total += week_data.get('actual_points', 0)
            your_score = week_data.get('actual_points', 0)
            opp_score = week_data.get('opponent_points', 0)
            if your_score > opp_score:
                week_13_wins += 1
            elif your_score < opp_score:
                week_13_losses += 1

    print("HYPOTHESIS: Team-level data is from Week 13 (before Week 14 was played)")
    print(f"  Week 1-13 PF:       {week_13_total:.2f}")
    print(f"  Team-level PF:      {team_pf:.2f}")
    print(f"  Match?              {abs(team_pf - week_13_total) < 1 and '✓ YES - Team data is from Week 13!' or f'❌ NO - Still {abs(team_pf - week_13_total):.2f} pts off'}")
    print()
    print(f"  Week 1-13 Record:   {week_13_wins}-{week_13_losses}-0")
    print(f"  Team-level Record:  {team_record}")
    print(f"  Match?              {team_record == f'{week_13_wins}-{week_13_losses}-0' and '✓ YES' or '❌ NO'}")
    print()

    # Show Week 14 specifically
    week_14_key = 'week_14'
    if week_14_key in calc.weekly_data.get(team_key, {}):
        week_14_data = calc.weekly_data[team_key][week_14_key]
        week_14_score = week_14_data.get('actual_points', 0)
        week_14_opp = week_14_data.get('opponent_points', 0)
        week_14_result = 'WON' if week_14_score > week_14_opp else 'LOST'

        print(f"WEEK 14 DATA:")
        print(f"  Your Score: {week_14_score:.2f}")
        print(f"  Opp Score:  {week_14_opp:.2f}")
        print(f"  Result:     {week_14_result}")
        print(f"  Impact:     This is the missing {week_14_score:.2f} points and the {week_14_result.lower()} game")

print()
print("=" * 100)
print("CONCLUSION")
print("=" * 100)

if abs(team_pf - running_total_pf) > 1:
    print("⚠️  DATA INCONSISTENCY DETECTED")
    print()
    print("The team-level summary data (PF, PA, Record) appears to be from Week 13,")
    print("but the weekly game-by-game data includes Week 14. This causes:")
    print()
    print("  1. PF/PA values to be ~100+ points too low")
    print("  2. Record to potentially be off by 1 game")
    print("  3. All card calculations to use incomplete data")
    print()
    print("RECOMMENDATION: Re-pull league data to get Week 14 summary stats")
else:
    print("✓ Data is consistent across team-level and weekly breakdowns")
