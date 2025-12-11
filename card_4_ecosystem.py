"""
Card 4: The Forsaken
Track drops that became weapons and lost FAAB bids that helped rivals
"""

from datetime import datetime
from collections import defaultdict

def calculate_card_4_ecosystem(calc, team_key: str) -> dict:
    """
    Calculate Card 4: The Forsaken metrics

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with ecosystem analysis
    """
    team = calc.teams[team_key]
    current_week = calc.league['current_week']

    # Track players this manager dropped
    dropped_players = []

    # Track FAAB bids this manager lost
    lost_bids = []

    # Calculate NFL season start (Week 1 typically starts first Thursday of September)
    # For 2025 season, Week 1 started around September 4, 2025
    season_year = calc.league.get('season', 2025)
    season_start = datetime(season_year, 9, 4)  # Approximate Week 1 start

    # Track all transactions chronologically
    for trans in calc.transactions:
        trans_type = trans.get('type', '')
        timestamp = trans.get('timestamp', 0)

        # Parse timestamp to get week
        try:
            trans_date = datetime.fromtimestamp(timestamp)
            # Calculate week number: days since season start / 7, plus 1
            days_since_start = (trans_date - season_start).days
            trans_week = max(1, min(current_week, (days_since_start // 7) + 1))
        except:
            trans_week = 1

        # Check for drops by this manager
        for player in trans.get('players', []):
            if not isinstance(player, dict):
                continue

            player_id = str(player.get('player_id', ''))
            trans_data = player.get('transaction_data', {})

            # Check if this manager dropped this player
            if trans_data.get('type') == 'drop' and trans_data.get('source_team_key') == team_key:
                # Track the drop
                dropped_players.append({
                    'player_id': player_id,
                    'drop_week': trans_week,
                    'timestamp': timestamp
                })

            # Check if this was an add by another team (could be a pickup of our drop or a lost bid)
            if trans_data.get('type') == 'add' and trans_data.get('destination_team_key') != team_key:
                acquiring_team = trans_data.get('destination_team_key')
                faab_bid = trans_data.get('faab_bid', 0)

                # Check if we dropped this player earlier
                was_our_drop = any(
                    d['player_id'] == player_id and d['timestamp'] < timestamp
                    for d in dropped_players
                )

                if was_our_drop:
                    # Calculate ROS points this player scored for the acquiring team
                    ros_points = calc.get_ros_points(player_id, trans_week)

                    # Find the drop record
                    for drop in dropped_players:
                        if drop['player_id'] == player_id and drop['timestamp'] < timestamp:
                            drop['acquired_by'] = acquiring_team
                            drop['acquired_by_name'] = calc.teams.get(acquiring_team, {}).get('manager_name', 'Unknown')
                            drop['ros_points'] = ros_points
                            drop['faab_cost_to_acquire'] = faab_bid
                            break

    # Calculate impact of drops
    drops_that_hurt = []
    for drop in dropped_players:
        if drop.get('ros_points', 0) > 0:
            drops_that_hurt.append({
                'player_id': drop['player_id'],
                'drop_week': drop['drop_week'],
                'acquired_by': drop.get('acquired_by_name', 'Waiver wire'),
                'ros_points': round(drop.get('ros_points', 0), 1),
                'faab_cost': drop.get('faab_cost_to_acquire', 0)
            })

    # Sort by ROS points (highest impact first)
    drops_that_hurt.sort(key=lambda x: x['ros_points'], reverse=True)

    # Find optimal FA pickups this manager could have made
    optimal_fa_by_week = []

    for week in range(1, min(current_week + 1, 5)):  # Sample first 5 weeks
        week_key = f'week_{week}'

        # Get available FAs at this week
        available_fas = calc.get_available_fas(week)

        if available_fas:
            # Get top 3 FAs by ROS points
            top_fas = available_fas[:3]

            optimal_fa_by_week.append({
                'week': week,
                'top_available': [
                    {
                        'player_id': fa[0],
                        'ros_points': round(fa[1], 1)
                    }
                    for fa in top_fas
                ]
            })

    # Calculate total opportunity cost
    total_drop_impact = sum(d['ros_points'] for d in drops_that_hurt)

    # Find worst drops (top 5)
    worst_drops = drops_that_hurt[:5]

    # Simulate optimal FA strategy
    # If they had picked up the top FA each week instead of their actual pickups
    actual_waiver_points = 0
    optimal_waiver_points = 0

    for week in range(1, current_week + 1):
        # Get best available FA
        available_fas = calc.get_available_fas(week)
        if available_fas:
            optimal_waiver_points += available_fas[0][1]  # Top FA's ROS points

    # Get actual waiver points from Card 2 calculation
    card_2 = calc.calculate_card_2(team_key)
    actual_waiver_points = card_2.get('insights', {}).get('waiver_points_acquired', 0)

    waiver_opportunity_cost = optimal_waiver_points - actual_waiver_points

    return {
        'manager_name': team['manager_name'],
        'drops_analysis': {
            'total_drops': len(dropped_players),
            'drops_that_hurt': len(drops_that_hurt),
            'total_ros_points_given_away': round(total_drop_impact, 1),
            'worst_drops': worst_drops
        },
        'lost_bids_analysis': {
            'note': 'FAAB bid tracking requires detailed transaction data',
            'lost_bids_count': len(lost_bids),
            'estimated_impact': 'Low'  # Placeholder
        },
        'optimal_fa_analysis': {
            'actual_waiver_points': round(actual_waiver_points, 1),
            'optimal_waiver_points': round(optimal_waiver_points, 1),
            'opportunity_cost': round(waiver_opportunity_cost, 1),
            'efficiency_pct': round((actual_waiver_points / optimal_waiver_points * 100), 1) if optimal_waiver_points > 0 else 0,
            'sample_weeks': optimal_fa_by_week[:3]  # Show first 3 weeks
        },
        'ecosystem_impact': {
            'players_given_to_rivals': len([d for d in drops_that_hurt if d.get('acquired_by') != 'Waiver wire']),
            'points_given_to_rivals': round(sum(d['ros_points'] for d in drops_that_hurt if d.get('acquired_by') != 'Waiver wire'), 1),
            'biggest_mistake': worst_drops[0] if worst_drops else None
        },
        'insights': {
            'total_opportunity_cost': round(total_drop_impact + waiver_opportunity_cost, 1),
            'avg_opportunity_cost_per_week': round((total_drop_impact + waiver_opportunity_cost) / current_week, 1) if current_week > 0 else 0
        }
    }
