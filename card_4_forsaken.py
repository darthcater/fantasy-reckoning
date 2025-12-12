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

    # Calculate impact of drops with player names
    drops_that_hurt = []
    for drop in dropped_players:
        if drop.get('ros_points', 0) > 0:
            player_id = drop['player_id']
            player_name = calc.player_names.get(player_id, f"Player {player_id}")  # NEW: Add player name

            drops_that_hurt.append({
                'player_id': player_id,
                'player_name': player_name,  # NEW
                'drop_week': drop['drop_week'],
                'acquired_by': drop.get('acquired_by_name', 'Waiver wire'),
                'ros_points': round(drop.get('ros_points', 0), 1),
                'faab_cost': drop.get('faab_cost_to_acquire', 0),
                'context': f"Dropped week {drop['drop_week']}, went on to score {drop.get('ros_points', 0):.1f} ROS points"  # NEW: Context
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

    # Calculate waiver efficiency rate
    # Find all players added by this manager
    added_players = []
    for trans in calc.transactions:
        if trans.get('type') not in ['add', 'trade']:
            continue

        timestamp = trans.get('timestamp', 0)
        try:
            trans_date = datetime.fromtimestamp(timestamp)
            days_since_start = (trans_date - season_start).days
            trans_week = max(1, min(current_week, (days_since_start // 7) + 1))
        except:
            trans_week = 1

        # Check for adds by this manager
        for player in trans.get('players', []):
            if not isinstance(player, dict):
                continue

            trans_data = player.get('transaction_data', {})
            if trans_data.get('type') == 'add' and trans_data.get('destination_team_key') == team_key:
                player_id = str(player.get('player_id', ''))
                if player_id:
                    added_players.append({
                        'player_id': player_id,
                        'add_week': trans_week
                    })

    # For each added player, check if they were productive
    productive_adds = 0
    total_adds = len(added_players)
    replacement_threshold = 5.0  # Minimum points per game to be considered productive

    for add in added_players:
        player_id = add['player_id']
        add_week = add['add_week']

        # Check weeks after they were added
        games_started = 0
        total_points_in_starts = 0

        for week in range(add_week, current_week + 1):
            week_key = f'week_{week}'
            if week_key not in calc.weekly_data.get(team_key, {}):
                continue

            week_data = calc.weekly_data[team_key][week_key]
            roster = week_data.get('roster', {})
            starters = roster.get('starters', [])

            # Check if this player started
            for starter in starters:
                if str(starter.get('player_id')) == player_id:
                    games_started += 1
                    total_points_in_starts += starter.get('points', 0)
                    break

        # Consider productive if started at least 1 game with decent avg
        if games_started > 0:
            avg_points = total_points_in_starts / games_started
            if avg_points >= replacement_threshold:
                productive_adds += 1

    # Calculate efficiency rate
    efficiency_rate = (productive_adds / total_adds * 100) if total_adds > 0 else 0

    # ====================================================================================
    # THE HAUNTING: The ghost that won't leave you alone
    # ====================================================================================

    if worst_drops:
        biggest_drop = worst_drops[0]
        drop_player_name = biggest_drop.get('player_name', 'Unknown')
        drop_ros_points = biggest_drop.get('ros_points', 0)
        drop_week = biggest_drop.get('drop_week', 0)
        acquired_by = biggest_drop.get('acquired_by', 'Waiver wire')

        the_haunting = {
            'player_name': drop_player_name,
            'week_forsaken': drop_week,
            'what_they_became': f"Scored {drop_ros_points:.0f} points after you discarded them",
            'where_they_went': acquired_by,
            'the_mistake': f"You dropped {drop_player_name} in Week {drop_week}, thinking they were done. They weren't.",
            'the_ghost': f"{drop_player_name} haunts you. Every notification, every waiver claim by someone else, every start against you.",
            'unforgivable': drop_ros_points > 150,
            'cost': f"~{min(3, total_drop_impact // 50):.0f} wins lost to impatience"
        }
    elif waiver_opportunity_cost > 500:
        the_haunting = {
            'player_name': 'The waiver wire itself',
            'week_forsaken': 'All season',
            'what_they_became': f"{waiver_opportunity_cost:.0f} points left unclaimed",
            'where_they_went': 'Into your rivals\' lineups',
            'the_mistake': f"You made only {total_adds} waiver moves all season. The wire was rich with talent. You starved.",
            'the_ghost': "Every breakout player you ignored whispers your name in the dark.",
            'unforgivable': waiver_opportunity_cost > 1000,
            'cost': '2-3 wins lost to inaction'
        }
    else:
        the_haunting = {
            'player_name': 'None',
            'week_forsaken': None,
            'what_they_became': 'You managed your roster prudently',
            'where_they_went': 'N/A',
            'the_mistake': 'No major drops haunt you',
            'the_ghost': "Your conscience is clear. For now.",
            'unforgivable': False,
            'cost': 'Minimal'
        }

    # ====================================================================================
    # THE BETRAYAL: How your forsaken players helped your enemies
    # ====================================================================================

    # Calculate which rivals benefited from your drops
    rivals_helped = {}
    for drop in drops_that_hurt:
        acquired_by = drop.get('acquired_by', 'Waiver wire')
        if acquired_by != 'Waiver wire':
            if acquired_by not in rivals_helped:
                rivals_helped[acquired_by] = {
                    'manager_name': acquired_by,
                    'players_taken': [],
                    'total_points_gained': 0
                }
            rivals_helped[acquired_by]['players_taken'].append(drop['player_name'])
            rivals_helped[acquired_by]['total_points_gained'] += drop['ros_points']

    # Find biggest beneficiary
    if rivals_helped:
        biggest_beneficiary = max(rivals_helped.values(), key=lambda x: x['total_points_gained'])

        the_betrayal = {
            'you_gave_them_away': len([d for d in drops_that_hurt if d.get('acquired_by') != 'Waiver wire']),
            'total_points_to_rivals': round(sum(d['ros_points'] for d in drops_that_hurt if d.get('acquired_by') != 'Waiver wire'), 1),
            'biggest_beneficiary': biggest_beneficiary['manager_name'],
            'what_they_got': f"{len(biggest_beneficiary['players_taken'])} of your discarded players for {biggest_beneficiary['total_points_gained']:.0f} points",
            'the_irony': f"You armed {biggest_beneficiary['manager_name']} with the weapons that helped defeat you.",
            'self_inflicted': True,
            'players_list': biggest_beneficiary['players_taken']
        }
    else:
        the_betrayal = {
            'you_gave_them_away': 0,
            'total_points_to_rivals': 0,
            'biggest_beneficiary': None,
            'what_they_got': 'Nothing significant',
            'the_irony': "Your drops stayed on waivers. No rival profited from your mistakes.",
            'self_inflicted': False,
            'players_list': []
        }

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
        },
        'waiver_efficiency': {
            'total_adds': total_adds,
            'productive_adds': productive_adds,
            'efficiency_rate': round(efficiency_rate, 1),
            'wasted_adds': total_adds - productive_adds,
            'note': f"{productive_adds} of {total_adds} waiver adds produced value (≥{replacement_threshold} PPG when started)"
        },
        'the_haunting': the_haunting,  # The ghost that won't leave you alone
        'the_betrayal': the_betrayal  # How your drops helped your enemies
    }
