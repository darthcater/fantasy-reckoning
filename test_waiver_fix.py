"""
Test the fixed waiver calculation for Dobbs' Decision
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator

calc = FantasyWrappedCalculator('league_908221_2025.json')

# Find Dobbs' Decision
dobbs_key = None
for tk, team in calc.teams.items():
    if team['team_name'] == "Dobbs' Decision":
        dobbs_key = tk
        break

print("=" * 100)
print("TESTING FIXED WAIVER CALCULATION - Dobbs' Decision")
print("=" * 100)
print()

# Calculate Card 4 with fixed parsing
card_4 = calc.calculate_card_4(dobbs_key)

waiver_metric = card_4.get('waiver_contribution', {})

print("WAIVER WIRE CONTRIBUTION (FIXED):")
print("-" * 100)
print(f"  Total Points Added: {waiver_metric.get('total_points_added', 0):.1f}")
print(f"  League Rank: {waiver_metric.get('league_rank', 'N/A')}")
print(f"  Percentile: {waiver_metric.get('percentile', 0):.1f}%")
print(f"  Grade: {waiver_metric.get('grade', 'N/A')}")
print(f"  League Average: {waiver_metric.get('league_avg_points', 0):.1f} points")
print(f"  Playoff Average: {waiver_metric.get('playoff_avg_points', 0):.1f} points")
print(f"  Gap to Playoff Avg: {waiver_metric.get('gap_to_playoff_avg', 0):+.1f} points")
print()

# Show detailed adds
adds_detail = card_4.get('added_players_detail', [])
if adds_detail:
    print("YOUR WAIVER/FA ADDS (Detailed):")
    print("-" * 100)
    print(f"{'Player':<30} {'Add Week':<10} {'ROS Pts':<10} {'Started':<10} {'PPG':<10}")
    print("-" * 100)

    for add in adds_detail[:10]:  # Top 10
        print(f"{add.get('player_name', 'Unknown'):<30} "
              f"Week {add.get('add_week', '?'):<7} "
              f"{add.get('ros_points', 0):<10.1f} "
              f"{add.get('points_started', 0):<10.1f} "
              f"{add.get('ppg', 0):<10.1f}")

print()
print("=" * 100)
print("COMPARISON")
print("=" * 100)
print()
print("Before fix (WRONG):  0 points, rank 9/14")
print(f"After fix (CORRECT): {waiver_metric.get('total_points_added', 0):.1f} points, rank {waiver_metric.get('league_rank', 'N/A')}")
print()

if waiver_metric.get('total_points_added', 0) > 0:
    print("✅ BUG FIXED - Now showing actual waiver contribution!")
else:
    print("⚠️  Still showing 0 - may need to investigate further")
