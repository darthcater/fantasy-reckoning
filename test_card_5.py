"""
Test Card 5: The Accounting
Generate and validate Card 5 for one test manager
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print('='*70)
print('TESTING CARD 5: THE ACCOUNTING')
print('='*70)

# Initialize calculator
calc = FantasyWrappedCalculator()

# Pick first team to test
test_team_key = list(calc.teams.keys())[0]
test_team = calc.teams[test_team_key]

print(f"\nTest Manager: {test_team['manager_name']}")
print(f"Team: {test_team['team_name']}")

# Generate all cards (Card 5 depends on Cards 1-4)
print("\nGenerating all cards...")
try:
    card_1 = calc.calculate_card_1(test_team_key)
    print("  ✓ Card 1")

    card_2 = calc.calculate_card_2(test_team_key)
    print("  ✓ Card 2")

    card_3 = calc.calculate_card_3(test_team_key)
    print("  ✓ Card 3")

    card_4 = calc.calculate_card_4(test_team_key)
    print("  ✓ Card 4")

    # Generate Card 5
    print("\nGenerating Card 5...")
    other_cards = {
        'card_1_draft': card_1,
        'card_2_identity': card_2,
        'card_3_inflection': card_3,
        'card_4_ecosystem': card_4
    }

    card_5 = calc.calculate_card_5(test_team_key, other_cards)
    print("✓ Card 5 generated successfully!")

    print("\n" + "="*70)
    print("CARD 5 RESULTS")
    print("="*70)

    print(f"\n📊 ACTUAL RECORD:")
    print(f"  Record: {card_5['actual_record']['record']}")
    print(f"  Wins: {card_5['actual_record']['wins']}")
    print(f"  Losses: {card_5['actual_record']['losses']}")

    print(f"\n🎯 WIN ATTRIBUTION:")
    print(f"  Draft Impact: {card_5['win_attribution']['draft_impact']:+d} wins")
    print(f"  Lineup Impact: {card_5['win_attribution']['lineup_impact']:+d} wins")
    print(f"  Waiver Impact: {card_5['win_attribution']['waiver_impact']:+d} wins")
    print(f"  Luck Impact: {card_5['win_attribution']['luck_impact']:+d} wins")
    print(f"  Injury Impact: {card_5['win_attribution']['injury_impact']:+d} wins")
    print(f"  Total Attributed: {card_5['win_attribution']['total_attributed']:+d} wins")

    print(f"\n  All Factors:")
    for factor in card_5['win_attribution']['factors']:
        print(f"    {factor['factor']}: {factor['impact']:+d} wins (Grade: {factor['grade']})")

    print(f"\n⚡ THE ONE THING TO FIX:")
    print(f"  Factor: {card_5['the_one_thing']['factor']}")
    print(f"  Current Grade: {card_5['the_one_thing']['current_grade']}")
    print(f"  Impact: {card_5['the_one_thing']['impact']:+d} wins")
    print(f"  Diagnosis: {card_5['the_one_thing']['diagnosis']}")

    print(f"\n📝 IMPROVEMENT CHECKLIST:")
    for i, item in enumerate(card_5['improvement_checklist'], 1):
        print(f"\n  {i}. [{item['priority']}] {item['category']}")
        print(f"     Action: {item['action']}")
        print(f"     Expected Impact: {item['expected_impact']}")

    print(f"\n🔮 PROJECTED 2026 RECORD:")
    print(f"  Record: {card_5['projected_2026_record']['record']}")
    print(f"  Wins: {card_5['projected_2026_record']['wins']}")
    print(f"  Improvement: {card_5['projected_2026_record']['improvement']:+d} wins")
    print(f"  Note: {card_5['projected_2026_record']['note']}")

    print(f"\n💡 INSIGHTS:")
    print(f"  Total Checklist Items: {card_5['insights']['total_checklist_items']}")
    print(f"  High Priority Items: {card_5['insights']['high_priority_items']}")

    if card_5['insights']['biggest_opportunity']:
        opp = card_5['insights']['biggest_opportunity']
        print(f"\n  Biggest Opportunity:")
        print(f"    {opp['category']}: {opp['action']}")
        print(f"    Expected Impact: {opp['expected_impact']}")

    # Save to file
    output_file = f"test_card_5_{test_team['manager_name'].replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'manager': test_team['manager_name'],
            'team': test_team['team_name'],
            'card_5': card_5
        }, f, indent=2)

    print(f"\n✓ Saved to: {output_file}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
