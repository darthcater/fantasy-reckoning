"""
Test Card 2: The Identity
Generate and validate Card 2 for one test manager
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print('='*70)
print('TESTING CARD 2: THE IDENTITY')
print('='*70)

# Initialize calculator
calc = FantasyWrappedCalculator()

# Pick first team to test
test_team_key = list(calc.teams.keys())[0]
test_team = calc.teams[test_team_key]

print(f"\nTest Manager: {test_team['manager_name']}")
print(f"Team: {test_team['team_name']}")

# Generate Card 2
print("\nGenerating Card 2...")
try:
    card_2 = calc.calculate_card_2(test_team_key)
    print("✓ Card 2 generated successfully!")

    print("\n" + "="*70)
    print("CARD 2 RESULTS")
    print("="*70)

    print(f"\n👤 MANAGER ARCHETYPE:")
    print(f"  Type: {card_2['archetype']['type']}")
    print(f"  Description: {card_2['archetype']['description']}")
    print(f"  Total Transactions: {card_2['archetype']['transactions_total']}")
    print(f"  Transactions/Week: {card_2['archetype']['transactions_per_week']}")

    print(f"\n📊 PARALLEL TIMELINES:")

    print(f"\n  Actual Record:")
    print(f"    Record: {card_2['timelines']['actual']['record']}")
    print(f"    Total Points: {card_2['timelines']['actual']['total_points']}")

    print(f"\n  Optimal Lineup Record:")
    print(f"    Record: {card_2['timelines']['optimal_lineup']['record']}")
    print(f"    Total Points: {card_2['timelines']['optimal_lineup']['total_points']}")
    print(f"    Wins Difference: {card_2['timelines']['optimal_lineup']['wins_difference']:+d}")

    print(f"\n  Optimal Adds Record:")
    print(f"    Record: {card_2['timelines']['optimal_adds']['record']}")
    print(f"    Wins Difference: {card_2['timelines']['optimal_adds']['wins_difference']:+d}")
    print(f"    Note: {card_2['timelines']['optimal_adds']['note']}")

    print(f"\n⚡ EFFICIENCY METRICS:")
    print(f"  Lineup Efficiency: {card_2['efficiency']['lineup_efficiency_pct']}%")
    print(f"  Avg Weekly Efficiency: {card_2['efficiency']['avg_weekly_efficiency']}%")
    print(f"  Total Bench Points Left: {card_2['efficiency']['total_bench_points_left']}")
    print(f"  Avg Bench Points/Week: {card_2['efficiency']['avg_bench_points_per_week']}")

    print(f"\n🎓 SKILL GRADES:")
    print(f"  Draft: {card_2['skill_grades']['draft']}")
    print(f"  Waivers: {card_2['skill_grades']['waivers']}")
    print(f"  Lineups: {card_2['skill_grades']['lineups']}")
    print(f"  Luck: {card_2['skill_grades']['luck']}")

    print(f"\n💡 INSIGHTS:")
    print(f"  Waiver Points Acquired: {card_2['insights']['waiver_points_acquired']}")
    print(f"  FAAB Spent on Waivers: ${card_2['insights']['waiver_faab_spent']}")
    print(f"  Points vs League Avg: {card_2['insights']['points_vs_league_avg']:+.1f}")

    # Save to file
    output_file = f"test_card_2_{test_team['manager_name'].replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'manager': test_team['manager_name'],
            'team': test_team['team_name'],
            'card_2': card_2
        }, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
