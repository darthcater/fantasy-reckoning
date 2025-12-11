"""
Card 3: The Fatal Error
Identify 2-3 pivotal moments that changed the season
"""

from collections import defaultdict

def calculate_card_3_inflection(calc, team_key: str) -> dict:
    """
    Calculate Card 3: The Fatal Error

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with pivotal moments
    """
    team = calc.teams[team_key]

    # Use regular season weeks only (playoffs are different beast)
    regular_season_weeks = calc.get_regular_season_weeks()

    inflection_points = []

    # INFLECTION TYPE 1: Lineup Mistakes That Flipped Outcomes
    # Find weeks where bench player would have won/lost the matchup

    for week in regular_season_weeks:
        week_key = f'week_{week}'

        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        actual_points = week_data.get('actual_points', 0)
        roster = week_data.get('roster', {})

        # Calculate optimal lineup
        optimal_result = calc.calculate_optimal_lineup(roster, filter_injured=False)
        optimal_points = optimal_result['optimal_points']
        bench_left = optimal_result['points_left_on_bench']

        # Get actual opponent data
        opponent_id = week_data.get('opponent_id', '')
        opponent_points = week_data.get('opponent_points', 0)
        opponent_name = calc.teams.get(opponent_id, {}).get('manager_name', 'Unknown')

        # Check if lineup mistake changed outcome
        actual_won = actual_points > opponent_points
        optimal_won = optimal_points > opponent_points

        if actual_won != optimal_won and bench_left > 5:
            # This was a pivotal lineup decision
            impact_type = 'Loss' if optimal_won and not actual_won else 'Win'

            inflection_points.append({
                'type': 'lineup_mistake',
                'week': week,
                'description': f"Week {week} lineup decision vs {opponent_name}",
                'impact': impact_type,
                'details': {
                    'actual_score': round(actual_points, 1),
                    'optimal_score': round(optimal_points, 1),
                    'opponent_score': round(opponent_points, 1),
                    'bench_points_left': round(bench_left, 1),
                    'outcome': f"{'Won' if actual_won else 'Lost'} with actual lineup, would have {'won' if optimal_won else 'lost'} with optimal"
                },
                'win_impact': 1 if (optimal_won and not actual_won) else -1
            })

    # INFLECTION TYPE 2: Close Losses Where Small Changes Mattered
    # Games lost by < 10 points where a bench player could have changed outcome

    for week in regular_season_weeks:
        week_key = f'week_{week}'

        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        actual_points = week_data.get('actual_points', 0)
        roster = week_data.get('roster', {})

        # Get actual opponent data
        opponent_id = week_data.get('opponent_id', '')
        opponent_points = week_data.get('opponent_points', 0)
        opponent_name = calc.teams.get(opponent_id, {}).get('manager_name', 'Unknown')

        # Check for close loss
        margin = actual_points - opponent_points

        if -10 < margin < 0:  # Lost by less than 10 points
            # Find bench player who could have changed it
            bench = roster.get('bench', [])
            starters = roster.get('starters', [])

            # Find lowest-scoring starter
            if starters:
                lowest_starter = min(starters, key=lambda p: p.get('actual_points', 0))
                lowest_starter_points = lowest_starter.get('actual_points', 0)

                # Find highest-scoring bench player
                if bench:
                    highest_bench = max(bench, key=lambda p: p.get('actual_points', 0))
                    highest_bench_points = highest_bench.get('actual_points', 0)

                    swap_diff = highest_bench_points - lowest_starter_points

                    if swap_diff > abs(margin):
                        # This swap would have won the game
                        inflection_points.append({
                            'type': 'close_loss',
                            'week': week,
                            'description': f"Week {week} heartbreaker vs {opponent_name}",
                            'impact': 'Loss',
                            'details': {
                                'margin': round(abs(margin), 1),
                                'wrong_starter': f"Player {lowest_starter['player_id']}",
                                'wrong_starter_points': round(lowest_starter_points, 1),
                                'bench_player': f"Player {highest_bench['player_id']}",
                                'bench_player_points': round(highest_bench_points, 1),
                                'swap_difference': round(swap_diff, 1)
                            },
                            'win_impact': 1
                        })

    # INFLECTION TYPE 3: High-Impact Weeks (scored way above/below average)
    # Find weeks where unusual performance changed trajectory

    team_weekly_scores = []
    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key in calc.weekly_data.get(team_key, {}):
            points = calc.weekly_data[team_key][week_key].get('actual_points', 0)
            team_weekly_scores.append((week, points))

    if team_weekly_scores:
        avg_score = sum(s[1] for s in team_weekly_scores) / len(team_weekly_scores)

        for week, score in team_weekly_scores:
            week_key = f'week_{week}'

            # Get actual opponent data for this week
            week_data = calc.weekly_data[team_key][week_key]
            opponent_points = week_data.get('opponent_points', 0)

            won = score > opponent_points
            deviation = score - avg_score

            # Flag weeks with >30 point deviation from average
            if abs(deviation) > 30:
                inflection_points.append({
                    'type': 'boom_or_bust',
                    'week': week,
                    'description': f"Week {week} {'explosion' if deviation > 0 else 'disaster'}",
                    'impact': 'Win' if won else 'Loss',
                    'details': {
                        'score': round(score, 1),
                        'avg_score': round(avg_score, 1),
                        'deviation': round(deviation, 1),
                        'result': 'Won' if won else 'Lost'
                    },
                    'win_impact': 1 if won else -1
                })

    # Sort inflection points by absolute win impact
    inflection_points.sort(key=lambda x: abs(x.get('win_impact', 0)), reverse=True)

    # Take top 5 most impactful moments
    top_inflections = inflection_points[:5]

    # Calculate cumulative win impact
    total_win_impact = sum(ip.get('win_impact', 0) for ip in top_inflections)

    # Categorize inflections
    lineup_mistakes = [ip for ip in top_inflections if ip['type'] == 'lineup_mistake']
    close_losses = [ip for ip in top_inflections if ip['type'] == 'close_loss']
    boom_bust = [ip for ip in top_inflections if ip['type'] == 'boom_or_bust']

    # Identify the single biggest mistake (preventable loss with highest impact)
    biggest_mistake = None
    for ip in top_inflections:
        if ip['type'] in ['lineup_mistake', 'close_loss'] and ip['impact'] == 'Loss':
            biggest_mistake = ip
            break  # First one is already sorted by impact

    return {
        'manager_name': team['manager_name'],
        'inflection_points': top_inflections,
        'biggest_mistake': {
            'event': biggest_mistake if biggest_mistake else None,
            'tagline': f"Week {biggest_mistake['week']}: {biggest_mistake['description']}" if biggest_mistake else "No major preventable mistakes",
            'note': 'This single decision had the biggest impact on your season'
        },
        'summary': {
            'total_inflection_points': len(top_inflections),
            'lineup_mistakes': len(lineup_mistakes),
            'close_losses': len(close_losses),
            'boom_bust_weeks': len(boom_bust),
            'cumulative_win_impact': total_win_impact,
            'biggest_what_if': top_inflections[0] if top_inflections else None
        },
        'insights': {
            'preventable_losses': len([ip for ip in top_inflections if ip['impact'] == 'Loss' and ip['type'] in ['lineup_mistake', 'close_loss']]),
            'total_preventable_win_impact': sum(ip.get('win_impact', 0) for ip in top_inflections if ip['type'] in ['lineup_mistake', 'close_loss'])
        }
    }
