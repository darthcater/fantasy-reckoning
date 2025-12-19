"""
Debug why waiver points are showing as 0
Show exactly what the code is looking for vs what exists
"""

import json

with open('league_908221_2025.json', 'r') as f:
    data = json.load(f)

dobbs_key = "461.l.908221.t.12"

print("=" * 100)
print("DEBUGGING WAIVER POINTS CALCULATION - Dobbs' Decision")
print("=" * 100)
print()

# Find waiver transactions for Dobbs
waiver_adds = []
for trans in data['transactions']:
    for player in trans.get('players', []):
        if player.get('destination_team_key') == dobbs_key:
            if player.get('source_type') == 'waivers':
                waiver_adds.append({
                    'trans_id': trans['transaction_id'],
                    'player_name': player.get('player_name', 'Unknown'),
                    'player_id': player.get('player_id'),
                    'player': player
                })

print(f"Found {len(waiver_adds)} waiver adds for Dobbs' Decision")
print()

if waiver_adds:
    # Show structure of first waiver add
    print("=" * 100)
    print("ACTUAL DATA STRUCTURE (Transaction #" + waiver_adds[0]['trans_id'] + " - " + waiver_adds[0]['player_name'] + ")")
    print("=" * 100)
    print()

    sample_player = waiver_adds[0]['player']

    print("What EXISTS in player object:")
    print(json.dumps(sample_player, indent=2))
    print()

    print("=" * 100)
    print("WHAT THE CODE IS LOOKING FOR (BUG)")
    print("=" * 100)
    print()

    print("Code looks for: player.get('transaction_data', {})")
    print(f"What it finds: {sample_player.get('transaction_data', 'DOES NOT EXIST')}")
    print()

    print("Code then checks: trans_data.get('type')")
    trans_data = sample_player.get('transaction_data', {})
    print(f"Value: {trans_data.get('type', 'NONE - Empty dict!')}")
    print()

    print("Code checks: trans_data.get('destination_team_key') == team_key")
    print(f"Value: {trans_data.get('destination_team_key', 'NONE - Empty dict!')}")
    print()

    print("=" * 100)
    print("WHAT THE CODE SHOULD BE LOOKING FOR (FIX)")
    print("=" * 100)
    print()

    print("Should look for: player.get('type')")
    print(f"Actual value: '{sample_player.get('type')}'")
    print()

    print("Should check: player.get('destination_team_key') == team_key")
    print(f"Actual value: '{sample_player.get('destination_team_key')}'")
    print(f"Matches Dobbs' key? {sample_player.get('destination_team_key') == dobbs_key}")
    print()

    print("Should check: player.get('source_type') == 'waivers'")
    print(f"Actual value: '{sample_player.get('source_type')}'")
    print()

print("=" * 100)
print("THE BUG")
print("=" * 100)
print()
print("❌ WRONG (current code):")
print("   trans_data = player.get('transaction_data', {})")
print("   if trans_data.get('type') == 'add':")
print()
print("   Result: transaction_data doesn't exist → empty dict → no matches → 0 points!")
print()
print("✅ CORRECT (should be):")
print("   if player.get('type') == 'add':")
print("   if player.get('destination_team_key') == team_key:")
print("   if player.get('source_type') in ['waivers', 'freeagents']:")
print()

print("=" * 100)
print("IMPACT")
print("=" * 100)
print()
print(f"Your 6 waiver adds: {[w['player_name'] for w in waiver_adds]}")
print()
print("Because of this bug:")
print("  - Code never finds ANY of your waiver adds")
print("  - Calculates 0 points added from waivers")
print("  - Shows rank 9/14 (middle of pack) instead of actual performance")
print("  - Same bug affects ALL 14 teams")
print()
print("This is why Jake also showed 0 waiver points despite 25 total moves!")
