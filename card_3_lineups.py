"""
Card 3: The Lineup
How you played your pieces on the board

Displays:
- Lineup efficiency % and rank
- Actual record and optimal record
- Position units (strongest/weakest)
- Pivotal moment (fatal error or clutch call)
"""


def calculate_card_3_lineups(calc, team_key: str) -> dict:
    """
    Calculate Card 3: The Lineup - Weekly lineup decisions

    Returns:
        Dict with efficiency, timelines, and pivotal moments
    """
    team = calc.teams[team_key]
    manager_name = team.get('manager_name', 'Unknown')
    num_teams = len(calc.teams)
    regular_season_weeks = calc.get_regular_season_weeks()

    # ================================================================
    # EFFICIENCY AND TIMELINES
    # ================================================================

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

    # Process each week
    for week in regular_season_weeks:
        week_key = f'week_{week}'

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

        # Get opponent score
        opponent_points = week_data.get('opponent_points', 0)
        result = week_data.get('result', '')

        # Calculate actual record
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

    # Calculate efficiency metrics
    avg_efficiency = sum(weekly_efficiency) / len(weekly_efficiency) if weekly_efficiency else 0
    lineup_efficiency_pct = (total_actual_points / total_optimal_points * 100) if total_optimal_points > 0 else 0

    # Calculate league-wide efficiency for percentile
    all_team_efficiencies = []
    for tk in calc.teams.keys():
        team_total_actual = 0
        team_total_optimal = 0

        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key in calc.weekly_data.get(tk, {}):
                week_data = calc.weekly_data[tk][week_key]
                team_total_actual += week_data.get('actual_points', 0)

                roster = week_data.get('roster', {})
                optimal_result = calc.calculate_optimal_lineup(roster, filter_injured=False)
                team_total_optimal += optimal_result['optimal_points']

        team_efficiency = (team_total_actual / team_total_optimal * 100) if team_total_optimal > 0 else 0
        all_team_efficiencies.append((tk, team_efficiency))

    # Calculate league average
    league_avg_efficiency = sum(eff for _, eff in all_team_efficiencies) / len(all_team_efficiencies) if all_team_efficiencies else 0

    # Rank by efficiency
    all_team_efficiencies.sort(key=lambda x: x[1], reverse=True)
    efficiency_rank = next((i + 1 for i, (tk, _) in enumerate(all_team_efficiencies) if tk == team_key), num_teams)
    efficiency_percentile = ((num_teams - efficiency_rank) / (num_teams - 1)) * 100 if num_teams > 1 else 50

    # ================================================================
    # POSITION UNITS (Strongest/Weakest)
    # ================================================================

    # Sum started points by position for ALL teams
    league_position_totals = {tk: {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0} for tk in calc.teams}

    for tk in calc.teams:
        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key not in calc.weekly_data.get(tk, {}):
                continue

            roster = calc.weekly_data[tk][week_key].get('roster', {})
            starters = roster.get('starters', [])

            for starter in starters:
                # Use natural position (first eligible position), not selected_position
                eligible = starter.get('eligible_positions', [])
                if not eligible:
                    continue

                # Get natural position (first in eligible list)
                natural_pos = eligible[0]
                if natural_pos in ['QB', 'RB', 'WR', 'TE']:
                    pts = starter.get('actual_points', 0)
                    league_position_totals[tk][natural_pos] += pts

    # Rank each position across league (1 = most points = best)
    position_ranks = {tk: {} for tk in calc.teams}
    for pos in ['QB', 'RB', 'WR', 'TE']:
        sorted_teams = sorted(
            calc.teams.keys(),
            key=lambda t: league_position_totals[t][pos],
            reverse=True
        )
        for rank, tk in enumerate(sorted_teams, 1):
            position_ranks[tk][pos] = rank

    # Find best and worst for target team
    my_ranks = position_ranks[team_key]
    best_pos = min(my_ranks, key=my_ranks.get)  # Lowest rank number = best
    worst_pos = max(my_ranks, key=my_ranks.get)  # Highest rank number = worst

    position_units = {
        'strongest': {
            'position': best_pos,
            'rank': my_ranks[best_pos],
            'points': round(league_position_totals[team_key][best_pos], 1)
        },
        'weakest': {
            'position': worst_pos,
            'rank': my_ranks[worst_pos],
            'points': round(league_position_totals[team_key][worst_pos], 1)
        }
    }

    # ================================================================
    # WINS LEFT ON TABLE
    # ================================================================

    wins_diff = optimal_lineup_wins - actual_wins
    lineup_wins_lost = max(0, wins_diff)  # Only count positive difference

    # ================================================================
    # RANK ACTUAL AND OPTIMAL RECORDS ACROSS LEAGUE
    # ================================================================

    # Rank by actual wins
    all_team_actual_wins = {}
    all_team_optimal_wins = {}

    for tk in calc.teams.keys():
        tk_actual_wins = 0
        tk_optimal_wins = 0

        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key not in calc.weekly_data.get(tk, {}):
                continue

            week_data = calc.weekly_data[tk][week_key]
            result = week_data.get('result', '')

            # Actual wins
            if result == 'W':
                tk_actual_wins += 1

            # Calculate optimal wins
            roster = week_data.get('roster', {})
            optimal_result = calc.calculate_optimal_lineup(roster, filter_injured=False)
            optimal_pts = optimal_result['optimal_points']
            opp_pts = week_data.get('opponent_points', 0)

            if optimal_pts > opp_pts:
                tk_optimal_wins += 1

        all_team_actual_wins[tk] = tk_actual_wins
        all_team_optimal_wins[tk] = tk_optimal_wins

    # Rank actual wins (more wins = better = rank 1)
    sorted_actual = sorted(all_team_actual_wins.items(), key=lambda x: x[1], reverse=True)
    actual_record_rank = next((i + 1 for i, (tk, _) in enumerate(sorted_actual) if tk == team_key), num_teams)

    # Rank optimal wins (more wins = better = rank 1)
    sorted_optimal = sorted(all_team_optimal_wins.items(), key=lambda x: x[1], reverse=True)
    optimal_record_rank = next((i + 1 for i, (tk, _) in enumerate(sorted_optimal) if tk == team_key), num_teams)

    # ================================================================
    # PIVOTAL MOMENTS
    # ================================================================

    def can_swap_positions(started_slot, benched_player):
        """
        Check if a benched player could have legally filled the started slot.

        Args:
            started_slot: The roster slot (e.g., 'QB', 'WR', 'FLEX', 'DEF', 'IR')
            benched_player: The benched player dict with 'eligible_positions' field
        """
        # IR slots are not real starting positions - can't swap into them
        if started_slot in ['IR', 'BN']:
            return False

        # Get the benched player's eligible positions
        eligible = benched_player.get('eligible_positions', [])

        # Check if the started slot is in the benched player's eligible positions
        # This handles all cases: DEF, K, QB, WR, RB, TE, FLEX, Superflex
        return started_slot in eligible

    def is_obvious_decision(started, benched, slot_pos):
        """Filter out obvious start/sit decisions that don't require skill"""
        # Use eligible_positions[0] for real position (position field contains 'O' for offense)
        started_eligible = started.get('eligible_positions', [])
        benched_eligible = benched.get('eligible_positions', [])
        started_pos = started_eligible[0] if started_eligible else started.get('position', '')
        benched_pos = benched_eligible[0] if benched_eligible else benched.get('position', '')

        # OBVIOUS: QB in superflex/flex over non-QB
        if slot_pos in ['Q/W/R/T', 'FLEX', 'W/R/T']:
            if started_pos == 'QB' and benched_pos != 'QB':
                return True  # Starting QB in flex is obvious
            if benched_pos == 'QB' and started_pos != 'QB':
                return False  # NOT starting QB is a real mistake

        # OBVIOUS: Massive talent gap (check if one player scores way more)
        started_pts = started.get('actual_points', 0)
        benched_pts = benched.get('actual_points', 0)

        # If started scored 2x+ what benched scored, it was obvious to start them
        if started_pts > 0 and benched_pts > 0:
            if started_pts >= benched_pts * 2:
                return True  # Obvious to start the better player

        return False

    fatal_error_candidates = []
    clutch_call_candidates = []

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        actual_points = week_data.get('actual_points', 0)
        opponent_points = week_data.get('opponent_points', 0)
        week_result = week_data.get('result', '')

        # Get optimal lineup for this week
        roster = week_data.get('roster', {})
        optimal_result = calc.calculate_optimal_lineup(roster, filter_injured=False)
        optimal_points = optimal_result['optimal_points']
        bench_left = optimal_result['points_left_on_bench']

        margin = abs(actual_points - opponent_points)

        # FATAL ERROR: Lost a close game with significant bench points
        if week_result == 'L' and margin <= bench_left and bench_left >= 5:
            # Find the biggest mistake
            starters = roster.get('starters', [])
            bench = roster.get('bench', [])

            max_swap_impact = 0
            best_swap = None

            for started in starters:
                started_pts = started.get('actual_points', 0)
                started_slot = started.get('selected_position', 'FLEX')

                for benched in bench:
                    benched_pts = benched.get('actual_points', 0)

                    # Check if benched player could legally fill the started slot
                    if not can_swap_positions(started_slot, benched):
                        continue

                    # Skip obvious decisions (QB in superflex, massive talent gaps)
                    if is_obvious_decision(started, benched, started_slot):
                        continue

                    impact = benched_pts - started_pts
                    if impact > max_swap_impact:
                        max_swap_impact = impact
                        best_swap = {
                            'started_player': started.get('player_name', 'Unknown'),
                            'started_points': started_pts,
                            'benched_player': benched.get('player_name', 'Unknown'),
                            'benched_points': benched_pts,
                            'week': week,
                            'margin': margin,
                            'impact': impact
                        }

            if best_swap and max_swap_impact >= 5:
                fatal_error_candidates.append(best_swap)

        # CLUTCH CALL: Won a close game by making the right choice
        elif week_result == 'W' and margin <= 20:
            # Find the best decision
            starters = roster.get('starters', [])
            bench = roster.get('bench', [])

            for started in starters:
                started_pts = started.get('actual_points', 0)
                started_slot = started.get('selected_position', 'FLEX')

                for benched in bench:
                    benched_pts = benched.get('actual_points', 0)

                    # Skip if benched player wasn't viable (scored 0 = bye/injury/DNP)
                    if benched_pts == 0:
                        continue

                    # Check if benched player could legally fill the started slot
                    if not can_swap_positions(started_slot, benched):
                        continue

                    # Skip obvious decisions
                    if is_obvious_decision(started, benched, started_slot):
                        continue

                    # If you would have lost by benching this player
                    if started_pts - benched_pts >= margin:
                        clutch_call_candidates.append({
                            'started_player': started.get('player_name', 'Unknown'),
                            'started_points': started_pts,
                            'benched_player': benched.get('player_name', 'Unknown'),
                            'benched_points': benched_pts,
                            'week': week,
                            'margin': margin,
                            'impact': started_pts - benched_pts
                        })
                        break

    # Choose the most impactful moment
    if fatal_error_candidates:
        fatal_error_candidates.sort(key=lambda x: x['impact'], reverse=True)
        pivotal_moment = fatal_error_candidates[0]
        moment_type = 'fatal_error'
    elif clutch_call_candidates:
        clutch_call_candidates.sort(key=lambda x: x['impact'], reverse=True)
        pivotal_moment = clutch_call_candidates[0]
        moment_type = 'clutch_call'
    else:
        # Fallback: find any loss with bench points
        pivotal_moment = {
            'started_player': 'N/A',
            'started_points': 0,
            'benched_player': 'N/A',
            'benched_points': 0,
            'week': 1,
            'margin': 0
        }
        moment_type = 'fatal_error'

    # ================================================================
    # RETURN CARD DATA
    # ================================================================

    return {
        'manager_name': manager_name,
        'efficiency': {
            'lineup_efficiency_pct': round(lineup_efficiency_pct, 1),
            'avg_weekly_efficiency': round(avg_efficiency, 1),
            'league_avg_efficiency': round(league_avg_efficiency, 1),
            'league_rank_numeric': efficiency_rank,
            'percentile': round(efficiency_percentile, 1)
        },
        'position_units': position_units,
        'timelines': {
            'actual': {
                'wins': actual_wins,
                'losses': actual_losses,
                'ties': actual_ties,
                'record': f"{actual_wins}-{actual_losses}",
                'total_points': round(total_actual_points, 1),
                'rank': actual_record_rank
            },
            'optimal_lineup': {
                'wins': optimal_lineup_wins,
                'losses': optimal_lineup_losses,
                'ties': optimal_lineup_ties,
                'record': f"{optimal_lineup_wins}-{optimal_lineup_losses}",
                'total_points': round(total_optimal_points, 1),
                'wins_difference': optimal_lineup_wins - actual_wins,
                'rank': optimal_record_rank
            }
        },
        'wins_left_on_table': {
            'lineup_wins_lost': lineup_wins_lost,
            'waiver_wins_lost': 0,
            'total_wins_lost': lineup_wins_lost
        },
        'pivotal_moments': {
            'moment_type': moment_type,
            'the_fatal_error': pivotal_moment if moment_type == 'fatal_error' else {},
            'the_clutch_call': pivotal_moment if moment_type == 'clutch_call' else {}
        }
    }
