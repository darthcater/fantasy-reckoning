"""
Test Card 1: The Draft
Generate and validate Card 1 for one test manager
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print('='*70)
print('TESTING CARD 1: THE DRAFT')
print('='*70)

# Initialize calculator
calc = FantasyWrappedCalculator()

# Pick first team to test
test_team_key = list(calc.teams.keys())[0]
test_team = calc.teams[test_team_key]

print(f"\nTest Manager: {test_team['manager_name']}")
print(f"Team: {test_team['team_name']}")
print(f"Auction Budget Spent: ${test_team['auction_budget_spent']}")

# Generate Card 1
print("\nGenerating Card 1...")
try:
    card_1 = calc.calculate_card_1(test_team_key)
    print("✓ Card 1 generated successfully!")

    print("\n" + "="*70)
    print("CARD 1 RESULTS")
    print("="*70)

    print(f"\n📊 DRAFT PERFORMANCE:")
    print(f"  Draft ROI: ${card_1['draft_roi']}/point")
    print(f"  League Avg: ${card_1['league_avg_roi']}/point")
    print(f"  Rank: {card_1['rank']} out of {len(calc.teams)}")
    print(f"  Grade: {card_1['grade']}")
    print(f"  Total Spent: ${card_1['total_spent']}")
    print(f"  Total Points: {card_1['total_points']}")

    print(f"\n🌟 TOP 3 STEALS:")
    for i, steal in enumerate(card_1['steals'], 1):
        print(f"  {i}. Player {steal['player_id']}")
        print(f"     Cost: ${steal['cost']}, Points: {steal['points']}")
        print(f"     $/point: ${steal['per_point']}")

    print(f"\n💸 TOP 3 BUSTS:")
    for i, bust in enumerate(card_1['busts'], 1):
        print(f"  {i}. Player {bust['player_id']}")
        print(f"     Cost: ${bust['cost']}, Points: {bust['points']}")
        print(f"     $/point: ${bust['per_point']}")

    # Save to file
    output_file = f"test_card_1_{test_team['manager_name'].replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'manager': test_team['manager_name'],
            'team': test_team['team_name'],
            'card_1': card_1
        }, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
