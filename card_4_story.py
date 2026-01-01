"""
Card 4: The Legend
The story of your season - skill versus luck

Win Attribution Analysis:
- True Skill Record: Your actual record minus luck
- Luck Factors: Schedule, Opponent Mistakes, Random
"""

from card_2_ledger import calculate_card_2_ledger


def calculate_card_4_story(calc, team_key: str, other_cards: dict = None) -> dict:
    """
    Calculate Card 4: The Legend - Win Attribution Analysis

    Separates your season into:
    - Skill (draft, lineups, waivers)
    - Luck (schedule, opponent mistakes, random)
    - True Skill Record (actual record minus luck)
    """

    if not other_cards:
        raise ValueError("Card 4 requires other cards to be calculated first")

    card_1 = other_cards.get('card_1_overview', {})
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_lineups', {})

    team = calc.teams[team_key]
    manager_name = team.get('manager_name', 'Unknown')

    # Get actual record from card_3
    actual_timeline = card_3.get('timelines', {}).get('actual', {})
    actual_wins = actual_timeline.get('wins', 0)
    actual_losses = actual_timeline.get('losses', 0)
    total_games = actual_wins + actual_losses

    # Baseline: 50% win rate (7-7 in 14-game season)
    baseline_wins = total_games / 2

    # ========================================
    # SKILL FACTORS
    # ========================================

    # 1. DRAFT SKILL
    num_teams = len(calc.teams)
    draft_rank = card_1.get('overall_rank_numeric', num_teams // 2)
    median_rank = (num_teams + 1) / 2
    draft_impact_wins = (median_rank - draft_rank) * 0.15

    # 2. LINEUP SKILL
    lineup_wins_lost = card_3.get('wins_left_on_table', {}).get('lineup_wins_lost', 0)
    lineup_impact_wins = -lineup_wins_lost  # Negative because you LOST these wins

    # 3. WAIVER SKILL
    waiver_points_started = card_2.get('waivers', {}).get('total_points_started', 0)

    # Calculate league average waiver points
    all_team_waiver_pts = []
    for tk in calc.teams.keys():
        tk_card_2 = calculate_card_2_ledger(calc, tk)
        tk_waiver_pts = tk_card_2.get('waivers', {}).get('total_points_started', 0)
        all_team_waiver_pts.append(tk_waiver_pts)

    league_avg_waiver_pts = sum(all_team_waiver_pts) / len(all_team_waiver_pts) if all_team_waiver_pts else 0
    waiver_points_diff = waiver_points_started - league_avg_waiver_pts
    waiver_impact_wins = (waiver_points_diff / 100) * 0.5

    total_skill_impact = draft_impact_wins + lineup_impact_wins + waiver_impact_wins

    # Build skill factors for output
    skill_factors = [
        {
            'factor': 'Draft',
            'impact': round(draft_impact_wins, 1),
            'category': 'skill'
        },
        {
            'factor': 'Lineups',
            'impact': round(lineup_impact_wins, 1),
            'category': 'skill'
        },
        {
            'factor': 'Waivers',
            'impact': round(waiver_impact_wins, 1),
            'category': 'skill'
        }
    ]

    # ========================================
    # LUCK FACTORS
    # ========================================

    regular_season_weeks = calc.get_regular_season_weeks()

    # 1. SCHEDULE LUCK
    expected_wins = 0
    schedule_luck_details = []

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        manager_score = calc.weekly_data[team_key][week_key].get('actual_points', 0)
        actual_opponent_score = calc.weekly_data[team_key][week_key].get('opponent_points', 0)
        result = calc.weekly_data[team_key][week_key].get('result', '')

        # Count how many teams this score would beat this week
        teams_beaten = 0
        for tk in calc.teams.keys():
            if tk == team_key:
                continue
            if week_key in calc.weekly_data.get(tk, {}):
                opponent_score = calc.weekly_data[tk][week_key].get('actual_points', 0)
                if manager_score > opponent_score:
                    teams_beaten += 1

        # Expected win probability = teams beaten / (total teams - 1)
        expected_wins += teams_beaten / (num_teams - 1)

        # Track significant luck moments (tough/weak opponents)
        actual_opp_teams_beaten = 0
        for tk in calc.teams.keys():
            if week_key in calc.weekly_data.get(tk, {}):
                other_score = calc.weekly_data[tk][week_key].get('actual_points', 0)
                if actual_opponent_score > other_score:
                    actual_opp_teams_beaten += 1

        # Track tough opponents (top 3 scorers) and weak opponents (bottom 3)
        if actual_opp_teams_beaten >= num_teams - 3:
            schedule_luck_details.append({
                'week': week,
                'type': 'tough_opponent',
                'opponent_score': round(actual_opponent_score, 1),
                'opponent_rank': actual_opp_teams_beaten + 1,
                'result': result
            })
        elif actual_opp_teams_beaten <= 2:
            schedule_luck_details.append({
                'week': week,
                'type': 'weak_opponent',
                'opponent_score': round(actual_opponent_score, 1),
                'opponent_rank': actual_opp_teams_beaten + 1,
                'result': result
            })

    schedule_luck_wins = actual_wins - expected_wins

    # Build schedule luck narrative
    tough_wins = [d for d in schedule_luck_details if d['type'] == 'tough_opponent' and d['result'] == 'W']
    tough_losses = [d for d in schedule_luck_details if d['type'] == 'tough_opponent' and d['result'] == 'L']
    weak_wins = [d for d in schedule_luck_details if d['type'] == 'weak_opponent' and d['result'] == 'W']
    weak_losses = [d for d in schedule_luck_details if d['type'] == 'weak_opponent' and d['result'] == 'L']

    narrative = []
    if weak_wins:
        narrative.append(f"Faced weak opponents in {len(weak_wins)} {'win' if len(weak_wins) == 1 else 'wins'}")
    if tough_losses:
        narrative.append(f"Faced top scorers in {len(tough_losses)} {'loss' if len(tough_losses) == 1 else 'losses'}")
    if weak_losses:
        narrative.append(f"Lost to weak opponents {len(weak_losses)} {'time' if len(weak_losses) == 1 else 'times'}")
    if tough_wins:
        narrative.append(f"Beat tough opponents {len(tough_wins)} {'time' if len(tough_wins) == 1 else 'times'}")

    # 2. OPPONENT MISTAKES
    opponent_mistake_wins = 0
    opponent_mistake_details = []

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        your_score = week_data.get('actual_points', 0)
        opponent_score = week_data.get('opponent_points', 0)
        result = week_data.get('result', '')

        if result != 'W':
            continue

        # Get opponent's optimal lineup
        opponent_key = week_data.get('opponent_id')
        if not opponent_key or opponent_key not in calc.weekly_data:
            continue

        if week_key not in calc.weekly_data[opponent_key]:
            continue

        opponent_week_data = calc.weekly_data[opponent_key][week_key]
        opponent_roster = opponent_week_data.get('roster', {})
        opponent_optimal = calc.calculate_optimal_lineup(opponent_roster, filter_injured=False)
        opponent_optimal_points = opponent_optimal['optimal_points']

        # If opponent's optimal lineup would have beaten you, you benefited from their mistake
        if opponent_optimal_points > your_score:
            opponent_mistake_wins += 1
            margin = your_score - opponent_score
            bench_left = opponent_optimal_points - opponent_score
            opponent_mistake_details.append({
                'week': week,
                'your_score': round(your_score, 1),
                'opponent_score': round(opponent_score, 1),
                'opponent_optimal': round(opponent_optimal_points, 1),
                'opponent_bench_left': round(bench_left, 1),
                'win_margin': round(margin, 1)
            })

    # Build opponent mistakes narrative
    opp_narrative = []
    for detail in opponent_mistake_details[:3]:  # Top 3
        opp_narrative.append(
            f"Week {detail['week']}: Won by {detail['win_margin']} pts, "
            f"opponent left {detail['opponent_bench_left']} on bench"
        )

    # 3. AGENT OF CHAOS
    # Find YOUR player with biggest game-deciding performance
    agent_of_chaos = None
    biggest_impact = 0

    # Calculate season averages for your players
    player_avgs = {}
    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue
        roster = calc.weekly_data[team_key][week_key].get('roster', {})
        for player in roster.get('starters', []):
            pos = player.get('selected_position', '')
            if pos in ['K', 'DEF', 'IR', 'BN']:
                continue
            pid = str(player.get('player_id', ''))
            pts = player.get('actual_points', 0)
            if pid not in player_avgs:
                player_avgs[pid] = {'name': player.get('player_name', 'Unknown'), 'points': []}
            player_avgs[pid]['points'].append(pts)

    for pid in player_avgs:
        pts_list = player_avgs[pid]['points']
        player_avgs[pid]['avg'] = sum(pts_list) / len(pts_list) if pts_list else 0

    # Collect your performances with game context
    player_performances = []  # [(player_id, player_name, week, points, result, margin)]

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        result = week_data.get('result', '')
        your_score = week_data.get('actual_points', 0)
        opp_score = week_data.get('opponent_points', 0)
        margin = abs(your_score - opp_score)

        # Your starters only
        roster = week_data.get('roster', {})
        for player in roster.get('starters', []):
            pos = player.get('selected_position', '')
            if pos in ['K', 'DEF', 'IR', 'BN']:
                continue
            player_performances.append((
                str(player.get('player_id', '')),
                player.get('player_name', 'Unknown'),
                week, player.get('actual_points', 0),
                result, margin
            ))

    # Find biggest game-deciding deviation
    # Priority 1: BOOM + WIN (hero) or BUST + LOSS (villain)
    # Fallback: BUST + WIN (nearly cost you)
    fallback_agent = None
    fallback_impact = 0

    for pid, pname, week, pts, result, margin in player_performances:
        if pid not in player_avgs or len(player_avgs[pid]['points']) < 2:
            continue

        avg = player_avgs[pid]['avg']
        deviation = pts - avg

        # Primary: boom→win or bust→loss (decisive moments)
        if result == 'W' and deviation > 0:
            # BOOM in a WIN - hero moment
            if deviation > margin:
                win_impact = 'won you the game'
            else:
                win_impact = 'sealed victory'
        elif result == 'L' and deviation < 0:
            # BUST in a LOSS - villain moment
            if abs(deviation) > margin:
                win_impact = 'cost you the game'
            else:
                win_impact = 'contributed to the loss'
        elif result == 'W' and deviation < 0:
            # BUST in a WIN - fallback option (nearly cost you)
            fallback_score = abs(deviation)
            if margin < 15:
                fallback_score *= 1.5
            if fallback_score > fallback_impact:
                fallback_impact = fallback_score
                fallback_agent = {
                    'player_name': pname,
                    'week': week,
                    'points': round(pts, 1),
                    'season_avg': round(avg, 1),
                    'deviation': round(deviation, 1),
                    'type': 'bust',
                    'is_yours': True,
                    'result': result,
                    'win_impact': 'nearly cost you'
                }
            continue
        else:
            # Skip: boom in loss - not meaningful
            continue

        # Weight by deviation and close games
        impact_score = abs(deviation)
        if margin < 15:
            impact_score *= 1.5  # Bonus for close games

        if impact_score > biggest_impact:
            biggest_impact = impact_score
            agent_of_chaos = {
                'player_name': pname,
                'week': week,
                'points': round(pts, 1),
                'season_avg': round(avg, 1),
                'deviation': round(deviation, 1),
                'type': 'boom' if deviation > 0 else 'bust',
                'is_yours': True,
                'result': result,
                'win_impact': win_impact
            }

    # Use fallback if no primary agent found
    if agent_of_chaos is None and fallback_agent is not None:
        agent_of_chaos = fallback_agent

    # Total luck impact = schedule luck only
    # (Opponent mistakes shown as fun fact but not subtracted - avoids double-counting)
    total_luck_impact = schedule_luck_wins

    # Build luck factors for output
    # Only show detailed narrative if luck is meaningful (rounds to non-zero)
    schedule_luck_rounded = round(schedule_luck_wins)
    if schedule_luck_rounded == 0:
        schedule_narrative = ['Average schedule difficulty']
    else:
        schedule_narrative = narrative if narrative else ['Average schedule difficulty']

    luck_factors = [
        {
            'factor': 'Schedule Luck',
            'impact': round(schedule_luck_wins, 1),
            'category': 'luck',
            'note': 'Faced easy/hard opponents at right/wrong times',
            'details': schedule_luck_details,
            'narrative': schedule_narrative
        },
        {
            'factor': 'Opponent Mistakes',
            'impact': opponent_mistake_wins,
            'category': 'luck',
            'note': 'Won games where opponent had better lineup available',
            'details': opponent_mistake_details,
            'narrative': opp_narrative if opp_narrative else ['Opponents set optimal lineups against you']
        }
    ]

    # ========================================
    # TRUE SKILL RECORD
    # ========================================

    # True skill = Actual record minus luck
    true_skill_wins = actual_wins - total_luck_impact
    true_skill_losses = total_games - true_skill_wins

    return {
        'manager_name': manager_name,
        'actual_record': f"{actual_wins}-{actual_losses}",
        'win_attribution': {
            'baseline_wins': round(baseline_wins, 1),
            'skill_factors': skill_factors,
            'luck_factors': luck_factors,
            'total_skill_impact': round(total_skill_impact, 1),
            'total_luck_impact': round(total_luck_impact, 1),
            'true_skill_record': f"{int(round(true_skill_wins))}-{int(round(true_skill_losses))}",
            'breakdown': {
                'draft': round(draft_impact_wins, 1),
                'lineups': round(lineup_impact_wins, 1),
                'waivers': round(waiver_impact_wins, 1),
                'schedule_luck': round(schedule_luck_wins, 1)
            },
            'explanation': f"True skill {int(round(true_skill_wins))}-{int(round(true_skill_losses))} = Actual {actual_wins}-{actual_losses} minus {round(total_luck_impact, 1)} luck",
            'agent_of_chaos': agent_of_chaos
        }
    }
