"""
Test Card 3: Inflection Points
Generate and validate Card 3 for one test manager
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print('='*70)
print('TESTING CARD 3: INFLECTION POINTS')
print('='*70)

# Initialize calculator
calc = FantasyWrappedCalculator()

# Pick first team to test
test_team_key = list(calc.teams.keys())[0]
test_team = calc.teams[test_team_key]

print(f"\nTest Manager: {test_team['manager_name']}")
print(f"Team: {test_team['team_name']}")

# Generate Card 3
print("\nGenerating Card 3...")
try:
    card_3 = calc.calculate_card_3(test_team_key)
    print("✓ Card 3 generated successfully!")

    print("\n" + "="*70)
    print("CARD 3 RESULTS")
    print("="*70)

    print(f"\n🎯 SUMMARY:")
    print(f"  Total Inflection Points: {card_3['summary']['total_inflection_points']}")
    print(f"  Lineup Mistakes: {card_3['summary']['lineup_mistakes']}")
    print(f"  Close Losses: {card_3['summary']['close_losses']}")
    print(f"  Boom/Bust Weeks: {card_3['summary']['boom_bust_weeks']}")
    print(f"  Cumulative Win Impact: {card_3['summary']['cumulative_win_impact']:+d}")

    if card_3['summary']['biggest_what_if']:
        print(f"\n⚡ BIGGEST WHAT-IF:")
        biggest = card_3['summary']['biggest_what_if']
        print(f"  {biggest['description']}")
        print(f"  Type: {biggest['type']}")
        print(f"  Impact: {biggest['impact']}")
        print(f"  Win Impact: {biggest['win_impact']:+d}")

    print(f"\n📊 INFLECTION POINTS:")
    for i, ip in enumerate(card_3['inflection_points'], 1):
        print(f"\n  {i}. {ip['description']}")
        print(f"     Type: {ip['type']}")
        print(f"     Impact: {ip['impact']}")
        print(f"     Win Impact: {ip['win_impact']:+d}")

        if ip['type'] == 'lineup_mistake':
            print(f"     Actual: {ip['details']['actual_score']} vs {ip['details']['opponent_score']}")
            print(f"     Optimal: {ip['details']['optimal_score']}")
            print(f"     Bench Left: {ip['details']['bench_points_left']}")
            print(f"     {ip['details']['outcome']}")

        elif ip['type'] == 'close_loss':
            print(f"     Lost by: {ip['details']['margin']} points")
            print(f"     Started: {ip['details']['wrong_starter']} ({ip['details']['wrong_starter_points']} pts)")
            print(f"     Benched: {ip['details']['bench_player']} ({ip['details']['bench_player_points']} pts)")
            print(f"     Swap Difference: {ip['details']['swap_difference']}")

        elif ip['type'] == 'boom_or_bust':
            print(f"     Score: {ip['details']['score']} (avg: {ip['details']['avg_score']})")
            print(f"     Deviation: {ip['details']['deviation']:+.1f}")
            print(f"     Result: {ip['details']['result']}")

    print(f"\n💡 INSIGHTS:")
    print(f"  Preventable Losses: {card_3['insights']['preventable_losses']}")
    print(f"  Total Preventable Win Impact: {card_3['insights']['total_preventable_win_impact']:+d}")

    # Save to file
    output_file = f"test_card_3_{test_team['manager_name'].replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'manager': test_team['manager_name'],
            'team': test_team['team_name'],
            'card_3': card_3
        }, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
