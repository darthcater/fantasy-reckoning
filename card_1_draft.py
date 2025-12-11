"""
Card 1: The Draft Tribunal
Calculate draft ROI, steals, busts, and positional spending

Supports both Auction and Snake drafts
"""


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


def calculate_card_1_draft(calc, team_key: str) -> dict:
    """
    Calculate Card 1: The Draft Tribunal metrics

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with draft analysis
    """
    team = calc.teams[team_key]
    draft_picks = calc.draft_by_team.get(team_key, [])

    if not draft_picks:
        return {
            'error': 'No draft data available',
            'manager_name': team['manager_name'],
            'draft_type': 'unavailable',
            'message': 'Draft analysis unavailable (offline draft, keeper league, or missing data)',
            'note': 'Card 1 cannot be generated without draft data',
            'grade': 'N/A',
            'rank': 0,
            'steals': [],
            'busts': []
        }

    # Check draft type and route to appropriate analysis
    if calc.draft_type == 'snake':
        return _calculate_snake_draft_analysis(calc, team_key, draft_picks)
    else:
        return _calculate_auction_draft_analysis(calc, team_key, draft_picks)


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
    Calculate draft ROI for AUCTION drafts

    Returns:
        Dict with auction draft analysis
    """
    # Get team info
    team = calc.teams[team_key]

    # Calculate total points scored by each drafted player
    player_season_points = {}
    for pick in draft_picks:
        player_id = str(pick['player_id'])
        total_points = sum(
            calc.player_points_by_week[player_id].values()
        )
        player_season_points[player_id] = total_points

    # Calculate Draft ROI ($/point)
    drafted_players_with_points = [
        {
            'player_id': pick['player_id'],
            'cost': pick['cost'],
            'points': player_season_points.get(str(pick['player_id']), 0),
            'per_point': pick['cost'] / player_season_points.get(str(pick['player_id']), 1) if player_season_points.get(str(pick['player_id']), 0) > 0 else 999
        }
        for pick in draft_picks
    ]

    total_spent = sum(pick['cost'] for pick in draft_picks)
    total_points = sum(p['points'] for p in drafted_players_with_points)

    manager_roi = total_spent / total_points if total_points > 0 else 999

    # Calculate league average ROI and build rankings
    all_teams_roi = []  # List of (team_key, roi) tuples
    for tk in calc.teams.keys():
        team_picks = calc.draft_by_team.get(tk, [])
        team_spent = sum(p['cost'] for p in team_picks)
        team_points = 0
        for p in team_picks:
            pid = str(p['player_id'])
            team_points += sum(calc.player_points_by_week[pid].values())

        if team_points > 0:
            roi = team_spent / team_points
            all_teams_roi.append((tk, roi))

    league_avg_roi = sum(roi for _, roi in all_teams_roi) / len(all_teams_roi) if all_teams_roi else 0

    # Rank this manager (lower ROI = better = lower rank number)
    all_teams_roi_sorted = sorted(all_teams_roi, key=lambda x: x[1])  # Sort by ROI ascending

    # Find this manager's rank
    rank = None
    for i, (tk, roi) in enumerate(all_teams_roi_sorted, start=1):
        if tk == team_key:
            rank = i
            break

    if rank is None:
        rank = len(all_teams_roi)

    # Calculate grade
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

    # Find steals (best $/point ratios)
    steals = sorted(drafted_players_with_points, key=lambda x: x['per_point'])[:3]

    # Find busts (worst $/point ratios where cost >= $20)
    expensive_picks = [p for p in drafted_players_with_points if p['cost'] >= 20]
    busts = sorted(expensive_picks, key=lambda x: x['per_point'], reverse=True)[:3]

    # TODO: Positional spending analysis
    # This requires knowing player positions, which we'll need to add

    return {
        'manager_name': team['manager_name'],
        'draft_type': 'auction',
        'draft_roi': round(manager_roi, 2),
        'league_avg_roi': round(league_avg_roi, 2),
        'rank': rank,
        'grade': grade,
        'total_spent': total_spent,
        'total_points': round(total_points, 1),
        'steals': [
            {
                'player_id': s['player_id'],
                'player_name': calc.player_names.get(str(s['player_id']), f"Player {s['player_id']}"),
                'cost': s['cost'],
                'points': round(s['points'], 1),
                'per_point': round(s['per_point'], 3)
            }
            for s in steals if s['points'] > 0
        ],
        'busts': [
            {
                'player_id': b['player_id'],
                'player_name': calc.player_names.get(str(b['player_id']), f"Player {b['player_id']}"),
                'cost': b['cost'],
                'points': round(b['points'], 1),
                'per_point': round(b['per_point'], 3)
            }
            for b in busts if b['cost'] >= 20
        ]
    }
