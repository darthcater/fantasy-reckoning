"""
Test Complete Fantasy Wrapped Output
Generate all 6 cards for one test manager
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print('='*70)
print('TESTING COMPLETE FANTASY WRAPPED OUTPUT')
print('='*70)

# Initialize calculator
calc = FantasyWrappedCalculator()

# Pick first team to test
test_team_key = list(calc.teams.keys())[0]
test_team = calc.teams[test_team_key]

print(f"\nTest Manager: {test_team['manager_name']}")
print(f"Team: {test_team['team_name']}")
print(f"Season: {calc.league['season']}")
print(f"League: {calc.league['name']}")

# Generate all cards
print("\n" + "="*70)
print("GENERATING ALL CARDS")
print("="*70)

cards = {
    'manager_id': test_team_key,
    'manager_name': test_team['manager_name'],
    'team_name': test_team['team_name'],
    'season': calc.league['season'],
    'league': calc.league['name'],
    'cards': {}
}

try:
    print("\n1. Card I: The Draft Tribunal...")
    cards['cards']['card_1_draft'] = calc.calculate_card_1(test_team_key)
    print("   ✓ Draft ROI: ${0}/point, Rank: {1}/14, Grade: {2}".format(
        cards['cards']['card_1_draft']['draft_roi'],
        cards['cards']['card_1_draft']['rank'],
        cards['cards']['card_1_draft']['grade']
    ))

    print("\n2. Card II: The Three Fates...")
    cards['cards']['card_2_identity'] = calc.calculate_card_2(test_team_key)
    print("   ✓ Archetype: {0}".format(cards['cards']['card_2_identity']['archetype']['type']))
    print("   ✓ Actual Record: {0}".format(cards['cards']['card_2_identity']['timelines']['actual']['record']))
    print("   ✓ Optimal Lineup Record: {0} ({1:+d} wins)".format(
        cards['cards']['card_2_identity']['timelines']['optimal_lineup']['record'],
        cards['cards']['card_2_identity']['timelines']['optimal_lineup']['wins_difference']
    ))

    print("\n3. Card III: The Fatal Error...")
    cards['cards']['card_3_inflection'] = calc.calculate_card_3(test_team_key)
    print("   ✓ Found {0} inflection points".format(
        cards['cards']['card_3_inflection']['summary']['total_inflection_points']
    ))
    print("   ✓ Preventable Losses: {0}".format(
        cards['cards']['card_3_inflection']['insights']['preventable_losses']
    ))

    print("\n4. Card IV: The Forsaken...")
    cards['cards']['card_4_ecosystem'] = calc.calculate_card_4(test_team_key)
    print("   ✓ Total Drops: {0}".format(
        cards['cards']['card_4_ecosystem']['drops_analysis']['total_drops']
    ))
    print("   ✓ Waiver Opportunity Cost: {0} points".format(
        cards['cards']['card_4_ecosystem']['optimal_fa_analysis']['opportunity_cost']
    ))

    print("\n5. Card V: The Final Ledger...")
    cards['cards']['card_5_accounting'] = calc.calculate_card_5(test_team_key, cards['cards'])
    print("   ✓ The One Thing: {0}".format(
        cards['cards']['card_5_accounting']['the_one_thing']['factor']
    ))
    print("   ✓ Projected 2026 Record: {0} ({1:+d} wins improvement)".format(
        cards['cards']['card_5_accounting']['projected_2026_record']['record'],
        cards['cards']['card_5_accounting']['projected_2026_record']['improvement']
    ))

    print("\n6. The Six Faces: Your Manager Profile...")
    cards['cards']['spider_chart'] = calc.calculate_spider_chart(test_team_key, cards['cards'])
    print("   ✓ Profile: {0}".format(cards['cards']['spider_chart']['profile_summary']))
    print("   ✓ Strengths: {0}".format(', '.join(cards['cards']['spider_chart']['strengths'])))
    print("   ✓ Weaknesses: {0}".format(', '.join(cards['cards']['spider_chart']['weaknesses'])))

    print("\n" + "="*70)
    print("✓ ALL CARDS GENERATED SUCCESSFULLY!")
    print("="*70)

    # Save complete output
    output_file = f"fantasy_wrapped_{test_team['manager_name'].replace(' ', '_').lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(cards, f, indent=2)

    print(f"\n✓ Complete Fantasy Wrapped saved to: {output_file}")

    # Print file size
    import os
    file_size = os.path.getsize(output_file)
    print(f"✓ File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    # Display summary
    print("\n" + "="*70)
    print("FANTASY WRAPPED SUMMARY")
    print("="*70)

    print(f"\n{test_team['manager_name']}'s 2025 Season:")
    print(f"  Archetype: {cards['cards']['card_2_identity']['archetype']['type']}")
    print(f"  Record: {cards['cards']['card_2_identity']['timelines']['actual']['record']}")
    print(f"  Draft Grade: {cards['cards']['card_1_draft']['grade']}")
    print(f"  Lineup Efficiency: {cards['cards']['card_2_identity']['efficiency']['lineup_efficiency_pct']}%")
    print(f"\nThe One Thing to Fix: {cards['cards']['card_5_accounting']['the_one_thing']['factor']}")
    print(f"  {cards['cards']['card_5_accounting']['the_one_thing']['diagnosis']}")
    print(f"\nProjected Improvement: {cards['cards']['card_5_accounting']['projected_2026_record']['improvement']:+d} wins")
    print(f"  From {cards['cards']['card_2_identity']['timelines']['actual']['record']} → {cards['cards']['card_5_accounting']['projected_2026_record']['record']}")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
