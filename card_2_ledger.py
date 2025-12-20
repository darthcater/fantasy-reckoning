"""
Card 2: The Ledger
Point distribution - draft, waivers, free agents, trades, and costly drops.
Supports both Auction and Snake drafts.
"""
from datetime import datetime


def get_week_from_timestamp(timestamp):
    """Convert timestamp to NFL week number"""
    trade_date = datetime.fromtimestamp(timestamp)
    week_1_start = datetime(2025, 9, 4)  # 2025 NFL season start
    days_since_week1 = (trade_date - week_1_start).days
    week = max(1, min(18, (days_since_week1 // 7) + 1))
    return week


def _get_league_positions(calc) -> list:
    """
    Get list of valid positions for this league

    Args:
        calc: FantasyWrappedCalculator instance

    Returns:
        List of position strings (e.g., ['QB', 'RB', 'WR', 'TE', 'K', 'DEF'])
    """
    if 'roster_positions' in calc.league and calc.league['roster_positions']:
        roster = calc.league['roster_positions']
        # Filter to non-bench, non-IR positions, exclude flex combinations
        positions = [pos for pos in roster.keys()
                     if pos not in ['BN', 'IR', 'N/A'] and '/' not in pos]
        return positions if positions else ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
    else:
        # Fallback to standard positions
        return ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']


def calculate_waiver_analysis(calc, team_key, transactions, transactions_by_team,
                              player_points_by_week, weekly_data, teams):
    """
    Calculate waiver wire performance for a manager.
    Returns points added via waivers and conversion efficiency.
    """
    team_transactions = transactions_by_team.get(team_key, [])

    # Find all waiver adds for this team
    waiver_adds = []
    for trans in team_transactions:
        trans_type = trans.get('type', '')
        # Include both 'add' and 'add/drop' transactions
        if trans_type in ['add', 'add/drop']:
            # Get players list and filter for 'add' type
            players_list = trans.get('players', [])
            for player in players_list:
                # Check if this is an add (not a drop)
                if player.get('type') == 'add':
                    player_id = str(player.get('player_id'))
                    player_name = player.get('player_name', 'Unknown')
                    # Get week from timestamp
                    timestamp = trans.get('timestamp', 0)
                    week = get_week_from_timestamp(timestamp) if timestamp else 0
                    waiver_adds.append({
                        'player_id': player_id,
                        'player_name': player_name,
                        'week': week
                    })

    # Calculate points started by waiver adds
    total_points_started = 0
    add_details = []

    for add in waiver_adds:
        player_id = add['player_id']
        add_week = add['week']

        # Calculate points this player scored in starting lineup
        points_started = 0
        weeks_started = []

        # Look through all weeks after the add
        for week in range(add_week + 1, calc.league.get('current_week', 15) + 1):
            week_key = f'week_{week}'
            if week_key in weekly_data.get(team_key, {}):
                week_data = weekly_data[team_key][week_key]
                # Get starters from roster
                roster = week_data.get('roster', {})
                week_starters = roster.get('starters', [])

                # Check if this player started this week
                for starter in week_starters:
                    if str(starter.get('player_id')) == player_id:
                        points = starter.get('points', 0)
                        points_started += points
                        weeks_started.append(week)
                        break

        if points_started > 0:
            total_points_started += points_started
            add_details.append({
                'player_name': add['player_name'],
                'player_id': player_id,
                'points_started': round(points_started, 1),
                'weeks_started': len(weeks_started),
                'added_week': add_week
            })

    # Sort by points started
    add_details.sort(key=lambda x: x['points_started'], reverse=True)

    # Calculate efficiency metrics
    total_adds = len(waiver_adds)
    productive_adds = len([a for a in add_details if a['points_started'] > 10])
    efficiency_rate = (productive_adds / total_adds * 100) if total_adds > 0 else 0

    return {
        'total_adds': total_adds,
        'total_points_started': round(total_points_started, 1),
        'productive_adds': productive_adds,
        'efficiency_rate': round(efficiency_rate, 1),
        'best_adds': add_details[:5],  # Top 5
        'adds': add_details
    }


def calculate_card_2_ledger(calc, team_key: str) -> dict:
    """
    Calculate Card II: The Ledger - Your Points Story

    Tells the complete story of your points:
    - Draft: Total points from drafted players
    - Waivers: Points started by waiver pickups
    - Trades: Net started points gained/lost
    - Costly Drops: Points given to opponents via drops

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with points story breakdown including draft, waivers, trades, and costly drops
    """
    team = calc.teams[team_key]
    draft_picks = calc.draft_by_team.get(team_key, [])

    # Get draft analysis
    if not draft_picks:
        draft_result = {
            'error': 'No draft data available',
            'draft_type': 'unavailable',
            'message': 'Draft analysis unavailable (offline draft, keeper league, or missing data)',
            'grade': 'N/A',
            'rank': 0,
            'steals': [],
            'busts': []
        }
    else:
        # Check draft type and route to appropriate analysis
        if calc.draft_type == 'snake':
            draft_result = _calculate_snake_draft_analysis(calc, team_key, draft_picks)
        else:
            draft_result = _calculate_auction_draft_analysis(calc, team_key, draft_picks)

    # Get trade analysis
    from trade_impact_calculation import calculate_trade_impact
    trade_result = calculate_trade_impact(
        team_key,
        calc.transactions,
        calc.weekly_data,
        calc.teams
    )

    # Get costly drops analysis
    from costly_drops_calculation import calculate_costly_drops
    costly_drops_result = calculate_costly_drops(
        team_key,
        calc.transactions,
        calc.weekly_data,
        calc.teams
    )

    # Get waiver wire analysis
    waiver_result = calculate_waiver_analysis(
        calc,
        team_key,
        calc.transactions,
        calc.transactions_by_team,
        calc.player_points_by_week,
        calc.weekly_data,
        calc.teams
    )

    # Combine draft, waivers, and trades analysis
    combined_result = {
        'manager_name': team['manager_name'],
        'card_name': 'The Roster',

        # Draft section
        'draft': draft_result,

        # Waiver wire section
        'waivers': waiver_result,

        # Trade section
        'trades': trade_result,

        # Costly drops section
        'costly_drops': costly_drops_result,

        # Overall roster acquisition summary - "Your Points Story"
        'summary': {
            'total_acquisition_channels': 3,
            'draft_grade': draft_result.get('grade', 'N/A'),
            'waiver_efficiency': waiver_result.get('efficiency_rate', 0),
            'trade_verdict': trade_result.get('overall_verdict', 'No trades'),

            # Points story metrics
            'points_story': {
                'draft_points': draft_result.get('total_points', 0),
                'waiver_points_started': waiver_result.get('total_points_started', 0),
                'trade_net_impact': trade_result.get('net_started_impact', 0),
                'costly_drops_total': costly_drops_result.get('total_value_given_away', 0),
            }
        }
    }

    return combined_result


def _calculate_snake_draft_analysis(calc, team_key: str, draft_picks: list) -> dict:
    """
    Calculate draft value for SNAKE drafts

    Analyzes draft performance by comparing draft position vs player finish position
    within each position group (QB, RB, WR, TE)

    Also calculates Value Over Replacement (VOR) for each pick to provide
    league-specific draft value assessment

    Returns:
        Dict with snake draft analysis including VOR metrics
    """
    team = calc.teams[team_key]
    num_teams = calc.league.get('num_teams', 12)

    # Step 0: Calculate replacement levels for VOR analysis
    replacement_levels = calc.calculate_replacement_levels()

    # Step 1: Get all drafted players across league with their positions and season points
    all_drafted_players = []
    for tk in calc.teams.keys():
        team_draft_picks = calc.draft_by_team.get(tk, [])
        for pick in team_draft_picks:
            player_id = str(pick['player_id'])

            # Get player's primary position from weekly roster data
            position = _get_player_position(calc, player_id)

            # Calculate season total points
            total_points = sum(calc.player_points_by_week.get(player_id, {}).values())

            # Calculate VOR (Value Over Replacement)
            weeks_played = len([pts for pts in calc.player_points_by_week.get(player_id, {}).values() if pts > 0])
            ppg = total_points / weeks_played if weeks_played > 0 else 0
            replacement_ppg = replacement_levels.get(position, 0)
            vor = ppg - replacement_ppg  # Points per game above replacement

            all_drafted_players.append({
                'player_id': player_id,
                'team_key': pick['team_key'],
                'round': pick.get('round', 1),
                'pick': pick.get('pick', 1),
                'overall_pick': pick.get('overall_pick', 1),
                'position': position,
                'total_points': total_points,
                'ppg': ppg,
                'vor': vor  # NEW: VOR metric
            })

    # Step 2: Calculate positional rankings (drafted and finish)
    # Group by position
    by_position = {}
    for player in all_drafted_players:
        pos = player['position']
        if pos not in by_position:
            by_position[pos] = []
        by_position[pos].append(player)

    # For each position, assign draft rank and finish rank
    for pos in by_position:
        players = by_position[pos]

        # Sort by draft order to get draft rank
        players.sort(key=lambda x: x['overall_pick'])
        for i, p in enumerate(players, 1):
            p['draft_pos_rank'] = i  # QB1, QB2, etc. (by draft order)

        # Sort by points to get finish rank
        players.sort(key=lambda x: x['total_points'], reverse=True)
        for i, p in enumerate(players, 1):
            p['finish_pos_rank'] = i  # QB1, QB2, etc. (by points scored)

    # Step 3: Analyze this manager's picks
    manager_picks = []
    for pick in draft_picks:
        player_id = str(pick['player_id'])

        # Find this player in all_drafted_players
        player_data = next((p for p in all_drafted_players if p['player_id'] == player_id), None)
        if not player_data:
            continue

        # Calculate round from overall pick
        pick_round = ((pick.get('overall_pick', 1) - 1) // num_teams) + 1

        # Calculate value round (what round should their finish rank have gone in?)
        finish_rank = player_data['finish_pos_rank']
        value_round = _calculate_expected_round(player_data['position'], finish_rank, num_teams)

        # Round difference (positive = steal, negative = bust)
        round_diff = pick_round - value_round

        # Weight by draft round (early picks matter more)
        if pick_round <= 3:
            weight = 3
        elif pick_round <= 6:
            weight = 2
        else:
            weight = 1

        weighted_value = round_diff * weight

        # NEW: VOR-based value assessment
        player_vor = player_data['vor']
        player_ppg = player_data['ppg']

        # Determine VOR grade (relative to position)
        if player_vor >= 8:
            vor_grade = 'Elite'
        elif player_vor >= 5:
            vor_grade = 'Strong'
        elif player_vor >= 2:
            vor_grade = 'Solid'
        elif player_vor >= 0:
            vor_grade = 'Replacement'
        else:
            vor_grade = 'Below Replacement'

        manager_picks.append({
            'player_id': player_id,
            'player_name': calc.player_names.get(player_id, f"Player {player_id}"),
            'position': player_data['position'],
            'round': pick_round,
            'overall_pick': pick.get('overall_pick', 1),
            'draft_pos_rank': player_data['draft_pos_rank'],
            'finish_pos_rank': player_data['finish_pos_rank'],
            'total_points': round(player_data['total_points'], 1),
            'value_round': value_round,
            'round_diff': round_diff,
            'weighted_value': weighted_value,
            'ppg': round(player_ppg, 1),  # NEW
            'vor': round(player_vor, 1),  # NEW
            'vor_grade': vor_grade  # NEW
        })

    # Step 4: Calculate overall value score
    total_weighted_value = sum(p['weighted_value'] for p in manager_picks)

    # Step 5: Compare to league average
    all_teams_values = []
    for tk in calc.teams.keys():
        team_draft = calc.draft_by_team.get(tk, [])
        team_value = 0
        for pick in team_draft:
            player_id = str(pick['player_id'])
            player_data = next((p for p in all_drafted_players if p['player_id'] == player_id), None)
            if player_data:
                pick_round = ((pick.get('overall_pick', 1) - 1) // num_teams) + 1
                value_round = _calculate_expected_round(player_data['position'], player_data['finish_pos_rank'], num_teams)
                round_diff = pick_round - value_round

                if pick_round <= 3:
                    weight = 3
                elif pick_round <= 6:
                    weight = 2
                else:
                    weight = 1

                team_value += round_diff * weight

        all_teams_values.append((tk, team_value))

    # Rank (higher value = better draft = lower rank number)
    all_teams_values.sort(key=lambda x: x[1], reverse=True)
    rank = next((i for i, (tk, _) in enumerate(all_teams_values, 1) if tk == team_key), len(all_teams_values))

    # Calculate grade
    percentile = (len(all_teams_values) - rank + 1) / len(all_teams_values)
    if percentile >= 0.8:
        grade = 'A'
    elif percentile >= 0.6:
        grade = 'B'
    elif percentile >= 0.4:
        grade = 'C'
    elif percentile >= 0.2:
        grade = 'D'
    else:
        grade = 'F'

    # Step 6: Identify steals and busts (2+ round difference threshold)
    steals = [p for p in manager_picks if p['round_diff'] >= 2]
    steals.sort(key=lambda x: x['round_diff'], reverse=True)

    busts = [p for p in manager_picks if p['round_diff'] <= -2]
    busts.sort(key=lambda x: x['round_diff'])

    # Step 6b: Calculate VOR-based draft value
    total_vor = sum(p['vor'] for p in manager_picks)

    # Calculate expected VOR for draft position (league average at each pick)
    # For simplicity: use league-average VOR
    league_avg_vor_per_pick = sum(p['vor'] for p in all_drafted_players) / len(all_drafted_players) if all_drafted_players else 0
    expected_vor = league_avg_vor_per_pick * len(manager_picks)
    vor_surplus = total_vor - expected_vor

    # VOR-based steals: High VOR players drafted late
    # Sort by VOR, take top players who were picked in later rounds (Rd 4+)
    vor_steals = [p for p in manager_picks if p['vor'] >= 5 and p['round'] >= 4]
    vor_steals.sort(key=lambda x: x['vor'], reverse=True)

    # VOR-based busts: Low/negative VOR players drafted early
    vor_busts = [p for p in manager_picks if p['vor'] < 0 and p['round'] <= 8]
    vor_busts.sort(key=lambda x: x['vor'])

    # Step 7: "Walked past gold" - players available at multiple picks who became winners
    walked_past_gold = []

    # Get manager's draft picks sorted by overall pick
    manager_pick_numbers = sorted([p.get('overall_pick', 1) for p in draft_picks])

    # For each high-performing player (top 20% by points), check if manager passed on them multiple times
    all_drafted_players.sort(key=lambda x: x['total_points'], reverse=True)
    top_performers = all_drafted_players[:max(1, len(all_drafted_players) // 5)]  # Top 20%

    for player in top_performers:
        # Skip if manager actually drafted this player
        if player['team_key'] == team_key:
            continue

        # Count how many times this player was available when manager picked
        times_passed = 0
        missed_opportunities = []

        for mgr_pick_num in manager_pick_numbers:
            # Player was available if they were drafted after this manager's pick
            if player['overall_pick'] > mgr_pick_num:
                times_passed += 1
                missed_opportunities.append(mgr_pick_num)

        # Only include if passed on 2+ times
        if times_passed >= 2:
            walked_past_gold.append({
                'player_id': player['player_id'],
                'player_name': calc.player_names.get(player['player_id'], f"Player {player['player_id']}"),
                'position': player['position'],
                'times_passed': times_passed,
                'total_points': round(player['total_points'], 1),
                'finish_pos_rank': player['finish_pos_rank'],
                'actual_pick': player['overall_pick'],
                'missed_at_picks': missed_opportunities[:3],  # Show first 3 missed chances
                'note': f"Available at {times_passed} of your picks, scored {round(player['total_points'], 1)} points (#{player['finish_pos_rank']} {player['position']})"
            })

    # Sort by combination of times passed and total points
    walked_past_gold.sort(key=lambda x: (x['times_passed'] * x['total_points']), reverse=True)

    return {
        'manager_name': team['manager_name'],
        'draft_type': 'snake',
        'rank': rank,
        'grade': grade,
        'total_picks': len(draft_picks),
        'total_weighted_value': round(total_weighted_value, 1),
        'steals': [
            {
                'player_id': s['player_id'],
                'player_name': s['player_name'],
                'position': s['position'],
                'draft_round': s['round'],
                'draft_pos_rank': s['draft_pos_rank'],
                'finish_pos_rank': s['finish_pos_rank'],
                'points': s['total_points'],
                'ppg': s['ppg'],  # NEW
                'vor': s['vor'],  # NEW
                'vor_grade': s['vor_grade'],  # NEW
                'round_diff': s['round_diff'],
                'note': f"Drafted round {s['round']} (#{s['finish_pos_rank']} {s['position']}), performed like round {s['value_round']}. {s['ppg']} PPG ({s['vor']:+.1f} VOR)"
            }
            for s in steals[:3]
        ],
        'busts': [
            {
                'player_id': b['player_id'],
                'player_name': b['player_name'],
                'position': b['position'],
                'draft_round': b['round'],
                'draft_pos_rank': b['draft_pos_rank'],
                'finish_pos_rank': b['finish_pos_rank'],
                'points': b['total_points'],
                'ppg': b['ppg'],  # NEW
                'vor': b['vor'],  # NEW
                'vor_grade': b['vor_grade'],  # NEW
                'round_diff': b['round_diff'],
                'note': f"Drafted round {b['round']} (#{b['draft_pos_rank']} {b['position']}), finished as #{b['finish_pos_rank']} {b['position']}. {b['ppg']} PPG ({b['vor']:+.1f} VOR)"
            }
            for b in busts[:3]
        ],
        'walked_past_gold': walked_past_gold[:3],  # Top 3 most painful misses
        'vor_analysis': {  # NEW: VOR-specific metrics
            'total_vor': round(total_vor, 1),
            'expected_vor': round(expected_vor, 1),
            'vor_surplus': round(vor_surplus, 1),
            'replacement_levels': replacement_levels,
            'vor_steals': [
                {
                    'player_name': s['player_name'],
                    'position': s['position'],
                    'draft_round': s['round'],
                    'vor': s['vor'],
                    'vor_grade': s['vor_grade'],
                    'ppg': s['ppg'],
                    'note': f"Round {s['round']} pick delivered {s['vor']:+.1f} VOR ({s['vor_grade']})"
                }
                for s in vor_steals[:3]
            ],
            'vor_busts': [
                {
                    'player_name': b['player_name'],
                    'position': b['position'],
                    'draft_round': b['round'],
                    'vor': b['vor'],
                    'vor_grade': b['vor_grade'],
                    'ppg': b['ppg'],
                    'note': f"Round {b['round']} pick delivered {b['vor']:+.1f} VOR (below replacement)"
                }
                for b in vor_busts[:3]
            ],
            'summary': f"Total VOR: {total_vor:+.1f} (expected: {expected_vor:.1f}). Draft surplus: {vor_surplus:+.1f} VOR."
        }
    }


def _get_player_position(calc, player_id: str) -> str:
    """
    Get a player's primary position from weekly roster data

    Args:
        calc: FantasyWrappedCalculator instance
        player_id: Player ID

    Returns:
        Position string (QB, RB, WR, TE, K, DEF, or league-specific positions)
    """
    # Get valid positions for this league
    valid_positions = _get_league_positions(calc)

    # Check all weeks/teams to find this player
    for team_key in calc.weekly_data:
        for week_key in calc.weekly_data[team_key]:
            week_data = calc.weekly_data[team_key][week_key]
            roster = week_data.get('roster', {})

            # Check starters
            for player in roster.get('starters', []):
                if str(player.get('player_id')) == player_id:
                    # Use selected_position, or derive from eligible_positions
                    selected_pos = player.get('selected_position', '')

                    # Check if position is valid for this league
                    if selected_pos in valid_positions:
                        return selected_pos
                    elif '/' in selected_pos:  # Flex position
                        # Derive from eligible positions
                        eligible = player.get('eligible_positions', [])
                        for pos in valid_positions:
                            if pos in eligible:
                                return pos

            # Check bench
            for player in roster.get('bench', []):
                if str(player.get('player_id')) == player_id:
                    selected_pos = player.get('selected_position', '')
                    if selected_pos in valid_positions:
                        return selected_pos
                    elif selected_pos == 'BN':
                        # Derive from eligible positions
                        eligible = player.get('eligible_positions', [])
                        for pos in valid_positions:
                            if pos in eligible:
                                return pos

    return 'UNKNOWN'


def _calculate_expected_round(position: str, finish_rank: int, num_teams: int = 12) -> int:
    """
    Calculate what round a player should have been drafted based on their finish rank

    Uses positional scarcity assumptions:
    - QB: Less scarce, drafted later
    - RB/WR: High scarcity in early ranks
    - TE: Very scarce at top, falls off
    - K/DEF: Late rounds
    - Unknown positions: Generic linear model

    Args:
        position: Player position (QB, RB, WR, TE, K, DEF, or other)
        finish_rank: Where they finished within position (1 = best)
        num_teams: League size

    Returns:
        Expected draft round
    """
    if position == 'QB':
        # QBs go later due to depth
        # QB1-2: Round 2-3
        # QB3-6: Round 4-6
        # QB7+: Round 7+
        if finish_rank <= 2:
            return 2
        elif finish_rank <= 6:
            return 4
        elif finish_rank <= 12:
            return 7
        else:
            return 10

    elif position in ['RB', 'WR']:
        # RBs and WRs are high value early
        # Top 12: Rounds 1-2
        # 13-24: Rounds 3-4
        # 25-36: Rounds 5-6
        # 37+: Later rounds
        if finish_rank <= 12:
            return max(1, (finish_rank - 1) // 6 + 1)  # Ranks 1-6 → R1, 7-12 → R2
        elif finish_rank <= 24:
            return 3 + ((finish_rank - 13) // 12)
        elif finish_rank <= 36:
            return 5 + ((finish_rank - 25) // 12)
        else:
            return 7 + ((finish_rank - 37) // 24)

    elif position == 'TE':
        # TE is very scarce at top
        # TE1-3: Round 2-4
        # TE4-8: Round 6-8
        # TE9+: Round 10+
        if finish_rank <= 3:
            return 2 + finish_rank - 1
        elif finish_rank <= 8:
            return 6
        else:
            return 10

    elif position in ['K', 'DEF']:
        # Kickers and defenses go very late
        return max(12, 10 + finish_rank // 6)

    else:
        # Unknown position (IDP, etc.) - use generic linear model
        # Top-tier: rounds 1-3
        # Mid-tier: rounds 4-8
        # Late: rounds 9+
        if finish_rank <= num_teams:
            # Top N within position → rounds 1-3
            return max(1, (finish_rank - 1) // 4 + 1)
        elif finish_rank <= num_teams * 2:
            # Next tier → rounds 4-8
            return 4 + ((finish_rank - num_teams - 1) // num_teams) * 2
        else:
            # Late rounds
            return 9 + ((finish_rank - num_teams * 2 - 1) // (num_teams * 2))


def _calculate_auction_draft_analysis(calc, team_key: str, draft_picks: list) -> dict:
    """
    Calculate draft ROI for AUCTION drafts with enhanced context and explanations

    Returns:
        Dict with comprehensive auction draft analysis including:
        - VOR analysis
        - Positional spending breakdown
        - Contextual steals/busts with WHY they were good/bad
        - The Verdict (diagnosis)
        - The One Thing (actionable takeaway)
    """
    # Get team info
    team = calc.teams[team_key]

    # Step 0: Calculate replacement levels for VOR
    replacement_levels = calc.calculate_replacement_levels()

    # Step 1: Build comprehensive player data with positions and VOR
    drafted_players_with_data = []
    for pick in draft_picks:
        player_id = str(pick['player_id'])
        player_name = calc.player_names.get(player_id, f"Player {player_id}")

        # Get position
        position = _get_player_position(calc, player_id)

        # Calculate season stats
        total_points = sum(calc.player_points_by_week.get(player_id, {}).values())
        weeks_played = len([pts for pts in calc.player_points_by_week.get(player_id, {}).values() if pts > 0])
        ppg = total_points / weeks_played if weeks_played > 0 else 0

        # Calculate VOR
        replacement_ppg = replacement_levels.get(position, 0)
        vor = ppg - replacement_ppg

        # Determine VOR grade
        if vor >= 8:
            vor_grade = 'Elite'
        elif vor >= 5:
            vor_grade = 'Strong'
        elif vor >= 2:
            vor_grade = 'Solid'
        elif vor >= 0:
            vor_grade = 'Replacement'
        else:
            vor_grade = 'Below Replacement'

        # Calculate cost efficiency
        cost = pick['cost']
        per_point = cost / total_points if total_points > 0 else 999

        drafted_players_with_data.append({
            'player_id': player_id,
            'player_name': player_name,
            'position': position,
            'cost': cost,
            'points': total_points,
            'ppg': ppg,
            'weeks_played': weeks_played,
            'vor': vor,
            'vor_grade': vor_grade,
            'per_point': per_point
        })

    # Step 2: Calculate league-wide stats for context
    # Build all league picks with positions and costs
    league_picks_by_position = {}  # {position: [(cost, points, ppg), ...]}

    for tk in calc.teams.keys():
        team_picks = calc.draft_by_team.get(tk, [])
        for pick in team_picks:
            player_id = str(pick['player_id'])
            position = _get_player_position(calc, player_id)
            total_points = sum(calc.player_points_by_week.get(player_id, {}).values())
            weeks_played = len([pts for pts in calc.player_points_by_week.get(player_id, {}).values() if pts > 0])
            ppg = total_points / weeks_played if weeks_played > 0 else 0

            if position not in league_picks_by_position:
                league_picks_by_position[position] = []

            league_picks_by_position[position].append({
                'cost': pick['cost'],
                'points': total_points,
                'ppg': ppg
            })

    # Calculate positional averages
    positional_averages = {}
    for pos, picks in league_picks_by_position.items():
        avg_cost = sum(p['cost'] for p in picks) / len(picks) if picks else 0
        avg_points = sum(p['points'] for p in picks) / len(picks) if picks else 0
        avg_ppg = sum(p['ppg'] for p in picks) / len(picks) if picks else 0

        positional_averages[pos] = {
            'avg_cost': avg_cost,
            'avg_points': avg_points,
            'avg_ppg': avg_ppg,
            'count': len(picks)
        }

    # Step 3: Calculate cost tiers for each position (for bust/steal context)
    # Elite tier = top 20% cost, Mid tier = 20-60%, Budget = 60%+
    cost_tiers_by_position = {}
    for pos, picks in league_picks_by_position.items():
        if len(picks) < 3:
            continue

        costs_sorted = sorted([p['cost'] for p in picks], reverse=True)
        elite_threshold = costs_sorted[max(0, len(costs_sorted) // 5)]  # Top 20%
        mid_threshold = costs_sorted[max(0, len(costs_sorted) * 3 // 5)]  # Top 60%

        # Calculate expected points for each tier
        elite_picks = [p for p in picks if p['cost'] >= elite_threshold]
        mid_picks = [p for p in picks if mid_threshold <= p['cost'] < elite_threshold]
        budget_picks = [p for p in picks if p['cost'] < mid_threshold]

        cost_tiers_by_position[pos] = {
            'elite_threshold': elite_threshold,
            'mid_threshold': mid_threshold,
            'elite_avg_points': sum(p['points'] for p in elite_picks) / len(elite_picks) if elite_picks else 0,
            'mid_avg_points': sum(p['points'] for p in mid_picks) / len(mid_picks) if mid_picks else 0,
            'budget_avg_points': sum(p['points'] for p in budget_picks) / len(budget_picks) if budget_picks else 0
        }

    # Step 4: Calculate manager's overall stats
    total_spent = sum(p['cost'] for p in drafted_players_with_data)
    total_points = sum(p['points'] for p in drafted_players_with_data)
    manager_roi = total_spent / total_points if total_points > 0 else 999

    # Calculate league average ROI and rankings
    all_teams_roi = []
    for tk in calc.teams.keys():
        team_picks = calc.draft_by_team.get(tk, [])
        team_spent = sum(p['cost'] for p in team_picks)
        team_points = 0
        for p in team_picks:
            pid = str(p['player_id'])
            team_points += sum(calc.player_points_by_week.get(pid, {}).values())

        if team_points > 0:
            roi = team_spent / team_points
            all_teams_roi.append((tk, roi))

    league_avg_roi = sum(roi for _, roi in all_teams_roi) / len(all_teams_roi) if all_teams_roi else 0

    # Rank (lower ROI = better)
    all_teams_roi_sorted = sorted(all_teams_roi, key=lambda x: x[1])
    rank = next((i for i, (tk, _) in enumerate(all_teams_roi_sorted, 1) if tk == team_key), len(all_teams_roi))

    # Calculate percentile grade
    percentile = (len(all_teams_roi) - rank + 1) / len(all_teams_roi)
    if percentile >= 0.8:
        grade = 'A'
    elif percentile >= 0.6:
        grade = 'B'
    elif percentile >= 0.4:
        grade = 'C'
    elif percentile >= 0.2:
        grade = 'D'
    else:
        grade = 'F'

    # Step 5: Identify steals with CONTEXT
    steals_with_context = []
    for player in sorted(drafted_players_with_data, key=lambda x: x['per_point'])[:5]:  # Top 5 candidates
        if player['points'] < 50:  # Filter out low-scoring flukes
            continue

        pos = player['position']
        cost = player['cost']
        points = player['points']
        ppg = player['ppg']
        vor = player['vor']

        # Get positional context
        pos_avg = positional_averages.get(pos, {})
        avg_cost = pos_avg.get('avg_cost', cost)
        avg_points = pos_avg.get('avg_points', points)

        # Determine why this was a steal
        cost_saved = avg_cost - cost
        points_surplus = points - avg_points

        # Build contextual explanation
        if cost_saved > 10:
            why_good = f"Average {pos} cost ${avg_cost:.0f}, you paid ${cost}"
        elif points_surplus > 50:
            why_good = f"Delivered {points:.1f} pts (league avg {pos}: {avg_points:.1f} pts)"
        else:
            why_good = f"Elite {vor:+.1f} VOR at bargain price"

        # Determine tier they performed at
        if vor >= 8:
            performance_tier = f"{pos}1 elite performance"
        elif vor >= 5:
            performance_tier = f"Strong {pos}2 production"
        elif vor >= 2:
            performance_tier = f"Solid starter value"
        else:
            performance_tier = f"Replacement level"

        steals_with_context.append({
            'player_id': player['player_id'],
            'player_name': player['player_name'],
            'position': pos,
            'cost': cost,
            'points': round(points, 1),
            'ppg': round(ppg, 1),
            'vor': round(vor, 1),
            'vor_grade': player['vor_grade'],
            'per_point': round(player['per_point'], 3),
            'why_good': why_good,
            'performance_tier': performance_tier,
            'value_summary': f"${cost} → {points:.1f} pts ({ppg:.1f} PPG, {vor:+.1f} VOR)"
        })

    # Step 6: Identify busts with CONTEXT
    busts_with_context = []
    expensive_picks = [p for p in drafted_players_with_data if p['cost'] >= 20]  # $20+ threshold

    for player in sorted(expensive_picks, key=lambda x: x['per_point'], reverse=True)[:5]:  # Top 5 candidates
        pos = player['position']
        cost = player['cost']
        points = player['points']
        ppg = player['ppg']
        vor = player['vor']

        # Get tier expectations
        tier_data = cost_tiers_by_position.get(pos, {})

        # Determine what tier they paid for
        elite_threshold = tier_data.get('elite_threshold', 50)
        mid_threshold = tier_data.get('mid_threshold', 25)

        if cost >= elite_threshold:
            paid_tier = f"elite {pos}1"
            expected_points = tier_data.get('elite_avg_points', points * 2)
        elif cost >= mid_threshold:
            paid_tier = f"mid-tier {pos}2"
            expected_points = tier_data.get('mid_avg_points', points * 1.5)
        else:
            paid_tier = f"starter-level {pos}"
            expected_points = tier_data.get('budget_avg_points', points * 1.2)

        # Calculate shortfall
        points_shortfall = expected_points - points

        # Determine what production they actually got
        if vor < 0:
            got_tier = f"below-replacement production"
        elif vor < 2:
            got_tier = f"replacement-level production"
        elif ppg < positional_averages.get(pos, {}).get('avg_ppg', 0):
            got_tier = f"below-average production"
        else:
            got_tier = f"average production"

        # Build explanation
        why_hurt = f"Paid {paid_tier} price (${cost}), got {got_tier}"

        # Calculate estimated win impact
        # Rough estimate: every 30 points below expected ≈ 1 lost win
        estimated_wins_lost = max(0, points_shortfall / 30)

        # ONLY add to busts if they actually underperformed (positive shortfall)
        # Negative shortfall means they exceeded expectations (NOT a bust!)
        if points_shortfall > 0:
            busts_with_context.append({
                'player_id': player['player_id'],
                'player_name': player['player_name'],
                'position': pos,
                'cost': cost,
                'points': round(points, 1),
                'ppg': round(ppg, 1),
                'vor': round(vor, 1),
                'vor_grade': player['vor_grade'],
                'per_point': round(player['per_point'], 3),
                'why_hurt': why_hurt,
                'expected_points': round(expected_points, 1),
                'points_shortfall': round(points_shortfall, 1),
                'estimated_wins_lost': round(estimated_wins_lost, 1),
                'impact_summary': f"This pick cost you ~{estimated_wins_lost:.1f} wins" if estimated_wins_lost >= 0.5 else "Underperformed expectations"
            })

    # Step 7: Positional spending analysis ("The Money")
    positional_spending = {}
    for pos in set(p['position'] for p in drafted_players_with_data):
        pos_players = [p for p in drafted_players_with_data if p['position'] == pos]
        pos_spent = sum(p['cost'] for p in pos_players)
        pos_points = sum(p['points'] for p in pos_players)
        pos_count = len(pos_players)

        budget_pct = (pos_spent / total_spent * 100) if total_spent > 0 else 0

        # Compare to league average for this position
        league_avg_spent = positional_averages.get(pos, {}).get('avg_cost', 0) * pos_count
        league_avg_points = positional_averages.get(pos, {}).get('avg_points', 0) * pos_count

        spending_diff = pos_spent - league_avg_spent
        points_diff = pos_points - league_avg_points

        # Determine verdict
        if budget_pct > 30:  # Heavy investment
            if points_diff > 0:
                verdict = "GOOD VALUE ✓"
                verdict_explanation = f"Heavy investment paid off (+{points_diff:.0f} pts vs avg)"
            else:
                verdict = "OVERPAID ✗"
                verdict_explanation = f"Overspent by ${spending_diff:.0f}, got {points_diff:.0f} pts below average"
        elif budget_pct > 15:  # Moderate investment
            if points_diff > 20:
                verdict = "GOOD VALUE ✓"
                verdict_explanation = f"Solid value at this position"
            elif points_diff < -20:
                verdict = "WEAK ✗"
                verdict_explanation = f"Underperformed at key position"
            else:
                verdict = "FAIR VALUE ~"
                verdict_explanation = f"Performed near expectations"
        else:  # Light investment
            if points_diff > 0:
                verdict = "BARGAIN ✓✓"
                verdict_explanation = f"Got more than you paid for"
            else:
                verdict = "WEAK ✗"
                verdict_explanation = f"Didn't invest enough at this position"

        positional_spending[pos] = {
            'total_spent': pos_spent,
            'budget_pct': round(budget_pct, 1),
            'total_points': round(pos_points, 1),
            'player_count': pos_count,
            'avg_cost_per_player': round(pos_spent / pos_count, 1) if pos_count > 0 else 0,
            'verdict': verdict,
            'verdict_explanation': verdict_explanation,
            'league_comparison': f"${spending_diff:+.0f} vs league avg"
        }

    # Step 8: Generate "The Verdict" (diagnosis)
    # Identify the biggest problem(s)
    problems = []

    # Problem 1: Too many busts
    if len(busts_with_context) >= 3:
        total_bust_cost = sum(b['cost'] for b in busts_with_context[:3])
        problems.append(f"${total_bust_cost:.0f} wasted on {len(busts_with_context)} busts")

    # Problem 2: Poor positional allocation
    weak_positions = [pos for pos, data in positional_spending.items() if 'WEAK' in data['verdict'] or 'OVERPAID' in data['verdict']]
    if len(weak_positions) >= 2:
        problems.append(f"Weak at key positions: {', '.join(weak_positions)}")

    # Problem 3: Overall ROI
    if manager_roi > league_avg_roi * 1.15:
        problems.append(f"Paid {manager_roi:.3f} per point (league avg: {league_avg_roi:.3f})")

    # Build verdict statement
    if rank <= 3:
        verdict_tone = "Your draft was elite."
    elif rank <= len(all_teams_roi) // 2:
        verdict_tone = "Your draft was mediocre."
    else:
        verdict_tone = "Your draft was poor."

    the_verdict = {
        'rank': rank,
        'total_teams': len(all_teams_roi),
        'total_spent': total_spent,
        'total_points': round(total_points, 1),
        'roi': round(manager_roi, 3),
        'league_avg_roi': round(league_avg_roi, 3),
        'grade': grade,
        'summary': verdict_tone,
        'problems': problems
    }

    # Step 9: Generate "The Sentence" (tribunal's judgment and path forward)
    # The tribunal pronounces sentence based on your greatest crime
    if busts_with_context:
        biggest_bust = busts_with_context[0]
        biggest_bust_pos = biggest_bust['position']
        biggest_bust_cost = biggest_bust['cost']
        estimated_wins_lost = biggest_bust.get('estimated_wins_lost', 1)

        the_sentence = {
            'crime': f"Overpaying for {biggest_bust['player_name']}",
            'evidence': f"You paid ${biggest_bust_cost} for a {biggest_bust_pos} who delivered {biggest_bust['points']} points. {biggest_bust['why_hurt']}.",
            'damage': f"This reckless spending cost you approximately {estimated_wins_lost:.0f} win{'s' if estimated_wins_lost != 1 else ''}.",
            'punishment': f"You are sentenced to NEVER pay ${biggest_bust_cost}+ for a single {biggest_bust_pos} again.",
            'path_to_redemption': f"Spread your risk. Acquire 2-3 mid-tier {biggest_bust_pos}s at ${biggest_bust_cost//2}-${biggest_bust_cost//3} each instead of one expensive bust.",
            'expected_improvement': f"{estimated_wins_lost:.0f} fewer losses" if estimated_wins_lost >= 1 else "Improved draft stability"
        }
    elif weak_positions:
        weakest_pos = weak_positions[0]
        weak_spending = positional_spending[weakest_pos]['budget_pct']

        the_sentence = {
            'crime': f"Neglecting the {weakest_pos} position",
            'evidence': f"You allocated only {weak_spending:.0f}% of your budget to {weakest_pos}, leaving this position critically weak all season.",
            'damage': f"This structural flaw undermined your roster foundation.",
            'punishment': f"You are sentenced to prioritize {weakest_pos} in next year's draft.",
            'path_to_redemption': f"Allocate 20-30% of your budget to {weakest_pos}. Build strength at this position to avoid weekly struggles.",
            'expected_improvement': "1-2 wins with stronger positional foundation"
        }
    else:
        the_sentence = {
            'crime': "Failure to acquire surplus value",
            'evidence': f"You ranked #{rank} in draft efficiency. Your picks returned pedestrian value.",
            'damage': f"Mediocrity in the draft doomed your season before Week 1.",
            'punishment': f"You are sentenced to study the waiver wire—your draft cannot save you.",
            'path_to_redemption': "Target undervalued players in the middle rounds. Avoid paying full price for stars. Find value in the margins.",
            'expected_improvement': f"Move from #{rank} to top-5 draft ranking"
        }

    return {
        'manager_name': team['manager_name'],
        'draft_type': 'auction',
        'draft_roi': round(manager_roi, 2),
        'league_avg_roi': round(league_avg_roi, 2),
        'rank': rank,
        'grade': grade,
        'total_spent': total_spent,
        'total_points': round(total_points, 1),
        'the_verdict': the_verdict,
        'steals': steals_with_context[:3],  # Top 3
        'busts': busts_with_context[:3],    # Top 3
        'positional_spending': positional_spending,
        'the_sentence': the_sentence,
        'vor_analysis': {
            'total_vor': round(sum(p['vor'] for p in drafted_players_with_data), 1),
            'replacement_levels': replacement_levels,
            'top_vor_picks': sorted([
                {
                    'player_name': p['player_name'],
                    'position': p['position'],
                    'vor': round(p['vor'], 1),
                    'cost': p['cost']
                }
                for p in drafted_players_with_data if p['vor'] > 2
            ], key=lambda x: x['vor'], reverse=True)[:5]
        }
    }
