"""
Card 2: The Ledger
Where your points came from (and where they went)

Displays:
- Draft points and rank, best value, biggest bust
- Waiver points and rank
- Trade impact and rank, best trade
- Costly drops and rank, most costly drop
"""


def calculate_card_2_ledger(calc, team_key: str) -> dict:
    """
    Calculate Card 2: The Ledger - Points accounting

    Returns:
        Dict with draft, waivers, trades, and costly drops analysis
    """
    team = calc.teams[team_key]
    manager_name = team.get('manager_name', 'Unknown')
    num_teams = len(calc.teams)

    # ================================================================
    # DRAFT ANALYSIS
    # ================================================================

    # Detect draft type: auction (varied costs) vs snake (costs are 0 or uniform)
    all_costs = [p.get('cost', 0) for p in calc.draft]
    unique_costs = len(set(all_costs))
    is_auction = unique_costs > 3 and max(all_costs) > 0

    # Get all draft picks for this team
    team_draft_picks = [p for p in calc.draft if p.get('team_key') == team_key]

    # Calculate total points scored by drafted players
    draft_total_points = 0
    draft_player_scores = []

    for pick in team_draft_picks:
        player_id = str(pick.get('player_id', ''))
        # Use player_names mapping to resolve "Unknown" names from draft data
        player_name = calc.player_names.get(player_id, pick.get('player_name', 'Unknown'))

        # Sum all points this player scored
        player_total = sum(calc.player_points_by_week.get(player_id, {}).values())
        draft_total_points += player_total

        draft_player_scores.append({
            'player_name': player_name,
            'player_id': player_id,
            'points': player_total,
            'cost': pick.get('cost', 0),
            'round': pick.get('round', 0),
            'pick': pick.get('pick', 0),
            'overall_pick': pick.get('overall_pick', 0)
        })

    # Rank by draft points
    all_team_draft_points = {}
    for tk in calc.teams.keys():
        tk_picks = [p for p in calc.draft if p.get('team_key') == tk]
        tk_total = 0
        for pick in tk_picks:
            player_id = str(pick.get('player_id', ''))
            tk_total += sum(calc.player_points_by_week.get(player_id, {}).values())
        all_team_draft_points[tk] = tk_total

    sorted_teams = sorted(all_team_draft_points.items(), key=lambda x: x[1], reverse=True)
    draft_rank = next((i + 1 for i, (tk, _) in enumerate(sorted_teams) if tk == team_key), num_teams)

    # Calculate best value and biggest bust based on draft type
    if draft_player_scores:
        if is_auction:
            # AUCTION: Use points per dollar (pts/$)
            for p in draft_player_scores:
                p['value'] = p['points'] / max(p['cost'], 1)
                p['value_type'] = 'pts/$'
            draft_player_scores.sort(key=lambda x: x['value'], reverse=True)
            best_value = draft_player_scores[0]

            # Biggest bust: lowest points among players who cost $5+
            expensive_players = [p for p in draft_player_scores if p['cost'] >= 5]
            if expensive_players:
                expensive_players.sort(key=lambda x: x['points'])
                biggest_bust = expensive_players[0]
            else:
                biggest_bust = {}
        else:
            # SNAKE: Use Points Above Round Average (PARA)
            # Calculate average points per round across all teams
            round_points = {}  # {round: [points]}
            for pick in calc.draft:
                rnd = pick.get('round', 0)
                if rnd > 0:
                    pid = str(pick.get('player_id', ''))
                    pts = sum(calc.player_points_by_week.get(pid, {}).values())
                    if rnd not in round_points:
                        round_points[rnd] = []
                    round_points[rnd].append(pts)

            round_avg = {rnd: sum(pts) / len(pts) for rnd, pts in round_points.items() if pts}

            # Calculate PARA for each player
            for p in draft_player_scores:
                rnd = p['round']
                avg = round_avg.get(rnd, 0)
                p['value'] = p['points'] - avg  # Points Above Round Average
                p['round_avg'] = round(avg, 1)
                p['value_type'] = 'PARA'

            # Best value: highest PARA (most above round average)
            draft_player_scores.sort(key=lambda x: x['value'], reverse=True)
            best_value = draft_player_scores[0]

            # Biggest bust: lowest PARA among early round picks (Rd 1-4)
            early_picks = [p for p in draft_player_scores if p['round'] <= 4]
            if early_picks:
                early_picks.sort(key=lambda x: x['value'])
                biggest_bust = early_picks[0]
            else:
                biggest_bust = {}
    else:
        best_value = {}
        biggest_bust = {}

    # ================================================================
    # WAIVER ANALYSIS
    # ================================================================

    team_transactions = calc.transactions_by_team.get(team_key, [])
    waiver_adds = [t for t in team_transactions if t.get('type') in ['add', 'trade']]

    waiver_total_points_started = 0
    waiver_adds_list = []

    for transaction in waiver_adds:
        # Player info is now flattened at transaction level
        player_id = str(transaction.get('player_id', ''))
        player_name = transaction.get('player_name', 'Unknown')
        if not player_id:
            continue

        # Calculate points scored by this player as a starter for this team
        total_points_started = 0
        weeks_started = 0

        regular_season_weeks = calc.get_regular_season_weeks()
        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key in calc.weekly_data.get(team_key, {}):
                starters = calc.weekly_data[team_key][week_key].get('roster', {}).get('starters', [])
                for starter in starters:
                    if str(starter.get('player_id')) == player_id:
                        pts = starter.get('actual_points', 0)
                        total_points_started += pts
                        weeks_started += 1

        waiver_total_points_started += total_points_started

        if total_points_started > 0:
            waiver_adds_list.append({
                'player_name': player_name,
                'player_id': player_id,
                'points_started': total_points_started,
                'weeks_started': weeks_started
            })

    # Rank by waiver points
    all_team_waiver_points = {}
    regular_season_weeks = calc.get_regular_season_weeks()
    for tk in calc.teams.keys():
        tk_transactions = calc.transactions_by_team.get(tk, [])
        tk_waiver_adds = [t for t in tk_transactions if t.get('type') in ['add', 'trade']]
        tk_total = 0

        for transaction in tk_waiver_adds:
            # Player info is now flattened at transaction level
            player_id = str(transaction.get('player_id', ''))
            if not player_id:
                continue

            for week in regular_season_weeks:
                week_key = f'week_{week}'
                if week_key in calc.weekly_data.get(tk, {}):
                    starters = calc.weekly_data[tk][week_key].get('roster', {}).get('starters', [])
                    for starter in starters:
                        if str(starter.get('player_id')) == player_id:
                            tk_total += starter.get('actual_points', 0)

        all_team_waiver_points[tk] = tk_total

    sorted_teams = sorted(all_team_waiver_points.items(), key=lambda x: x[1], reverse=True)
    waiver_rank = next((i + 1 for i, (tk, _) in enumerate(sorted_teams) if tk == team_key), num_teams)

    # Get best waiver adds
    waiver_adds_list.sort(key=lambda x: x['points_started'], reverse=True)
    best_adds = waiver_adds_list[:5] if waiver_adds_list else []

    # ================================================================
    # TRADE ANALYSIS
    # ================================================================

    trades = [t for t in team_transactions if t.get('type') == 'trade']
    trade_net_impact = 0
    trades_list = []

    for trade in trades:
        # For now, set impact to 0 (would need complex trade analysis)
        trades_list.append({
            'players_out': [trade.get('player_name', 'Unknown')],
            'players_in': [],
            'net_started_impact': 0
        })

    # Rank by trade impact
    trade_rank = num_teams // 2  # Default to middle

    best_trade = trades_list[0] if trades_list else {}

    # ================================================================
    # COSTLY DROPS ANALYSIS
    # ================================================================

    drops = [t for t in team_transactions if t.get('type') == 'drop']
    costly_drops_total = 0
    costly_drops_list = []

    for drop in drops:
        player_id = str(drop.get('player_id', ''))
        player_name = drop.get('player_name', 'Unknown')
        dropped_week = drop.get('week', 1)

        # Calculate points this player scored AFTER being dropped
        # BUT only count weeks when they were NOT on this team's roster
        points_after_drop = 0
        weeks_away = 0

        for week in range(dropped_week + 1, calc.league.get('current_week', 14) + 1):
            week_key = f'week_{week}'

            # Check if player is on this team's roster this week
            player_on_roster = False
            if week_key in calc.weekly_data.get(team_key, {}):
                roster = calc.weekly_data[team_key][week_key].get('roster', {})
                all_players = roster.get('starters', []) + roster.get('bench', [])
                for p in all_players:
                    if str(p.get('player_id')) == player_id:
                        player_on_roster = True
                        break

            # Only count points when player was NOT on our roster
            if not player_on_roster and player_id in calc.player_points_by_week:
                points_after_drop += calc.player_points_by_week[player_id].get(week, 0)
                weeks_away += 1

        if points_after_drop > 20:  # Only count significant losses
            costly_drops_total += points_after_drop
            costly_drops_list.append({
                'player_name': player_name,
                'player_id': player_id,
                'started_pts': points_after_drop,
                'dropped_week': dropped_week,
                'weeks_away': weeks_away
            })

    # Rank by costly drops (higher is worse)
    all_team_costly_drops = {}
    for tk in calc.teams.keys():
        tk_transactions = calc.transactions_by_team.get(tk, [])
        tk_drops = [t for t in tk_transactions if t.get('type') == 'drop']
        tk_total = 0

        for drop in tk_drops:
            player_id = str(drop.get('player_id', ''))
            dropped_week = drop.get('week', 1)

            for week in range(dropped_week + 1, calc.league.get('current_week', 14) + 1):
                week_key = f'week_{week}'

                # Check if player is on this team's roster this week
                player_on_roster = False
                if week_key in calc.weekly_data.get(tk, {}):
                    roster = calc.weekly_data[tk][week_key].get('roster', {})
                    all_players = roster.get('starters', []) + roster.get('bench', [])
                    for p in all_players:
                        if str(p.get('player_id')) == player_id:
                            player_on_roster = True
                            break

                # Only count points when player was NOT on this team's roster
                if not player_on_roster and player_id in calc.player_points_by_week:
                    tk_total += calc.player_points_by_week[player_id].get(week, 0)

        all_team_costly_drops[tk] = tk_total

    sorted_teams = sorted(all_team_costly_drops.items(), key=lambda x: x[1])  # Ascending - lower is better
    costly_drops_rank = next((i + 1 for i, (tk, _) in enumerate(sorted_teams) if tk == team_key), num_teams)

    # Get most costly drop
    costly_drops_list.sort(key=lambda x: x['started_pts'], reverse=True)
    most_costly_drop = costly_drops_list[0] if costly_drops_list else {}

    # ================================================================
    # RETURN CARD DATA
    # ================================================================

    return {
        'manager_name': manager_name,
        'draft': {
            'total_points': round(draft_total_points, 1),
            'rank': draft_rank,
            'steals': [best_value] if best_value else [],
            'busts': [biggest_bust] if biggest_bust else []
        },
        'waivers': {
            'total_points_started': round(waiver_total_points_started, 1),
            'rank': waiver_rank,
            'total_adds': len(waiver_adds),
            'productive_adds': len([a for a in waiver_adds_list if a['points_started'] >= 20]),
            'efficiency_rate': (len([a for a in waiver_adds_list if a['points_started'] >= 20]) / len(waiver_adds) * 100) if waiver_adds else 0,
            'best_adds': best_adds,
            'adds': waiver_adds_list
        },
        'trades': {
            'net_started_impact': trade_net_impact,
            'rank': trade_rank,
            'trades': trades_list
        },
        'costly_drops': {
            'total_value_given_away': round(costly_drops_total, 1),
            'rank': costly_drops_rank,
            'most_costly_drop': most_costly_drop
        }
    }
