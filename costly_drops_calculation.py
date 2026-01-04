"""
Costly Drops Calculation
Tracks when dropped players were picked up by opponents and contributed points
"""

import json
from datetime import datetime


def get_week_from_timestamp(timestamp):
    """Convert timestamp to NFL week number"""
    trade_date = datetime.fromtimestamp(timestamp)
    week_1_start = datetime(2025, 9, 4)  # 2025 NFL season start
    days_since_week1 = (trade_date - week_1_start).days
    week = max(1, min(18, (days_since_week1 // 7) + 1))
    return week


def calculate_costly_drops(team_key, transactions, weekly_data, teams_data, last_regular_season_week=14):
    """
    Calculate costly drops - when you dropped players that helped opponents

    Since Yahoo API doesn't provide dropped player info in transactions,
    we infer drops from weekly roster changes:
    - Player on roster week N but not week N+1 = dropped in week N+1

    Returns:
        - Total value given away (started points)
        - Most costly drops
        - Details list
    """
    # Infer drops from weekly roster changes
    team_drops = []

    if team_key not in weekly_data:
        return {
            'total_drops': 0,
            'total_value_given_away': 0,
            'costly_drops': [],
            'most_costly_drop': None,
            'verdict': "No roster data"
        }

    # Track players on roster each week (regular season only)
    for week in range(1, last_regular_season_week + 1):
        week_key = f'week_{week}'
        next_week_key = f'week_{week + 1}'

        if week_key not in weekly_data[team_key] or next_week_key not in weekly_data[team_key]:
            continue

        # Get all players on roster this week
        current_roster = weekly_data[team_key][week_key].get('roster', {})
        current_players = set()
        player_info = {}  # Store player names and positions

        for player in current_roster.get('starters', []) + current_roster.get('bench', []):
            pid = str(player.get('player_id'))
            current_players.add(pid)
            player_info[pid] = {
                'name': player.get('player_name', 'Unknown'),
                'position': player.get('position', 'Unknown')
            }

        # Get all players on roster next week
        next_roster = weekly_data[team_key][next_week_key].get('roster', {})
        next_players = set()

        for player in next_roster.get('starters', []) + next_roster.get('bench', []):
            pid = str(player.get('player_id'))
            next_players.add(pid)

        # Players in current but not in next = dropped
        dropped_players = current_players - next_players

        for pid in dropped_players:
            # Check if player was traded (not dropped)
            # For trades, a player leaving team_key will have destination_team_key != team_key
            was_traded = False
            for t in transactions:
                if t.get('type') == 'trade':
                    for p in t.get('players', []):
                        # If player is in trade and their destination is NOT our team, they were traded away
                        if str(p.get('player_id')) == pid and p.get('destination_team_key') != team_key:
                            # Need to verify this player was actually on our team before
                            # by checking if another player in same trade came TO our team
                            trade_involves_our_team = any(
                                tp.get('destination_team_key') == team_key
                                for tp in t.get('players', [])
                            )
                            if trade_involves_our_team:
                                was_traded = True
                                break

            if not was_traded and pid in player_info:
                team_drops.append({
                    'player_id': pid,
                    'player_name': player_info[pid]['name'],
                    'position': player_info[pid]['position'],
                    'drop_week': week + 1,
                    'drop_timestamp': None  # We don't have exact timestamp
                })

    if not team_drops:
        return {
            'total_drops': 0,
            'total_value_given_away': 0,
            'costly_drops': [],
            'most_costly_drop': None,
            'verdict': "No drops made"
        }

    costly_drops_details = []
    total_value_given = 0

    # For each dropped player, find if they were picked up and how they performed
    for drop_info in team_drops:
        player_id = drop_info['player_id']
        drop_week = drop_info['drop_week']

        # Find if another team picked up this player after the drop week
        # Check weekly rosters of all other teams starting from drop_week
        picked_up_by = None
        pickup_week = None

        for other_team_key in weekly_data.keys():
            if other_team_key == team_key:
                continue

            # Check weeks starting from drop_week (regular season only)
            for week in range(drop_week, last_regular_season_week + 1):
                week_key = f'week_{week}'

                if week_key not in weekly_data[other_team_key]:
                    continue

                roster = weekly_data[other_team_key][week_key].get('roster', {})
                all_players = roster.get('starters', []) + roster.get('bench', [])

                for p in all_players:
                    if str(p.get('player_id')) == str(player_id):
                        picked_up_by = other_team_key
                        pickup_week = week
                        break

                if picked_up_by:
                    break

            if picked_up_by:
                break

        # If player wasn't picked up by another team, skip
        if not picked_up_by:
            continue

        # Calculate how player performed for new team (started points only)
        total_pts = 0
        started_pts = 0
        weeks_as_starter = 0
        weeks_on_bench = 0

        for week in range(pickup_week, last_regular_season_week + 1):  # From pickup through end of regular season
            week_key = f'week_{week}'

            if week_key not in weekly_data.get(picked_up_by, {}):
                continue

            week_data = weekly_data[picked_up_by][week_key]
            roster = week_data.get('roster', {})

            # Check if in starters
            for p in roster.get('starters', []):
                if str(p.get('player_id')) == str(player_id):
                    pts = float(p.get('actual_points', 0))
                    total_pts += pts
                    started_pts += pts
                    weeks_as_starter += 1
                    break

            # Check if on bench
            for p in roster.get('bench', []):
                if str(p.get('player_id')) == str(player_id):
                    pts = float(p.get('actual_points', 0))
                    total_pts += pts
                    weeks_on_bench += 1
                    break

        # Only count as "costly" if player scored meaningful started points
        if started_pts >= 5:  # Threshold: at least 5 started points
            total_value_given += started_pts

            # Get team name of team that picked up player
            picked_up_team_name = 'Unknown'
            if isinstance(teams_data, dict):
                # teams_data is a dict with team_key as keys
                picked_up_team_name = teams_data.get(picked_up_by, {}).get('team_name', 'Unknown')
            else:
                # teams_data is a list
                for team in teams_data:
                    if team.get('team_key') == picked_up_by:
                        picked_up_team_name = team.get('team_name', 'Unknown')
                        break

            costly_drops_details.append({
                'player_name': drop_info['player_name'],
                'position': drop_info['position'],
                'drop_week': drop_week,
                'picked_up_by': picked_up_team_name,
                'pickup_week': pickup_week,
                'total_ros': round(total_pts, 1),
                'started_pts': round(started_pts, 1),
                'benched_pts': round(total_pts - started_pts, 1),
                'weeks_as_starter': weeks_as_starter,
                'weeks_on_bench': weeks_on_bench
            })

    # Sort by started points (most costly first)
    costly_drops_details.sort(key=lambda x: x['started_pts'], reverse=True)

    return {
        'total_drops': len(team_drops),
        'total_value_given_away': round(total_value_given, 1),
        'costly_drops': costly_drops_details,
        'most_costly_drop': costly_drops_details[0] if costly_drops_details else None,
        'verdict': get_drops_verdict(total_value_given, len(costly_drops_details))
    }


def get_drops_verdict(total_value, costly_count):
    """Get verdict for costly drops"""
    if costly_count == 0:
        return "No costly drops"
    elif total_value > 100:
        return f"MASSIVE BLUNDER - Gave away {total_value:.0f} started pts to opponents"
    elif total_value > 50:
        return f"Poor management - Gave away {total_value:.0f} started pts"
    elif total_value > 20:
        return f"Questionable drops - {total_value:.0f} started pts to opponents"
    else:
        return f"Minor impact - {total_value:.0f} started pts given away"


# Example usage
if __name__ == "__main__":
    with open('league_908221_2025.json') as f:
        data = json.load(f)

    team_key = '461.l.908221.t.12'  # max
    result = calculate_costly_drops(
        team_key,
        data['transactions'],
        data['weekly_data'],
        data['teams']
    )

    print("COSTLY DROPS ANALYSIS")
    print("=" * 80)
    print(f"Total Drops: {result['total_drops']}")
    print(f"Total Value Given Away: {result['total_value_given_away']:.1f} started pts")
    print(f"Verdict: {result['verdict']}")
    print()

    if result['most_costly_drop']:
        print("Most Costly Drop:")
        drop = result['most_costly_drop']
        print(f"  {drop['player_name']} ({drop['position']})")
        print(f"  Dropped Week {drop['drop_week']}, picked up by {drop['picked_up_by']} Week {drop['pickup_week']}")
        print(f"  Scored {drop['started_pts']:.1f} started pts ({drop['weeks_as_starter']} weeks)")

    print("\nAll Costly Drops:")
    for drop in result['costly_drops']:
        print(f"  {drop['player_name']}: {drop['started_pts']:.1f} started pts for {drop['picked_up_by']}")
