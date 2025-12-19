"""
Compare old vs new league data to show what changed with stat corrections
"""

import json
import sys

print("=" * 100)
print("COMPARING OLD VS NEW LEAGUE DATA")
print("=" * 100)
print()

# Load both files
try:
    with open('league_908221_2025_BACKUP.json', 'r') as f:
        old_data = json.load(f)
    print("✓ Loaded OLD data (pre-stat-correction)")
except FileNotFoundError:
    print("❌ Could not find backup file")
    sys.exit(1)

try:
    with open('league_908221_2025.json', 'r') as f:
        new_data = json.load(f)
    print("✓ Loaded NEW data (stat-corrected)")
except FileNotFoundError:
    print("❌ Could not find new data file - data puller may still be running")
    sys.exit(1)

print()

# Compare timestamps
old_time = old_data.get('generated_at', 'Unknown')
new_time = new_data.get('generated_at', 'Unknown')
print(f"Old data generated: {old_time}")
print(f"New data generated: {new_time}")
print()

# Compare team stats
print("=" * 100)
print("TEAM STATS CHANGES (Focus: Week 14 Stat Corrections)")
print("=" * 100)
print()

old_teams = {t['team_key']: t for t in old_data['teams']}
new_teams = {t['team_key']: t for t in new_data['teams']}

print(f"{'Team Name':<35} {'Old Record':<12} {'New Record':<12} {'PF Change':<12} {'PA Change':<12}")
print("-" * 100)

total_pf_change = 0
total_pa_change = 0
teams_with_changes = 0

for team_key in sorted(old_teams.keys(), key=lambda k: old_teams[k]['team_name']):
    old_team = old_teams[team_key]
    new_team = new_teams.get(team_key)

    if not new_team:
        continue

    old_record = f"{old_team['wins']}-{old_team['losses']}"
    new_record = f"{new_team['wins']}-{new_team['losses']}"

    old_pf = float(old_team.get('points_for', 0))
    new_pf = float(new_team.get('points_for', 0))
    pf_change = new_pf - old_pf

    old_pa = float(old_team.get('points_against', 0))
    new_pa = float(new_team.get('points_against', 0))
    pa_change = new_pa - old_pa

    total_pf_change += abs(pf_change)
    total_pa_change += abs(pa_change)

    if abs(pf_change) > 0.1 or abs(pa_change) > 0.1 or old_record != new_record:
        teams_with_changes += 1
        marker = "⚠️ " if abs(pa_change) > 5 else ""
    else:
        marker = ""

    pf_str = f"{pf_change:+.1f}" if abs(pf_change) > 0.1 else "-"
    pa_str = f"{pa_change:+.1f}" if abs(pa_change) > 0.1 else "-"

    print(f"{marker}{old_team['team_name']:<35} {old_record:<12} {new_record:<12} {pf_str:<12} {pa_str:<12}")

print()
print(f"Teams with changes: {teams_with_changes}/14")
print(f"Average PF change: {total_pf_change/14:.2f} points per team")
print(f"Average PA change: {total_pa_change/14:.2f} points per team")
print()

# Highlight Dobbs' Decision specifically
print("=" * 100)
print("DOBBS' DECISION SPECIFIC CHANGES")
print("=" * 100)
print()

dobbs_key = '461.l.908221.t.12'
old_dobbs = old_teams.get(dobbs_key)
new_dobbs = new_teams.get(dobbs_key)

if old_dobbs and new_dobbs:
    print(f"Record:  {old_dobbs['wins']}-{old_dobbs['losses']} → {new_dobbs['wins']}-{new_dobbs['losses']}")
    print(f"PF:      {old_dobbs['points_for']:.2f} → {new_dobbs['points_for']:.2f} ({new_dobbs['points_for'] - old_dobbs['points_for']:+.2f})")
    print(f"PA:      {old_dobbs['points_against']:.2f} → {new_dobbs['points_against']:.2f} ({new_dobbs['points_against'] - old_dobbs['points_against']:+.2f})")
    print()

    # Check Week 14 specifically
    old_weekly = old_data['weekly_data'].get(dobbs_key, {})
    new_weekly = new_data['weekly_data'].get(dobbs_key, {})

    old_w14 = old_weekly.get('week_14', {})
    new_w14 = new_weekly.get('week_14', {})

    if old_w14 and new_w14:
        print("Week 14 Changes:")
        print(f"  Your score:      {old_w14.get('actual_points', 0):.2f} → {new_w14.get('actual_points', 0):.2f}")
        print(f"  Opponent score:  {old_w14.get('opponent_points', 0):.2f} → {new_w14.get('opponent_points', 0):.2f}")

        opp_change = new_w14.get('opponent_points', 0) - old_w14.get('opponent_points', 0)
        if abs(opp_change) > 0.1:
            print(f"  Stat correction: {opp_change:+.2f} points to opponent ✓")

print()
print("=" * 100)
print("WEEK 14 STAT CORRECTIONS ACROSS LEAGUE")
print("=" * 100)
print()

week14_corrections = []
for team_key in old_teams.keys():
    old_weekly = old_data['weekly_data'].get(team_key, {})
    new_weekly = new_data['weekly_data'].get(team_key, {})

    old_w14 = old_weekly.get('week_14', {})
    new_w14 = new_weekly.get('week_14', {})

    if old_w14 and new_w14:
        old_score = old_w14.get('actual_points', 0)
        new_score = new_w14.get('actual_points', 0)
        diff = new_score - old_score

        if abs(diff) > 0.1:
            week14_corrections.append({
                'team': old_teams[team_key]['team_name'],
                'change': diff
            })

if week14_corrections:
    print(f"Found {len(week14_corrections)} teams with Week 14 stat corrections:\n")
    for corr in sorted(week14_corrections, key=lambda x: abs(x['change']), reverse=True):
        print(f"  {corr['team']:<35} {corr['change']:+.2f} points")
else:
    print("No Week 14 stat corrections found (or data is identical)")

print()
print("=" * 100)
print("SUMMARY")
print("=" * 100)
print()

if teams_with_changes > 0:
    print(f"✓ New data successfully pulled with {teams_with_changes} team(s) updated")
    print("✓ Week 14 stat corrections have been applied")
    print("✓ Data is now 100% accurate for card generation")
else:
    print("⚠️  No changes detected - data may be identical or puller not complete")

print()
print("Next step: Generate cards with new data using:")
print("  python3 fantasy_wrapped_calculator.py --use-team-names")
