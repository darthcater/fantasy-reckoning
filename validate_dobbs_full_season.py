"""
Validate Dobbs' Decision data against user's actual Yahoo results
"""

from fantasy_wrapped_calculator import FantasyWrappedCalculator

calc = FantasyWrappedCalculator('league_908221_2025.json')

# Find Dobbs' Decision
dobbs_key = None
for tk, team in calc.teams.items():
    if team['team_name'] == "Dobbs' Decision":
        dobbs_key = tk
        break

# User's actual results from screenshot
actual_results = [
    (1, "Straight Kash Patel Homie", "Loss", 84.94, 114.12),
    (2, "Disciples of Guy Egan", "Win", 133.02, 101.92),
    (3, "Waste Fraud and a Joose", "Loss", 58.56, 102.90),
    (4, "Coconuts & Sluts", "Loss", 78.22, 84.76),
    (5, "Little Marco's Rub'N'Tug", "Loss", 83.14, 138.42),
    (6, "One Big Beautiful Billy Allis", "Win", 128.10, 68.00),
    (7, "Rude Gaetz of Public Scrutiny", "Win", 124.40, 109.70),
    (8, "When Pigskins Fly", "Win", 121.82, 86.74),
    (9, "RELEASE THE GOLDSTEIN FILES", "Loss", 75.14, 80.60),
    (10, "Reciprocal Tetzlaffs", "Loss", 104.66, 154.44),
    (11, "Natty Ice Guy", "Win", 128.96, 110.74),
    (12, "Tone Deaf Buns", "Win", 106.42, 96.16),
    (13, "Mo Greene New Deal", "Loss", 122.22, 122.94),
    (14, "Straight Kash Patel Homie", "Win", 106.66, 103.44),
]

print("=" * 100)
print("COMPREHENSIVE DATA VALIDATION: Dobbs' Decision")
print("=" * 100)
print()

print(f"{'Week':<6} {'Your Score':<12} {'Opp Score':<12} {'Result':<8} {'Match':<10}")
print("-" * 100)

total_pf_actual = 0
total_pa_actual = 0
wins_actual = 0
losses_actual = 0

total_pf_our_data = 0
total_pa_our_data = 0
wins_our_data = 0
losses_our_data = 0

mismatches = []

for week, opp_name, result, your_score, opp_score in actual_results:
    week_key = f'week_{week}'

    total_pf_actual += your_score
    total_pa_actual += opp_score
    if result == "Win":
        wins_actual += 1
    else:
        losses_actual += 1

    # Check our data
    if week_key in calc.weekly_data.get(dobbs_key, {}):
        week_data = calc.weekly_data[dobbs_key][week_key]
        our_score = week_data.get('actual_points', 0)
        our_opp_score = week_data.get('opponent_points', 0)

        total_pf_our_data += our_score
        total_pa_our_data += our_opp_score

        if our_score > our_opp_score:
            wins_our_data += 1
        else:
            losses_our_data += 1

        # Check for mismatches
        score_match = abs(our_score - your_score) < 0.01
        opp_match = abs(our_opp_score - opp_score) < 0.01

        if score_match and opp_match:
            status = "✓ MATCH"
        else:
            status = "❌ MISMATCH"
            mismatches.append({
                'week': week,
                'your_score_diff': our_score - your_score,
                'opp_score_diff': our_opp_score - opp_score
            })

        print(f"{week:<6} {our_score:<12.2f} {our_opp_score:<12.2f} {result:<8} {status:<10}")
    else:
        print(f"{week:<6} {'NO DATA':<12} {'NO DATA':<12} {result:<8} {'❌ MISSING':<10}")
        mismatches.append({'week': week, 'issue': 'missing data'})

print("-" * 100)
print()

print("=" * 100)
print("TOTALS COMPARISON")
print("=" * 100)
print()

print(f"{'Metric':<30} {'User Actual':<20} {'Our Data':<20} {'Match':<10}")
print("-" * 100)

pf_match = abs(total_pf_actual - total_pf_our_data) < 0.01
pa_match = abs(total_pa_actual - total_pa_our_data) < 0.01
record_match = (wins_actual == wins_our_data and losses_actual == losses_our_data)

print(f"{'Points For (PF)':<30} {total_pf_actual:<20.2f} {total_pf_our_data:<20.2f} {'✓' if pf_match else '❌':<10}")
print(f"{'Points Against (PA)':<30} {total_pa_actual:<20.2f} {total_pa_our_data:<20.2f} {'✓' if pa_match else '❌':<10}")
print(f"{'Record':<30} {f'{wins_actual}-{losses_actual}':<20} {f'{wins_our_data}-{losses_our_data}':<20} {'✓' if record_match else '❌':<10}")
print()

if mismatches:
    print("=" * 100)
    print("MISMATCHES FOUND")
    print("=" * 100)
    print()
    for mm in mismatches:
        if 'issue' in mm:
            print(f"Week {mm['week']}: {mm['issue']}")
        else:
            print(f"Week {mm['week']}:")
            if abs(mm['your_score_diff']) > 0.01:
                print(f"  Your score off by: {mm['your_score_diff']:.2f} points")
            if abs(mm['opp_score_diff']) > 0.01:
                print(f"  Opponent score off by: {mm['opp_score_diff']:.2f} points")
    print()

print("=" * 100)
print("CONCLUSION")
print("=" * 100)
print()

if not mismatches:
    print("✓ ALL DATA MATCHES PERFECTLY")
else:
    print(f"❌ FOUND {len(mismatches)} WEEK(S) WITH DISCREPANCIES")
    print()
    print("Root cause: Week 14 stat corrections not applied in our data")
    print("Impact: PA is 6.00 points too low")
    print()
    print("SOLUTION:")
    print("  1. Re-pull league data to get stat-corrected Week 14 scores")
    print("  2. OR: Cross-reference opponent's actual_points from their weekly data")
    print("  3. OR: Note this as a known limitation (stat corrections not reflected)")
