"""
Test Card 4: The Ecosystem
Generate and validate Card 4 for one test manager
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print('='*70)
print('TESTING CARD 4: THE ECOSYSTEM')
print('='*70)

# Initialize calculator
calc = FantasyWrappedCalculator()

# Pick first team to test
test_team_key = list(calc.teams.keys())[0]
test_team = calc.teams[test_team_key]

print(f"\nTest Manager: {test_team['manager_name']}")
print(f"Team: {test_team['team_name']}")

# Generate Card 4
print("\nGenerating Card 4...")
try:
    card_4 = calc.calculate_card_4(test_team_key)
    print("✓ Card 4 generated successfully!")

    print("\n" + "="*70)
    print("CARD 4 RESULTS")
    print("="*70)

    print(f"\n💔 DROPS ANALYSIS:")
    print(f"  Total Drops: {card_4['drops_analysis']['total_drops']}")
    print(f"  Drops That Hurt: {card_4['drops_analysis']['drops_that_hurt']}")
    print(f"  Total ROS Points Given Away: {card_4['drops_analysis']['total_ros_points_given_away']}")

    print(f"\n  Worst Drops:")
    for i, drop in enumerate(card_4['drops_analysis']['worst_drops'][:3], 1):
        print(f"    {i}. Player {drop['player_id']}")
        print(f"       Dropped Week {drop['drop_week']}, picked up by {drop['acquired_by']}")
        print(f"       ROS Points: {drop['ros_points']}, FAAB Cost: ${drop['faab_cost']}")

    print(f"\n🎯 LOST BIDS ANALYSIS:")
    print(f"  Note: {card_4['lost_bids_analysis']['note']}")
    print(f"  Lost Bids Count: {card_4['lost_bids_analysis']['lost_bids_count']}")

    print(f"\n📊 OPTIMAL FA ANALYSIS:")
    print(f"  Actual Waiver Points: {card_4['optimal_fa_analysis']['actual_waiver_points']}")
    print(f"  Optimal Waiver Points: {card_4['optimal_fa_analysis']['optimal_waiver_points']}")
    print(f"  Opportunity Cost: {card_4['optimal_fa_analysis']['opportunity_cost']}")
    print(f"  Efficiency: {card_4['optimal_fa_analysis']['efficiency_pct']}%")

    print(f"\n  Sample Best Available FAs:")
    for week_data in card_4['optimal_fa_analysis']['sample_weeks']:
        print(f"    Week {week_data['week']}:")
        for fa in week_data['top_available'][:2]:
            print(f"      Player {fa['player_id']}: {fa['ros_points']} ROS points")

    print(f"\n🌍 ECOSYSTEM IMPACT:")
    print(f"  Players Given to Rivals: {card_4['ecosystem_impact']['players_given_to_rivals']}")
    print(f"  Points Given to Rivals: {card_4['ecosystem_impact']['points_given_to_rivals']}")

    if card_4['ecosystem_impact']['biggest_mistake']:
        mistake = card_4['ecosystem_impact']['biggest_mistake']
        print(f"\n  Biggest Mistake:")
        print(f"    Player {mistake['player_id']} - {mistake['ros_points']} points to {mistake['acquired_by']}")

    print(f"\n💡 INSIGHTS:")
    print(f"  Total Opportunity Cost: {card_4['insights']['total_opportunity_cost']}")
    print(f"  Avg Opportunity Cost/Week: {card_4['insights']['avg_opportunity_cost_per_week']}")

    # Save to file
    output_file = f"test_card_4_{test_team['manager_name'].replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'manager': test_team['manager_name'],
            'team': test_team['team_name'],
            'card_4': card_4
        }, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
