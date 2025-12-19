"""Check waiver percentile rankings across all teams"""
import json
import glob

teams_data = []

for file_path in glob.glob('fantasy_wrapped_*.json'):
    with open(file_path) as f:
        data = json.load(f)
        manager = data['manager_name']

        # Skip if card data is missing
        if 'card_1_reckoning' not in data['cards']:
            print(f"Skipping {manager} - missing card_1_reckoning")
            continue

        card1 = data['cards']['card_1_reckoning']
        card2 = data['cards'].get('card_2_roster', {})

        waiver_pct = card1['dimension_breakdown']['waivers']['percentile']
        costly_drops = card2.get('costly_drops', {})

        teams_data.append({
            'manager': manager,
            'waiver_percentile': waiver_pct,
            'total_drops': costly_drops.get('total_drops', 0),
            'value_given_away': costly_drops.get('total_value_given_away', 0),
            'most_costly': costly_drops.get('most_costly_drop')
        })

# Sort by waiver percentile
teams_data.sort(key=lambda x: x['waiver_percentile'], reverse=True)

print("WAIVER PERCENTILE RANKINGS (with Costly Drops Impact)")
print("=" * 100)
print()

for i, team in enumerate(teams_data, 1):
    print(f"{i}. {team['manager']}")
    print(f"   Waiver Percentile: {team['waiver_percentile']:.1f}")
    print(f"   Total Drops: {team['total_drops']}")
    print(f"   Value Given Away: {team['value_given_away']:.1f} started pts")

    if team['most_costly']:
        mc = team['most_costly']
        print(f"   Most Costly: {mc['player_name']} ({mc['started_pts']:.1f} pts to {mc['picked_up_by']})")

    print()
