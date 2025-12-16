"""
Trade Impact Calculation - Working Implementation
Calculates ROS points for traded players with STARTED vs BENCH distinction
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


def calculate_trade_impact(team_key, transactions, weekly_data, teams_data):
    """
    Calculate trade impact for a team

    Returns:
        - Total trades count
        - Net impact (total ROS)
        - Net started impact (practical lineup impact)
        - Trade details list
    """
    # Get team's trades
    team_trades = []
    for t in transactions:
        if t.get('type') != 'trade':
            continue

        # Check if team is involved
        involved = any(p.get('destination_team_key') == team_key for p in t.get('players', []))
        if involved:
            team_trades.append(t)

    if not team_trades:
        return {
            'total_trades': 0,
            'net_total_impact': 0,
            'net_started_impact': 0,
            'trades': []
        }

    trade_details = []
    total_net_impact = 0
    total_started_impact = 0

    for trade in sorted(team_trades, key=lambda x: x['timestamp']):
        trade_date = datetime.fromtimestamp(trade['timestamp'])
        trade_week = get_week_from_timestamp(trade['timestamp'])

        # Parse acquired vs gave away
        acquired = [p for p in trade['players'] if p['destination_team_key'] == team_key]
        gave_away = [p for p in trade['players'] if p['destination_team_key'] != team_key]

        # Calculate ROS for acquired players
        acquired_total = 0
        acquired_started = 0
        acquired_details = []

        for player in acquired:
            player_id = player['player_id']
            total_pts = 0
            started_pts = 0
            weeks_as_starter = 0
            weeks_on_bench = 0

            for week in range(trade_week, 15):  # Through Week 14
                week_key = f'week_{week}'

                if week_key not in weekly_data.get(team_key, {}):
                    continue

                week_data = weekly_data[team_key][week_key]
                roster = week_data.get('roster', {})

                # Check if in starters
                for p in roster.get('starters', []):
                    if p.get('player_id') == player_id:
                        pts = float(p.get('actual_points', 0))
                        total_pts += pts
                        started_pts += pts
                        weeks_as_starter += 1
                        break

                # Check if on bench
                for p in roster.get('bench', []):
                    if p.get('player_id') == player_id:
                        pts = float(p.get('actual_points', 0))
                        total_pts += pts
                        weeks_on_bench += 1
                        break

            acquired_total += total_pts
            acquired_started += started_pts

            acquired_details.append({
                'player_name': player['player_name'],
                'position': player['position'],
                'total_ros': round(total_pts, 1),
                'started': round(started_pts, 1),
                'benched': round(total_pts - started_pts, 1),
                'weeks_as_starter': weeks_as_starter,
                'weeks_on_bench': weeks_on_bench,
                'utilization_pct': round((started_pts / total_pts * 100) if total_pts > 0 else 0, 1)
            })

        # Calculate ROS for gave away players (on their new team)
        gave_away_total = 0
        gave_away_started = 0
        gave_away_details = []

        for player in gave_away:
            dest_team = player['destination_team_key']
            player_id = player['player_id']
            total_pts = 0
            started_pts = 0
            weeks_as_starter = 0
            weeks_on_bench = 0

            for week in range(trade_week, 15):
                week_key = f'week_{week}'

                if week_key not in weekly_data.get(dest_team, {}):
                    continue

                week_data = weekly_data[dest_team][week_key]
                roster = week_data.get('roster', {})

                # Check starters
                for p in roster.get('starters', []):
                    if p.get('player_id') == player_id:
                        pts = float(p.get('actual_points', 0))
                        total_pts += pts
                        started_pts += pts
                        weeks_as_starter += 1
                        break

                # Check bench
                for p in roster.get('bench', []):
                    if p.get('player_id') == player_id:
                        pts = float(p.get('actual_points', 0))
                        total_pts += pts
                        weeks_on_bench += 1
                        break

            gave_away_total += total_pts
            gave_away_started += started_pts

            gave_away_details.append({
                'player_name': player['player_name'],
                'position': player['position'],
                'destination_team': player['destination_team_name'],
                'total_ros': round(total_pts, 1),
                'started': round(started_pts, 1),
                'benched': round(total_pts - started_pts, 1),
                'weeks_as_starter': weeks_as_starter,
                'weeks_on_bench': weeks_on_bench,
                'utilization_pct': round((started_pts / total_pts * 100) if total_pts > 0 else 0, 1)
            })

        # Calculate net impact
        net_total = round(acquired_total - gave_away_total, 1)
        net_started = round(acquired_started - gave_away_started, 1)

        total_net_impact += net_total
        total_started_impact += net_started

        trade_details.append({
            'trade_id': trade['transaction_id'],
            'trade_date': trade_date.strftime('%B %d, %Y'),
            'trade_week': trade_week,
            'acquired': acquired_details,
            'gave_away': gave_away_details,
            'net_total_impact': net_total,
            'net_started_impact': net_started,
            'verdict': get_trade_verdict(net_started)
        })

    return {
        'total_trades': len(team_trades),
        'net_total_impact': round(total_net_impact, 1),
        'net_started_impact': round(total_started_impact, 1),
        'trades': trade_details,
        'overall_verdict': get_overall_verdict(total_started_impact, len(team_trades))
    }


def get_trade_verdict(net_started):
    """Get verdict for single trade"""
    if abs(net_started) < 1:
        return "WASH"
    elif net_started > 10:
        return "BIG WIN"
    elif net_started > 0:
        return "MINOR WIN"
    elif net_started < -10:
        return "BIG LOSS"
    else:
        return "MINOR LOSS"


def get_overall_verdict(total_started_impact, trade_count):
    """Get overall trading verdict"""
    if trade_count == 0:
        return "No trades made"

    if total_started_impact > 20:
        return f"Elite trader - Added {total_started_impact:.1f} starting points"
    elif total_started_impact > 5:
        return f"Good trader - Added {total_started_impact:.1f} starting points"
    elif total_started_impact < -20:
        return f"Poor trader - Lost {abs(total_started_impact):.1f} starting points"
    elif total_started_impact < -5:
        return f"Below average trader - Lost {abs(total_started_impact):.1f} starting points"
    else:
        return "Neutral - Trades had minimal impact"


# Example usage
if __name__ == "__main__":
    with open('league_908221_2025.json') as f:
        data = json.load(f)

    team_key = '461.l.908221.t.12'  # Dobbs' Decision
    result = calculate_trade_impact(
        team_key,
        data['transactions'],
        data['weekly_data'],
        data['teams']
    )

    print("TRADE IMPACT SUMMARY")
    print("=" * 80)
    print(f"Total Trades: {result['total_trades']}")
    print(f"Net Total Impact: {result['net_total_impact']:+.1f} points")
    print(f"Net STARTED Impact: {result['net_started_impact']:+.1f} points ⭐")
    print(f"Verdict: {result['overall_verdict']}")
    print()

    for i, trade in enumerate(result['trades'], 1):
        print(f"Trade {i} - {trade['trade_date']} (Week {trade['trade_week']})")
        print(f"  Net Started Impact: {trade['net_started_impact']:+.1f} points")
        print(f"  Verdict: {trade['verdict']}")
