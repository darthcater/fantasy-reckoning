"""
Find all waiver transactions for Dobbs' Decision
User says 7, we found 6 - find the missing one
"""

import json

with open('league_908221_2025.json', 'r') as f:
    data = json.load(f)

dobbs_key = "461.l.908221.t.12"

print("=" * 80)
print("WAIVER TRANSACTION AUDIT: Dobbs' Decision")
print("=" * 80)
print()

waiver_adds = []
fa_adds = []

for trans in data['transactions']:
    trans_id = trans.get('transaction_id')
    trans_timestamp = trans.get('timestamp')

    for player in trans.get('players', []):
        dest_team = player.get('destination_team_key')

        if dest_team == dobbs_key:
            player_type = player.get('type')
            source_type = player.get('source_type')
            player_name = player.get('player_name', f"Player {player.get('player_id')}")
            position = player.get('position', '?')

            if player_type == 'add':
                if source_type == 'waivers':
                    waiver_adds.append({
                        'id': trans_id,
                        'timestamp': trans_timestamp,
                        'player': player_name,
                        'position': position
                    })
                elif source_type == 'freeagents':
                    fa_adds.append({
                        'id': trans_id,
                        'timestamp': trans_timestamp,
                        'player': player_name,
                        'position': position
                    })

print(f"WAIVER WIRE ADDS (source_type='waivers'): {len(waiver_adds)}")
print("-" * 80)
for i, trans in enumerate(sorted(waiver_adds, key=lambda x: x['timestamp']), 1):
    print(f"{i}. Trans #{trans['id']:3s} | {trans['player']:30s} ({trans['position']})")
print()

print(f"FREE AGENT ADDS (source_type='freeagents'): {len(fa_adds)}")
print("-" * 80)
for i, trans in enumerate(sorted(fa_adds, key=lambda x: x['timestamp']), 1):
    print(f"{i}. Trans #{trans['id']:3s} | {trans['player']:30s} ({trans['position']})")
print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"User says: 7 waiver adds, 20 total moves")
print(f"We found:  {len(waiver_adds)} waiver adds, {len(waiver_adds) + len(fa_adds)} total adds")
print()

if len(waiver_adds) < 7:
    print(f"⚠️  MISSING {7 - len(waiver_adds)} WAIVER TRANSACTION(S)")
    print()
    print("Possible reasons:")
    print("  1. Transaction data was pulled before a recent waiver claim processed")
    print("  2. A waiver add was miscategorized as 'freeagents' instead of 'waivers'")
    print("  3. A trade involved a player from waivers (would show as trade, not add)")
    print()
    print("Let me check if any FA adds should actually be waiver adds...")
    print()
    print("SUSPICIOUS FREE AGENT ADDS (might be miscategorized waivers):")
    print("  → Check if any of these cost FAAB:")
    for trans in sorted(fa_adds, key=lambda x: x['timestamp']):
        print(f"     Trans #{trans['id']} - {trans['player']}")
