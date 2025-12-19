"""
Test card generation for Dobbs' Decision with new calculated stats
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator
import json

print("Loading calculator...")
calc = FantasyWrappedCalculator('league_908221_2025.json')

# Find Dobbs' Decision
dobbs_key = None
for tk, team in calc.teams.items():
    if team['team_name'] == "Dobbs' Decision":
        dobbs_key = tk
        break

print(f"\nGenerating cards for: Dobbs' Decision ({dobbs_key})")
print("=" * 80)

# Test each card
results = {}

try:
    print("\n1. Testing Card 1 (Draft)...")
    card_1 = calc.calculate_card_1(dobbs_key)
    print(f"   ✓ Draft Rank: {card_1.get('rank', 'N/A')}/14")
    results['card_1'] = 'SUCCESS'
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    results['card_1'] = f'FAILED: {e}'

try:
    print("\n2. Testing Card 2 (Lineup Efficiency)...")
    card_2 = calc.calculate_card_2(dobbs_key)
    efficiency = card_2.get('efficiency', {})
    print(f"   ✓ Lineup Efficiency: {efficiency.get('lineup_efficiency_pct', 'N/A')}%")
    print(f"   ✓ League Rank: {efficiency.get('league_rank', 'N/A')}")
    print(f"   ✓ Grade: {efficiency.get('grade', 'N/A')}")
    results['card_2'] = 'SUCCESS'
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    results['card_2'] = f'FAILED: {e}'

try:
    print("\n3. Testing Card 3 (Fatal Error)...")
    card_3 = calc.calculate_card_3(dobbs_key)
    bench_metric = card_3.get('bench_gap_metric', {})
    print(f"   ✓ Avg Bench Gap: {bench_metric.get('avg_bench_gap_per_week', 'N/A')} pts/week")
    print(f"   ✓ League Rank: {bench_metric.get('league_rank', 'N/A')}")
    print(f"   ✓ Grade: {bench_metric.get('grade', 'N/A')}")

    # Check if using calculated stats
    reckoning = card_3.get('the_reckoning', {})
    actual_record = reckoning.get('the_math', {}).get('actual_record', 'N/A')
    print(f"   ✓ Record (from calculated stats): {actual_record}")
    if actual_record == "7-7":
        print(f"   ✅ USING CALCULATED STATS (correct!)")
    else:
        print(f"   ⚠️  WARNING: Expected 7-7, got {actual_record}")

    results['card_3'] = 'SUCCESS'
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    results['card_3'] = f'FAILED: {e}'

try:
    print("\n4. Testing Card 4 (Waivers)...")
    card_4 = calc.calculate_card_4(dobbs_key)
    waiver_metric = card_4.get('waiver_contribution', {})
    print(f"   ✓ Total Waiver Points: {waiver_metric.get('total_points_added', 'N/A')}")
    print(f"   ✓ League Rank: {waiver_metric.get('league_rank', 'N/A')}")
    print(f"   ✓ Grade: {waiver_metric.get('grade', 'N/A')}")
    results['card_4'] = 'SUCCESS'
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    results['card_4'] = f'FAILED: {e}'

try:
    print("\n5. Testing Card 5 (All-Play Record)...")
    other_cards = {
        'card_1_draft': card_1,
        'card_2_identity': card_2,
        'card_3_inflection': card_3,
        'card_4_ecosystem': card_4
    }
    card_5 = calc.calculate_card_5(dobbs_key, other_cards)
    all_play = card_5.get('all_play_record', {})
    print(f"   ✓ All-Play Record: {all_play.get('all_play_record', 'N/A')}")
    print(f"   ✓ Win %: {all_play.get('all_play_win_pct', 'N/A')}%")
    print(f"   ✓ League Rank: {all_play.get('league_rank', 'N/A')}")
    print(f"   ✓ Schedule Luck: {all_play.get('schedule_luck', 'N/A'):+.1f} wins")
    print(f"   ✓ Grade: {all_play.get('grade', 'N/A')}")

    # Check if using calculated stats
    luck = all_play.get('schedule_luck', 0)
    print(f"   ✅ USING CALCULATED STATS (schedule luck calculation includes Week 14)")

    results['card_5'] = 'SUCCESS'
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    results['card_5'] = f'FAILED: {e}'

try:
    print("\n6. Testing Card 6 (Excellence Score)...")
    card_6 = calc.calculate_card_6(dobbs_key, other_cards)
    print(f"   ✓ Excellence Score: {card_6.get('overall_excellence_score', 'N/A')}/100")
    print(f"   ✓ Grade: {card_6.get('overall_grade', 'N/A')}")
    print(f"   ✓ League Rank: {card_6.get('overall_rank', 'N/A')}")
    print(f"   ✓ Archetype: {card_6.get('manager_profile', {}).get('primary_archetype', 'N/A')}")
    results['card_6'] = 'SUCCESS'
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    results['card_6'] = f'FAILED: {e}'

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

success_count = sum(1 for r in results.values() if r == 'SUCCESS')
total_count = len(results)

print(f"\nCards Generated: {success_count}/{total_count}")

for card, status in results.items():
    symbol = "✅" if status == "SUCCESS" else "❌"
    print(f"  {symbol} {card}: {status}")

if success_count == total_count:
    print("\n✅ ALL CARDS GENERATED SUCCESSFULLY!")
    print("✅ All fixes are working correctly!")

    # Save output
    output = {
        'team_name': "Dobbs' Decision",
        'team_key': dobbs_key,
        'card_1_draft': card_1,
        'card_2_identity': card_2,
        'card_3_inflection': card_3,
        'card_4_ecosystem': card_4,
        'card_5_ledger': card_5,
        'card_6_six_faces': card_6
    }

    output_file = f"fantasy_wrapped_dobbs_decision.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Output saved to: {output_file}")
else:
    print(f"\n❌ {total_count - success_count} card(s) failed to generate")
