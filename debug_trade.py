"""Debug trade calculation for McMillan/Hubbard trade"""
import json
from fantasy_wrapped_calculator import FantasyWrappedCalculator

# Load calculator
calc = FantasyWrappedCalculator('league_908221_2025.json')

team_key = '461.l.908221.t.12'  # max

# Find the Hubbard/McMillan trade
print("=== FINDING TRADE ===")
for t in calc.transactions:
    if t.get('type') == 'trade':
        players = [p['player_name'] for p in t['players']]
        if 'Chuba Hubbard' in players or 'Tetairoa McMillan' in players:
            print(f"\nTrade ID: {t['transaction_id']}")
            print(f"Date: {t['timestamp']}")
            for p in t['players']:
                print(f"  {p['player_name']} (ID: {p['player_id']}, type: {type(p['player_id'])}) -> {p.get('destination_team_name', 'unknown')}")

            # Check what weeks we have data for
            print("\n=== CHECKING WEEKLY DATA ===")
            mcmillan_id = None
            hubbard_id = None
            for p in t['players']:
                if 'McMillan' in p['player_name']:
                    mcmillan_id = p['player_id']
                if 'Hubbard' in p['player_name']:
                    hubbard_id = p['player_id']
                    hubbard_dest = p['destination_team_key']

            print(f"\nLooking for McMillan (ID: {mcmillan_id}, type: {type(mcmillan_id)}) on max's team:")
            for week in range(5, 15):
                week_key = f'week_{week}'
                if week_key in calc.weekly_data.get(team_key, {}):
                    roster = calc.weekly_data[team_key][week_key].get('roster', {})

                    # Check all starters
                    for p in roster.get('starters', []):
                        pid = p.get('player_id')
                        if str(pid) == str(mcmillan_id):
                            print(f"  Week {week} STARTER: {p['player_name']} (ID: {pid}, type: {type(pid)}) - {p.get('actual_points', 0)} pts")

                    # Check all bench
                    for p in roster.get('bench', []):
                        pid = p.get('player_id')
                        if str(pid) == str(mcmillan_id):
                            print(f"  Week {week} BENCH: {p['player_name']} (ID: {pid}, type: {type(pid)}) - {p.get('actual_points', 0)} pts")

            print(f"\nLooking for Hubbard (ID: {hubbard_id}, type: {type(hubbard_id)}) on {hubbard_dest}:")
            if hubbard_dest in calc.weekly_data:
                for week in range(5, 15):
                    week_key = f'week_{week}'
                    if week_key in calc.weekly_data.get(hubbard_dest, {}):
                        roster = calc.weekly_data[hubbard_dest][week_key].get('roster', {})

                        # Check all starters
                        for p in roster.get('starters', []):
                            pid = p.get('player_id')
                            if str(pid) == str(hubbard_id):
                                print(f"  Week {week} STARTER: {p['player_name']} (ID: {pid}, type: {type(pid)}) - {p.get('actual_points', 0)} pts")

                        # Check all bench
                        for p in roster.get('bench', []):
                            pid = p.get('player_id')
                            if str(pid) == str(hubbard_id):
                                print(f"  Week {week} BENCH: {p['player_name']} (ID: {pid}, type: {type(pid)}) - {p.get('actual_points', 0)} pts")
