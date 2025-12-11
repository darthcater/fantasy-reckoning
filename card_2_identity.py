"""
Card 2: The Three Fates
Calculate manager archetype and parallel timelines
"""

def calculate_card_2_identity(calc, team_key: str) -> dict:
    """
    Calculate Card 2: The Three Fates metrics

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with archetype, timelines, and skill grades
    """
    team = calc.teams[team_key]
    current_week = calc.league['current_week']

    # Get transactions for this team
    team_transactions = calc.transactions_by_team.get(team_key, [])

    # Calculate manager archetype based on transaction frequency
    num_transactions = len(team_transactions)
    avg_transactions_per_week = num_transactions / current_week if current_week > 0 else 0

    # Determine archetype
    if avg_transactions_per_week >= 2.0:
        archetype = "Tinkerer"
        archetype_description = "Always adjusting, constantly searching for an edge"
    elif avg_transactions_per_week >= 0.8:
        archetype = "Balanced"
        archetype_description = "Strategic moves when needed, patient otherwise"
    else:
        archetype = "Believer"
        archetype_description = "Trusts the draft, stays the course"

    # Calculate three parallel timelines
    actual_wins = 0
    actual_losses = 0
    actual_ties = 0

    optimal_lineup_wins = 0
    optimal_lineup_losses = 0
    optimal_lineup_ties = 0

    total_actual_points = 0
    total_optimal_points = 0
    total_bench_points_left = 0

    weekly_efficiency = []

    # Process each week to calculate timelines
    for week in range(1, current_week + 1):
        week_key = f'week_{week}'

        # Get this team's data
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        actual_points = week_data.get('actual_points', 0)

        # Calculate optimal lineup
        roster = week_data.get('roster', {})
        optimal_result = calc.calculate_optimal_lineup(roster, filter_injured=False)
        optimal_points = optimal_result['optimal_points']
        bench_left = optimal_result['points_left_on_bench']

        total_actual_points += actual_points
        total_optimal_points += optimal_points
        total_bench_points_left += bench_left

        if optimal_points > 0:
            weekly_efficiency.append(optimal_result['efficiency_pct'])

        # Get opponent score (already in week_data!)
        opponent_points = week_data.get('opponent_points', 0)
        result = week_data.get('result', '')

        # Calculate actual record using the correct result
        if result == 'W':
            actual_wins += 1
        elif result == 'L':
            actual_losses += 1
        elif result == 'T':
            actual_ties += 1

        # Calculate optimal lineup record
        if optimal_points > opponent_points:
            optimal_lineup_wins += 1
        elif optimal_points < opponent_points:
            optimal_lineup_losses += 1
        else:
            optimal_lineup_ties += 1

    # Calculate optimal adds timeline (simplified version)
    # This would require simulating what would happen if they picked up the best available FAs
    # For now, we'll estimate based on available FA points
    optimal_adds_wins = optimal_lineup_wins  # Placeholder - would need full simulation
    optimal_adds_losses = optimal_lineup_losses
    optimal_adds_ties = optimal_lineup_ties

    # Calculate efficiency metrics
    avg_efficiency = sum(weekly_efficiency) / len(weekly_efficiency) if weekly_efficiency else 0
    lineup_efficiency_pct = (total_actual_points / total_optimal_points * 100) if total_optimal_points > 0 else 0

    # Calculate skill grades

    # Draft grade - get from Card 1 data
    card_1 = calc.calculate_card_1(team_key)
    draft_grade = card_1.get('grade', 'C')

    # Lineup grade - based on efficiency
    if avg_efficiency >= 95:
        lineup_grade = 'A'
    elif avg_efficiency >= 90:
        lineup_grade = 'B'
    elif avg_efficiency >= 85:
        lineup_grade = 'C'
    elif avg_efficiency >= 80:
        lineup_grade = 'D'
    else:
        lineup_grade = 'F'

    # Waiver grade - based on ROS points from waiver pickups
    waiver_points = 0
    waiver_cost = 0

    for trans in team_transactions:
        if trans.get('type') == 'add':
            for player in trans.get('players', []):
                if player.get('transaction_data', {}).get('type') == 'add':
                    player_id = str(player.get('player_id'))
                    # Get timestamp to determine week
                    timestamp = trans.get('timestamp')
                    if timestamp:
                        # Calculate ROS points from this acquisition
                        trans_week = 1  # Simplified - would parse timestamp
                        ros = calc.get_ros_points(player_id, trans_week)
                        waiver_points += ros

                        # Get FAAB cost if available
                        faab = player.get('transaction_data', {}).get('faab_bid', 0)
                        if faab:
                            waiver_cost += int(faab)

    # Grade waivers based on points acquired
    avg_waiver_points_per_week = waiver_points / current_week if current_week > 0 else 0
    if avg_waiver_points_per_week >= 30:
        waiver_grade = 'A'
    elif avg_waiver_points_per_week >= 20:
        waiver_grade = 'B'
    elif avg_waiver_points_per_week >= 10:
        waiver_grade = 'C'
    elif avg_waiver_points_per_week >= 5:
        waiver_grade = 'D'
    else:
        waiver_grade = 'F'

    # Luck grade - based on actual vs expected record
    # Calculate points for/against
    total_points_against = 0
    for week in range(1, current_week + 1):
        week_key = f'week_{week}'
        # Simplified opponent points calculation
        # In a real implementation, we'd look up actual matchups
        # For now, use league average as approximation
        total_points_against += (total_actual_points / current_week) if current_week > 0 else 0

    # Simple luck metric: if you scored more than average but have losing record, bad luck
    league_avg_points = sum(
        sum(calc.weekly_data[tk].get(f'week_{w}', {}).get('actual_points', 0)
            for w in range(1, current_week + 1))
        for tk in calc.teams
    ) / len(calc.teams) if len(calc.teams) > 0 else 0

    points_vs_avg = total_actual_points - league_avg_points
    record_pct = actual_wins / (actual_wins + actual_losses) if (actual_wins + actual_losses) > 0 else 0.5

    # If high points but low wins = unlucky, low points but high wins = lucky
    if points_vs_avg > 100 and record_pct < 0.5:
        luck_grade = 'F'  # Very unlucky
    elif points_vs_avg < -100 and record_pct > 0.5:
        luck_grade = 'A'  # Very lucky
    else:
        luck_grade = 'C'  # Average luck

    return {
        'manager_name': team['manager_name'],
        'archetype': {
            'type': archetype,
            'description': archetype_description,
            'transactions_total': num_transactions,
            'transactions_per_week': round(avg_transactions_per_week, 2)
        },
        'timelines': {
            'actual': {
                'wins': actual_wins,
                'losses': actual_losses,
                'ties': actual_ties,
                'record': f"{actual_wins}-{actual_losses}" + (f"-{actual_ties}" if actual_ties > 0 else ""),
                'total_points': round(total_actual_points, 1)
            },
            'optimal_lineup': {
                'wins': optimal_lineup_wins,
                'losses': optimal_lineup_losses,
                'ties': optimal_lineup_ties,
                'record': f"{optimal_lineup_wins}-{optimal_lineup_losses}" + (f"-{optimal_lineup_ties}" if optimal_lineup_ties > 0 else ""),
                'total_points': round(total_optimal_points, 1),
                'wins_difference': optimal_lineup_wins - actual_wins
            },
            'optimal_adds': {
                'wins': optimal_adds_wins,
                'losses': optimal_adds_losses,
                'ties': optimal_adds_ties,
                'record': f"{optimal_adds_wins}-{optimal_adds_losses}" + (f"-{optimal_adds_ties}" if optimal_adds_ties > 0 else ""),
                'wins_difference': optimal_adds_wins - actual_wins,
                'note': 'Estimated - full simulation required for accuracy'
            }
        },
        'wins_left_on_table': {
            'lineup_wins_lost': optimal_lineup_wins - actual_wins,
            'waiver_wins_lost': max(0, optimal_adds_wins - optimal_lineup_wins),
            'total_wins_lost': max(optimal_lineup_wins - actual_wins, optimal_adds_wins - actual_wins),
            'perfect_season_record': f"{optimal_adds_wins}-{optimal_adds_losses}",
            'note': 'Total wins lost shows your gap to a perfect season'
        },
        'efficiency': {
            'lineup_efficiency_pct': round(lineup_efficiency_pct, 1),
            'avg_weekly_efficiency': round(avg_efficiency, 1),
            'total_bench_points_left': round(total_bench_points_left, 1),
            'avg_bench_points_per_week': round(total_bench_points_left / current_week, 1) if current_week > 0 else 0
        },
        'skill_grades': {
            'draft': draft_grade,
            'waivers': waiver_grade,
            'lineups': lineup_grade,
            'luck': luck_grade
        },
        'insights': {
            'waiver_points_acquired': round(waiver_points, 1),
            'waiver_faab_spent': waiver_cost,
            'points_vs_league_avg': round(points_vs_avg, 1)
        }
    }
