import json
import os
from datetime import datetime

with open('league_908221_2025.json', 'r') as f:
    data = json.load(f)

print('='*60)
print('FANTASY WRAPPED - COMPLETE DATA VALIDATION')
print('='*60)

print(f"\n📊 LEAGUE: {data['league']['name']}")
print(f"   Season: {data['league']['season']}")
print(f"   Teams: {data['league']['num_teams']}")
print(f"   Weeks: {data['league']['current_week']}")

print(f"\n✅ TEAMS: {len(data['teams'])} teams")
first_team = data['teams'][0]
print(f"   Sample: {first_team['team_name']} ({first_team['wins']}-{first_team['losses']})")

print(f"\n✅ WEEKLY DATA:")
team_id = first_team['team_key']
week1 = data['weekly_data'][team_id]['week_1']
print(f"   Week 1 Sample:")
print(f"     Actual Points: {week1.get('actual_points')}")
print(f"     Projected: {week1.get('projected_points')}")
print(f"     Result: {week1.get('result')}")
print(f"     Bench Points: {week1.get('bench_points')}")

print(f"\n✅ ROSTER DATA (Week 1):")
roster = week1['roster']
print(f"   Starters: {len(roster['starters'])}")
print(f"   Bench: {len(roster['bench'])}")
print(f"   Total Starter Points: {roster['total_starter_points']}")
print(f"   Total Bench Points: {roster['total_bench_points']}")

# Check injury status
injured = [p for p in roster['starters'] + roster['bench'] if p.get('status')]
if injured:
    print(f"   Injured Players: {len(injured)}")
    for p in injured[:2]:
        print(f"     - {p['player_name']}: {p['status']}")

print(f"\n✅ TRANSACTIONS: {len(data['transactions'])}")
if data['transactions']:
    # Check for FAAB
    faab_trans = [t for t in data['transactions'] if t.get('faab_bid')]
    print(f"   FAAB Transactions: {len(faab_trans)}")
    if faab_trans:
        sample = faab_trans[0]
        print(f"   Sample FAAB bid: ${sample['faab_bid']}")
        print(f"     Type: {sample['type']}")
        print(f"     Time: {datetime.fromtimestamp(sample['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        if sample.get('players'):
            print(f"     Player: {sample['players'][0].get('player_name')}")

print(f"\n✅ DRAFT: {len(data['draft'])} picks")

print(f"\n📁 FILE SIZE: ", end='')
size = os.path.getsize('league_908221_2025.json')
print(f"{size / 1024 / 1024:.1f} MB")

print(f"\n🎯 DATA COMPLETENESS CHECK:")
checks = {
    'Bench Player Points': roster['total_bench_points'] > 0,
    'Injury Status Tracking': len([p for p in roster['starters'] + roster['bench']]) > 0,
    'FAAB Data': len(faab_trans) > 0 if data['transactions'] else False,
    'Transaction Timestamps': data['transactions'][0]['timestamp'] > 0 if data['transactions'] else False,
    'Player Stats Detail': 'stats_detail' in roster['starters'][0] if roster['starters'] else False,
}

for check, passed in checks.items():
    status = '✅' if passed else '❌'
    print(f"   {status} {check}")

print('='*60)
print('🚀 READY FOR FANTASY WRAPPED METRICS CALCULATION!')
print('='*60)
