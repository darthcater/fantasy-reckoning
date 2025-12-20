"""
Card 3: Lineups
Lineup efficiency and decision-making analysis.

Analyzes your weekly lineup decisions:
- Lineup efficiency (actual vs optimal)
- Bench points wasted
- Pivotal moments where different lineups would have changed outcomes
"""
from league_metrics import (
    calculate_league_ranking,
    get_grade_from_percentile
)


def calculate_card_3_lineups(calc, team_key: str) -> dict:
    """
    Calculate Card 3: Lineups - Weekly lineup efficiency and decisions

    Combines efficiency metrics with pivotal moment analysis:
    1. Lineup Efficiency - How well you set lineups (actual vs optimal)
    2. Decision Patterns - Trends in your lineup management
    3. Pivotal Moments - Games where different lineups would have changed results
    4. Fatal Error - The single biggest missed opportunity

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with comprehensive weekly decision analysis
    """
    team = calc.teams[team_key]
    current_week = calc.league['current_week']

    # Get transactions for this team
    team_transactions = calc.transactions_by_team.get(team_key, [])

    # Calculate manager archetype based on LEAGUE-RELATIVE activity and effectiveness
    num_transactions = len(team_transactions)
    avg_transactions_per_week = num_transactions / current_week if current_week > 0 else 0

    # Calculate league-wide transaction rates for comparison
    all_team_transaction_rates = []
    for tk in calc.teams.keys():
        tk_transactions = calc.transactions_by_team.get(tk, [])
        tk_rate = len(tk_transactions) / current_week if current_week > 0 else 0
        all_team_transaction_rates.append(tk_rate)

    # Sort to get percentiles
    all_team_transaction_rates_sorted = sorted(all_team_transaction_rates)

    # Find this manager's activity percentile (higher = more active)
    manager_rank = sum(1 for rate in all_team_transaction_rates_sorted if rate <= avg_transactions_per_week)
    activity_percentile = (manager_rank / len(all_team_transaction_rates_sorted)) * 100 if len(all_team_transaction_rates_sorted) > 0 else 50

    # Calculate effectiveness ROI: points added per transaction
    # Calculate directly here to avoid circular dependency with Card 4
    total_points_added = 0
    effective_adds_count = 0

    for transaction in team_transactions:
        # Get player added
        if transaction['type'] in ['add', 'trade']:
            player_id = str(transaction.get('player_id', ''))
            if player_id and player_id in calc.player_points_by_week:
                # Calculate ROS (Rest of Season) points after acquisition
                transaction_week = transaction.get('week', 1)
                ros_points = sum(
                    pts for week, pts in calc.player_points_by_week[player_id].items()
                    if week >= transaction_week
                )
                total_points_added += ros_points

                # Count as effective if added >=20 ROS points
                if ros_points >= 20:
                    effective_adds_count += 1

    roi_per_transaction = total_points_added / num_transactions if num_transactions > 0 else 0
    efficiency_rate = (effective_adds_count / num_transactions * 100) if num_transactions > 0 else 0

    # Determine archetype using 2D matrix: Activity × Effectiveness
    # Activity levels: Low (<33rd percentile), Medium (33-66th), High (>66th)
    # Effectiveness: Low (<40% efficiency), High (>=40%)

    if activity_percentile < 33:  # LOW ACTIVITY
        if efficiency_rate >= 40 or num_transactions == 0:
            archetype = "The Idle Genius"
            archetype_description = "Trusts the draft, rarely moves. When you do, it counts."
        else:
            archetype = "The Passive Loser"
            archetype_description = "Inactive on waivers. The wire passed you by."
    elif activity_percentile > 66:  # HIGH ACTIVITY
        if efficiency_rate >= 40:
            archetype = "The Active Optimizer"
            archetype_description = "Always hunting, always improving. Waivers are your weapon."
        else:
            archetype = "The Busy Fool"
            archetype_description = "Constant churning, little return. Activity without purpose."
    else:  # MEDIUM ACTIVITY (Balanced)
        if efficiency_rate >= 50:
            archetype = "The Balanced Strategist"
            archetype_description = "Strategic moves when needed. Quality over quantity."
        else:
            archetype = "The Cautious Tinkerer"
            archetype_description = "Moderate activity, moderate results. Playing it safe."

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

    # ====================================================================================
    # ENHANCED CONTEXT: Calculate league-wide benchmarks for comparison
    # ====================================================================================

    # Calculate league-wide efficiency statistics
    all_team_efficiencies = []
    all_team_records = []

    for tk in calc.teams.keys():
        team_total_actual = 0
        team_total_optimal = 0
        team_wins = 0
        team_losses = 0

        for week in range(1, current_week + 1):
            week_key = f'week_{week}'
            if week_key in calc.weekly_data.get(tk, {}):
                week_data = calc.weekly_data[tk][week_key]
                team_total_actual += week_data.get('actual_points', 0)

                roster = week_data.get('roster', {})
                optimal_result = calc.calculate_optimal_lineup(roster, filter_injured=False)
                team_total_optimal += optimal_result['optimal_points']

                result = week_data.get('result', '')
                if result == 'W':
                    team_wins += 1
                elif result == 'L':
                    team_losses += 1

        team_efficiency = (team_total_actual / team_total_optimal * 100) if team_total_optimal > 0 else 0
        all_team_efficiencies.append((tk, team_efficiency, team_wins))
        all_team_records.append((tk, team_wins, team_losses))

    # Calculate league average efficiency
    league_avg_efficiency = sum(eff for _, eff, _ in all_team_efficiencies) / len(all_team_efficiencies) if all_team_efficiencies else 0

    # Calculate playoff team efficiency (top 6 teams by wins)
    all_team_records_sorted = sorted(all_team_records, key=lambda x: x[1], reverse=True)
    playoff_teams = [tk for tk, _, _ in all_team_records_sorted[:6]]
    playoff_team_efficiencies = [eff for tk, eff, _ in all_team_efficiencies if tk in playoff_teams]
    playoff_avg_efficiency = sum(playoff_team_efficiencies) / len(playoff_team_efficiencies) if playoff_team_efficiencies else 0

    # Calculate league ranking for lineup efficiency (PRIMARY METRIC)
    all_team_efficiency_dict = {tk: eff for tk, eff, _ in all_team_efficiencies}
    efficiency_ranking = calculate_league_ranking(all_team_efficiency_dict, team_key, reverse=True)

    # ====================================================================================
    # ENHANCED CONTEXT: Archetype impact analysis (NEW: League-Relative)
    # ====================================================================================

    # Calculate archetype impact on results
    archetype_impact = {}

    # Calculate league context for this manager
    num_teams = len(calc.teams)
    activity_rank = sum(1 for rate in all_team_transaction_rates if rate < avg_transactions_per_week) + 1

    if archetype == "The Active Optimizer":
        archetype_impact = {
            'strategy': f'High-activity waiver wire approach ({activity_rank}/{num_teams} in activity)',
            'effectiveness': f'Highly effective: {efficiency_rate:.0f}% hit rate',
            'context': f"{num_transactions} transactions generated {total_points_added:.0f} ROS points",
            'verdict': 'Your hustle created value. Active + effective = winning formula.'
        }
    elif archetype == "The Busy Fool":
        archetype_impact = {
            'strategy': f'High-activity waiver wire approach ({activity_rank}/{num_teams} in activity)',
            'effectiveness': f'Ineffective: Only {efficiency_rate:.0f}% hit rate',
            'context': f"{num_transactions} transactions generated only {total_points_added:.0f} ROS points",
            'verdict': 'Your tinkering was noise, not signal. Slow down and be selective.'
        }
    elif archetype == "The Balanced Strategist":
        archetype_impact = {
            'strategy': f'Strategic, measured approach ({activity_rank}/{num_teams} in activity)',
            'effectiveness': f'Effective: {efficiency_rate:.0f}% hit rate',
            'context': f"{num_transactions} targeted transactions, {total_points_added:.0f} ROS points added",
            'verdict': 'Quality over quantity. You picked your spots well.'
        }
    elif archetype == "The Cautious Tinkerer":
        archetype_impact = {
            'strategy': f'Moderate activity ({activity_rank}/{num_teams} in activity)',
            'effectiveness': f'Mixed results: {efficiency_rate:.0f}% hit rate',
            'context': f"{num_transactions} transactions, {total_points_added:.0f} ROS points added",
            'verdict': 'Playing it safe. More boldness could unlock value.'
        }
    elif archetype == "The Idle Genius":
        # Low activity but effective - trust the draft
        draft_roi_data = calc.calculate_card_1(team_key)
        draft_rank = draft_roi_data.get('rank', 7)
        if draft_rank <= 3:
            archetype_impact = {
                'strategy': f'Low-activity, draft-dependent approach ({activity_rank}/{num_teams} in activity)',
                'effectiveness': 'Worked - elite draft carried you',
                'context': f"Only {num_transactions} transactions, draft ranked #{draft_rank}",
                'verdict': 'Your faith in the draft was justified. When you did move, it counted.'
            }
        else:
            archetype_impact = {
                'strategy': f'Low-activity, draft-dependent approach ({activity_rank}/{num_teams} in activity)',
                'effectiveness': f'Risky - draft ranked #{draft_rank}, but your {num_transactions} moves were quality',
                'context': f"{efficiency_rate:.0f}% hit rate on limited activity",
                'verdict': 'Low volume, high quality. But you left opportunity on the table.'
            }
    else:  # The Passive Loser
        draft_roi_data = calc.calculate_card_1(team_key)
        draft_rank = draft_roi_data.get('rank', 7)
        archetype_impact = {
            'strategy': f'Inactive approach ({activity_rank}/{num_teams} in activity)',
            'effectiveness': f'Failed - only {efficiency_rate:.0f}% hit rate on {num_transactions} moves',
            'context': f"Draft ranked #{draft_rank}, minimal waiver activity, poor results",
            'verdict': 'The waiver wire passed you by. You needed to do more, and do it better.'
        }

    # ====================================================================================
    # ENHANCED CONTEXT: Timeline explanations
    # ====================================================================================

    # Calculate wins gaps
    lineup_wins_gap = optimal_lineup_wins - actual_wins
    waiver_wins_gap = max(0, optimal_adds_wins - optimal_lineup_wins)

    timeline_explanations = {
        'actual': {
            'description': 'What actually happened',
            'context': f"You went {actual_wins}-{actual_losses} with {total_actual_points:.0f} points scored",
            'analysis': 'This is your real season - the choices you made, the lineups you set'
        },
        'optimal_lineup': {
            'description': 'If you had set perfect lineups every week',
            'context': f"You would have gone {optimal_lineup_wins}-{optimal_lineup_losses} with {total_optimal_points:.0f} points",
            'analysis': f"You left {lineup_wins_gap} win{'s' if lineup_wins_gap != 1 else ''} on the table by benching {total_bench_points_left:.0f} points" if lineup_wins_gap > 0 else "Your lineup decisions were nearly perfect",
            'gap': lineup_wins_gap
        },
        'optimal_adds': {
            'description': 'If you had added the best available players each week',
            'context': f"You would have gone {optimal_adds_wins}-{optimal_adds_losses} (estimated)",
            'analysis': f"Perfect waiver moves could have gained you {waiver_wins_gap} more win{'s' if waiver_wins_gap != 1 else ''}" if waiver_wins_gap > 0 else "Waiver moves wouldn't have helped much",
            'gap': waiver_wins_gap,
            'note': 'Estimated - full simulation required for accuracy'
        }
    }

    # ====================================================================================
    # WHICH FATE AWAITS YOU? - Choose your 2026 destiny
    # ====================================================================================

    # Present three possible futures based on which timeline they follow

    # Fate 1: The Path of Repetition (if they change nothing)
    fate_repetition = {
        'name': 'The Path of Repetition',
        'description': 'You change nothing. You draft the same way, set lineups the same way, chase the same waiver wire ghosts.',
        'projected_record': f"{actual_wins}-{actual_losses}",
        'outlook': 'Stagnation. The same mistakes. The same regrets.',
        'probability': 'Likely, if you do not heed the warnings.'
    }

    # Fate 2: The Path of Discipline (if they fix lineup efficiency)
    if lineup_wins_gap >= 2:
        projected_discipline_wins = min(14, actual_wins + lineup_wins_gap)
        projected_discipline_losses = 14 - projected_discipline_wins

        fate_discipline = {
            'name': 'The Path of Discipline',
            'description': f'You master lineup decisions. You reach {playoff_avg_efficiency:.1f}% efficiency like the playoff teams.',
            'projected_record': f"{projected_discipline_wins}-{projected_discipline_losses}",
            'improvement': f"+{lineup_wins_gap} wins from better lineup management",
            'requirement': 'Study projections. Set lineups early. Trust data over gut feelings.',
            'probability': 'Achievable with focus and discipline.'
        }
    else:
        fate_discipline = {
            'name': 'The Path of Discipline',
            'description': f'Your lineup management is already strong ({lineup_efficiency_pct:.1f}% efficiency).',
            'projected_record': f"{actual_wins}-{actual_losses}",
            'improvement': 'Minimal gains available here',
            'requirement': 'Maintain your current approach.',
            'probability': 'This path offers little.'
        }

    # Fate 3: The Path of Perfection (if they fix everything)
    total_gains = optimal_adds_wins - actual_wins
    fate_perfection = {
        'name': 'The Path of Perfection',
        'description': 'Perfect lineups. Perfect waiver adds. Perfect execution.',
        'projected_record': f"{optimal_adds_wins}-{optimal_adds_losses}",
        'improvement': f"+{total_gains} wins from flawless management",
        'requirement': timeline_explanations['optimal_adds']['analysis'],
        'probability': 'Nearly impossible. Perfection is a mirage.',
        'note': 'This fate requires clairvoyance. Do not chase it.'
    }

    which_fate = {
        'your_season': f"You went {actual_wins}-{actual_losses} in 2025.",
        'wins_abandoned': f"You left {total_gains} wins on the table across all decisions.",
        'fates': {
            'repetition': fate_repetition,
            'discipline': fate_discipline,
            'perfection': fate_perfection
        },
        'the_choice': 'Three paths lie before you. The first leads to more of the same. The second is achievable. The third is a dream.',
        'recommended_path': 'discipline' if lineup_wins_gap >= 2 else 'repetition'
    }

    # Build base result with efficiency metrics
    result = {
        'manager_name': team['manager_name'],
        'archetype': {
            'type': archetype,
            'description': archetype_description,
            'transactions_total': num_transactions,
            'transactions_per_week': round(avg_transactions_per_week, 2),
            # NEW: League-relative metrics
            'activity_percentile': round(activity_percentile, 1),
            'activity_rank': f"{activity_rank}/{num_teams}",
            'efficiency_rate': round(efficiency_rate, 1),
            'roi_per_transaction': round(roi_per_transaction, 1),
            'impact': archetype_impact  # Rich context about archetype effectiveness
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
        'timeline_explanations': timeline_explanations,  # NEW: Plain English explanations
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
            'avg_bench_points_per_week': round(total_bench_points_left / current_week, 1) if current_week > 0 else 0,
            'league_avg_efficiency': round(league_avg_efficiency, 1),  # NEW: League comparison
            'playoff_avg_efficiency': round(playoff_avg_efficiency, 1),  # NEW: Playoff benchmark
            'efficiency_gap': round(playoff_avg_efficiency - lineup_efficiency_pct, 1),  # NEW: Gap to playoffs
            # PRIMARY METRIC: League ranking
            'league_rank': efficiency_ranking['league_rank'],
            'league_rank_numeric': efficiency_ranking['league_rank_numeric'],
            'percentile': efficiency_ranking['percentile'],
            'gap_to_average': efficiency_ranking['gap_to_average'],
            'grade': get_grade_from_percentile(efficiency_ranking['percentile'])
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
        },
        'which_fate_awaits_you': which_fate  # Three possible futures for 2026
    }

    # Merge pivotal moments analysis from card_3_fatal_error
    # TODO: Rebuild pivotal moments calculation now that card_3_fatal_error is removed

    # Add pivotal moments to the result
    result['pivotal_moments'] = {
        'inflection_points': [],
        'the_fatal_error': {},
        'preventable_losses': 0,
        'unavoidable_losses': 0,
        'total_losses': 0,
        'fate_sealed_pct': 0,
    }

    return result
