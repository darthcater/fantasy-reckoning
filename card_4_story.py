"""
Card 4: Story
Win attribution, skill vs luck, and playoff analysis.

Evaluates team performance and outcomes:
- Win attribution (draft impact, lineup decisions, schedule luck)
- True strength (all-play record vs actual record)
- Skill vs luck separation
- Playoff results and comparison
"""
from league_metrics import (
    calculate_league_ranking,
    calculate_playoff_comparison,
    get_playoff_teams,
    get_grade_from_percentile
)


def calculate_all_play_record(calc, team_key: str) -> dict:
    """
    Calculate how team would fare against ALL opponents every week.
    This is the best measure of true team strength (removes schedule luck).

    Returns:
        dict with all-play record, win %, league ranking
    """
    num_teams = len(calc.teams)
    regular_season_weeks = calc.get_regular_season_weeks()
    current_week = calc.league['current_week']

    all_play_wins = 0
    all_play_losses = 0
    weekly_records = []

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        manager_score = calc.weekly_data[team_key][week_key].get('actual_points', 0)

        # Compare to ALL other teams this week
        week_wins = 0
        week_losses = 0

        for tk in calc.teams.keys():
            if tk == team_key:
                continue  # Don't play yourself

            if week_key in calc.weekly_data.get(tk, {}):
                opponent_score = calc.weekly_data[tk][week_key].get('actual_points', 0)

                if manager_score > opponent_score:
                    week_wins += 1
                    all_play_wins += 1
                elif manager_score < opponent_score:
                    week_losses += 1
                    all_play_losses += 1
                # Ties are rare, not counted

        weekly_records.append({
            'week': week,
            'wins': week_wins,
            'losses': week_losses,
            'score': round(manager_score, 1)
        })

    total_games = all_play_wins + all_play_losses
    all_play_win_pct = (all_play_wins / total_games * 100) if total_games > 0 else 0

    # Calculate league rankings for all-play %
    all_team_all_play = {}
    for tk in calc.teams.keys():
        tk_all_play_wins = 0
        tk_all_play_losses = 0

        for week in regular_season_weeks:
            week_key = f'week_{week}'
            if week_key not in calc.weekly_data.get(tk, {}):
                continue

            tk_score = calc.weekly_data[tk][week_key].get('actual_points', 0)

            for opponent_tk in calc.teams.keys():
                if opponent_tk == tk:
                    continue
                if week_key in calc.weekly_data.get(opponent_tk, {}):
                    opp_score = calc.weekly_data[opponent_tk][week_key].get('actual_points', 0)
                    if tk_score > opp_score:
                        tk_all_play_wins += 1
                    elif tk_score < opp_score:
                        tk_all_play_losses += 1

        tk_total = tk_all_play_wins + tk_all_play_losses
        all_team_all_play[tk] = (tk_all_play_wins / tk_total * 100) if tk_total > 0 else 0

    # Get league ranking
    ranking_info = calculate_league_ranking(all_team_all_play, team_key, reverse=True)

    # Calculate expected actual record based on all-play %
    weeks_played = len([w for w in regular_season_weeks if f'week_{w}' in calc.weekly_data.get(team_key, {})])
    expected_actual_wins = (all_play_win_pct / 100) * weeks_played

    # Get actual wins from calculated stats (not stale team summary)
    calculated_stats = calc.calculate_team_stats_from_weekly_data(team_key)
    actual_wins = calculated_stats['wins']
    schedule_luck = actual_wins - expected_actual_wins

    # Determine luck category
    if schedule_luck >= 2:
        luck_type = "Very Lucky"
    elif schedule_luck >= 1:
        luck_type = "Slightly Lucky"
    elif schedule_luck <= -2:
        luck_type = "Very Unlucky"
    elif schedule_luck <= -1:
        luck_type = "Slightly Unlucky"
    else:
        luck_type = "Neutral"

    return {
        'all_play_wins': all_play_wins,
        'all_play_losses': all_play_losses,
        'all_play_record': f"{all_play_wins}-{all_play_losses}",
        'all_play_win_pct': round(all_play_win_pct, 1),
        'all_play_per_week_avg': f"{all_play_wins/weeks_played:.1f}-{all_play_losses/weeks_played:.1f}" if weeks_played > 0 else "0-0",
        'league_rank': ranking_info['league_rank'],
        'league_rank_numeric': ranking_info['league_rank_numeric'],
        'percentile': ranking_info['percentile'],
        'league_average': ranking_info['league_average'],
        'gap_to_average': ranking_info['gap_to_average'],
        'expected_actual_wins': round(expected_actual_wins, 1),
        'expected_actual_record': f"{int(round(expected_actual_wins))}-{weeks_played - int(round(expected_actual_wins))}",
        'schedule_luck': round(schedule_luck, 1),
        'luck_type': luck_type,
        'weekly_records': weekly_records,
        'grade': get_grade_from_percentile(ranking_info['percentile'])
    }


def calculate_card_4_story(calc, team_key: str, other_cards: dict = None) -> dict:
    """
    Calculate Card 4: Story - Win attribution and season outcomes

    Analyzes how wins were earned and season results:
    - Win attribution (draft impact, lineup decisions, schedule luck)
    - All-play record (true strength vs schedule luck)
    - Skill vs luck separation
    - Playoff results and comparison

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key
        other_cards: Dict containing other cards' data (optional)

    Returns:
        Dict with performance analysis
    """
    # Handle case where other_cards not yet available
    if other_cards is None:
        other_cards = {}
    team = calc.teams[team_key]
    current_week = calc.league['current_week']

    # Get data from other cards (don't call recursively if not provided)
    # FIX: Avoid infinite recursion by not calling cards if not in other_cards
    card_1 = other_cards.get('card_1_draft', other_cards.get('card_1_reckoning', {}))
    card_2 = other_cards.get('card_2_identity', other_cards.get('card_2_roster', {}))
    card_3 = other_cards.get('card_3_inflection', other_cards.get('card_3_decisions', {}))
    card_4 = other_cards.get('card_4_ecosystem', {})  # FIX: Don't call self!

    # CALCULATE ALL-PLAY RECORD (PRIMARY METRIC FOR CARD 5)
    all_play_data = calculate_all_play_record(calc, team_key)

    # STEP 1: Win Attribution Analysis (Data-Driven Approach)
    # Use regression to 7-7 baseline with actual correlations
    # Separate SKILL (repeatable) from LUCK (won't repeat)

    # Get actual record - timelines data is in card_3
    if card_3 and 'timelines' in card_3:
        actual_record = card_3['timelines']['actual']
        actual_wins = int(actual_record['wins'])
        actual_losses = int(actual_record['losses'])
        optimal_lineup_record = card_3['timelines']['optimal_lineup']
        optimal_lineup_wins = int(optimal_lineup_record['wins'])
    else:
        # Fallback: calculate directly from weekly data
        team_stats = calc.calculate_team_stats_from_weekly_data(team_key)
        actual_wins = team_stats['wins']
        actual_losses = team_stats['losses']
        optimal_lineup_wins = actual_wins  # Estimate
        actual_record = {
            'wins': actual_wins,
            'losses': actual_losses,
            'record': f"{actual_wins}-{actual_losses}"
        }

    total_games = actual_wins + actual_losses

    # Baseline: 50% win rate (7-7 in 14-game season)
    baseline_wins = total_games / 2

    # ========================================
    # SKILL FACTORS (Repeatable Performance)
    # ========================================

    # 1. DRAFT SKILL: Based on VOR rank vs league median
    num_teams = len(calc.teams)
    draft_rank = card_1.get('rank', num_teams // 2)  # Default to median if not available
    median_rank = (num_teams + 1) / 2

    # Correlation: Each rank above/below median = ~0.15 wins
    draft_impact_wins = (median_rank - draft_rank) * 0.15

    # 2. LINEUP SKILL: Based on efficiency percentage
    # Correlation: Each 1% efficiency = ~0.08 wins
    manager_efficiency = card_2.get('efficiency', {}).get('lineup_efficiency_pct', 75.0)  # Default estimate
    baseline_efficiency = 50.0  # 50% is median

    lineup_impact_wins = (manager_efficiency - baseline_efficiency) * 0.08

    # Alternative: Use preventable losses directly (more accurate)
    preventable_losses = card_3.get('insights', {}).get('preventable_losses', 0)
    # If you fixed lineup mistakes, you'd gain these wins
    lineup_potential_wins = preventable_losses

    # Use whichever is more conservative
    lineup_impact_wins = min(lineup_impact_wins, -preventable_losses)

    # 3. WAIVER SKILL: Based on opportunity cost
    # Get waiver points added vs league average
    if 'waiver_efficiency' in card_4:
        waiver_points_added = card_4['waiver_efficiency'].get('points_added', 0)

        # Calculate league average waiver points added
        # FIX: Don't recursively calculate Card 4 for all teams - causes infinite loop
        # Use a simpler estimate based on transaction volume instead
        league_waiver_totals = []
        for tk in calc.teams.keys():
            tk_transactions = len(calc.transactions_by_team.get(tk, []))
            # Rough estimate: avg 10 points per transaction
            estimated_waiver_pts = tk_transactions * 10
            league_waiver_totals.append(estimated_waiver_pts)

        league_avg_waiver_pts = sum(league_waiver_totals) / len(league_waiver_totals) if league_waiver_totals else 0

        # Correlation: Each 100 pts above league avg = ~0.5 wins
        waiver_points_diff = waiver_points_added - league_avg_waiver_pts
        waiver_impact_wins = (waiver_points_diff / 100) * 0.5
    else:
        waiver_impact_wins = 0

    # Total SKILL impact (sum of all skill factors)
    total_skill_impact = draft_impact_wins + lineup_impact_wins + waiver_impact_wins

    # ========================================
    # LUCK FACTORS (Won't Repeat Next Year)
    # ========================================

    # 1. SCHEDULE LUCK: Actual wins vs expected wins based on points-for
    # Calculate expected wins (how many teams would you beat each week on average?)
    regular_season_weeks = calc.get_regular_season_weeks()
    expected_wins = 0

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        manager_score = calc.weekly_data[team_key][week_key].get('actual_points', 0)

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

    schedule_luck_wins = actual_wins - expected_wins

    # 2. OPPONENT MISTAKES: Wins gained from opponent lineup errors
    # Count weeks where opponent left points on bench that would have beaten you
    opponent_mistake_wins = 0

    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        manager_score = week_data.get('actual_points', 0)
        opponent_id = week_data.get('opponent_id', '')
        opponent_score = week_data.get('opponent_points', 0)

        # Did manager win?
        manager_won = manager_score > opponent_score

        if manager_won and opponent_id:
            # Check if opponent had better lineup available
            if week_key in calc.weekly_data.get(opponent_id, {}):
                opp_week_data = calc.weekly_data[opponent_id][week_key]
                opp_roster = opp_week_data.get('roster', {})

                # Calculate opponent's optimal lineup
                opp_optimal = calc.calculate_optimal_lineup(opp_roster, filter_injured=False)
                opp_optimal_pts = opp_optimal['optimal_points']

                # If opponent's optimal lineup would have beaten manager, this is a lucky win
                if opp_optimal_pts > manager_score:
                    opponent_mistake_wins += 1

    # 3. RANDOM LUCK: Residual (everything else not explained by skill or known luck factors)
    # This includes: injury timing, player boom/bust weeks, etc.
    explained_wins = baseline_wins + total_skill_impact + schedule_luck_wins + opponent_mistake_wins
    random_luck_wins = actual_wins - explained_wins

    # Total LUCK impact
    total_luck_impact = schedule_luck_wins + opponent_mistake_wins + random_luck_wins

    # Injury impact (moved to luck category - injury timing is random)
    injury_impact_wins = 0  # Placeholder - would need injury data

    # STEP 2: Identify "The One Thing" to fix
    # Focus on SKILL factors only (luck can't be fixed!)

    # FIX: Get draft grade from card_2 (has draft data) not card_1 (not generated yet!)
    draft_grade = card_2.get('draft', {}).get('grade', 'C')

    skill_factors = [
        {
            'factor': 'Draft',
            'impact': draft_impact_wins,
            'grade': draft_grade,
            'category': 'skill'
        },
        {
            'factor': 'Lineups',
            'impact': lineup_impact_wins,
            'grade': card_3.get('skill_grades', {}).get('lineups', 'C'),  # FIX: Use card_3 not card_2
            'category': 'skill',
            'potential_gains': preventable_losses  # How many wins you COULD gain
        },
        {
            'factor': 'Waivers',
            'impact': waiver_impact_wins,
            'grade': card_2.get('waivers', {}).get('efficiency_rate', 50) / 20,  # FIX: Estimate grade from efficiency
            'category': 'skill'
        }
    ]

    luck_factors = [
        {
            'factor': 'Schedule Luck',
            'impact': schedule_luck_wins,
            'category': 'luck',
            'note': 'Faced easy/hard opponents at right/wrong times'
        },
        {
            'factor': 'Opponent Mistakes',
            'impact': opponent_mistake_wins,
            'category': 'luck',
            'note': 'Won games where opponent had better lineup available'
        },
        {
            'factor': 'Random Luck',
            'impact': random_luck_wins,
            'category': 'luck',
            'note': 'Injuries, player boom/bust timing, etc.'
        }
    ]

    all_impact_factors = skill_factors + luck_factors

    # Sort SKILL factors by impact (most negative first)
    skill_factors_sorted = sorted(skill_factors, key=lambda x: x['impact'])

    # The One Thing = worst skill factor (not luck - you can't fix luck!)
    the_one_thing = skill_factors_sorted[0]['factor']
    the_one_thing_impact = skill_factors_sorted[0]['impact']

    # ROI Analysis: Which improvement gives best return for effort?
    # Effort scores: Draft (high prep time), Lineups (medium - weekly), Waivers (high - constant monitoring)
    effort_map = {'Draft': 8, 'Lineups': 4, 'Waivers': 7}  # 1-10 scale

    for factor in skill_factors:
        factor_name = factor['factor']
        potential_improvement = abs(min(0, factor['impact']))  # How much you're losing
        if 'potential_gains' in factor:
            potential_improvement = max(potential_improvement, factor['potential_gains'])

        effort = effort_map.get(factor_name, 5)
        roi = potential_improvement / effort if effort > 0 else 0
        factor['roi'] = round(roi, 2)
        factor['effort_score'] = effort
        factor['potential_improvement'] = round(potential_improvement, 1)

    # Sort by ROI (highest ROI = best bang for buck)
    skill_factors_by_roi = sorted([f for f in skill_factors if f.get('potential_improvement', 0) > 0],
                                   key=lambda x: x.get('roi', 0),
                                   reverse=True)

    best_roi_factor = skill_factors_by_roi[0] if skill_factors_by_roi else skill_factors_sorted[0]

    # STEP 3: Generate improvement checklist

    improvement_checklist = []

    # Add items based on weaknesses
    if draft_grade in ['D', 'F']:
        improvement_checklist.append({
            'category': 'Draft',
            'priority': 'High',
            'action': 'Study player values and avoid reaching on stars',
            'expected_impact': '+2 wins'
        })

    # FIX: Updated to use card_3 for efficiency/archetype (new structure)
    if card_3.get('skill_grades', {}).get('lineups', 'C') in ['D', 'F']:
        bench_pts = card_3.get('efficiency', {}).get('total_bench_points_left', 0)
        improvement_checklist.append({
            'category': 'Lineups',
            'priority': 'High',
            'action': f"Set optimal lineups - you left {bench_pts:.1f} points on bench",
            'expected_impact': f"+{max(0, optimal_lineup_wins - actual_wins)} wins"
        })

    if card_2.get('waivers', {}).get('efficiency_rate', 50) < 40:
        improvement_checklist.append({
            'category': 'Waivers',
            'priority': 'Medium',
            'action': 'Target high-upside free agents earlier in the season',
            'expected_impact': '+1-2 wins'
        })

    archetype_type = card_3.get('archetype', {}).get('type', '')
    if archetype_type == 'Believer':
        trans_per_week = card_3.get('archetype', {}).get('transactions_per_week', 0)
        improvement_checklist.append({
            'category': 'Activity',
            'priority': 'Low',
            'action': f'Be more active on waivers - you only made {trans_per_week:.1f} transactions/week',
            'expected_impact': '+1 win'
        })

    if archetype_type == 'Tinkerer':
        trans_per_week = card_3.get('archetype', {}).get('transactions_per_week', 0)
        improvement_checklist.append({
            'category': 'Activity',
            'priority': 'Low',
            'action': f'Trust your roster more - you made {trans_per_week:.1f} transactions/week',
            'expected_impact': '+0 wins (save time)'
        })

    # Add inflection point lessons
    card_3_preventable = card_3.get('insights', {}).get('preventable_losses', 0)
    if card_3_preventable > 0:
        improvement_checklist.append({
            'category': 'Inflection Points',
            'priority': 'High',
            'action': f"Avoid {card_3_preventable} preventable lineup mistakes",
            'expected_impact': f"+{card_3_preventable} wins"
        })

    # STEP 4: Project next season record (WITH LUCK REGRESSION!)
    # Formula: 2026 Wins = Baseline + Current Skill + Skill Improvements - Luck Regression

    # Your TRUE skill level (what's repeatable)
    true_skill_wins = baseline_wins + total_skill_impact

    # SCENARIO 1: If you change nothing
    # Luck regresses to 0 (mean), so you lose all your lucky wins
    projected_wins_no_change = baseline_wins + total_skill_impact  # Luck → 0

    # SCENARIO 2: If you fix your biggest weakness (The One Thing)
    biggest_weakness_gain = abs(min(0, the_one_thing_impact))
    if the_one_thing == 'Lineups' and preventable_losses > 0:
        biggest_weakness_gain = preventable_losses  # Use actual mistakes count

    projected_wins_fix_one_thing = projected_wins_no_change + biggest_weakness_gain

    # SCENARIO 3: If you fix ALL skill weaknesses (improvement checklist)
    total_skill_improvements = 0
    for factor in skill_factors:
        potential = factor.get('potential_improvement', 0)
        total_skill_improvements += potential

    projected_wins_fix_all = projected_wins_no_change + total_skill_improvements

    # Cap at total games
    projected_wins_no_change = max(0, min(total_games, round(projected_wins_no_change)))
    projected_wins_fix_one_thing = max(0, min(total_games, round(projected_wins_fix_one_thing)))
    projected_wins_fix_all = max(0, min(total_games, round(projected_wins_fix_all)))

    # Default projection: Assume they fix The One Thing (moderate optimism)
    projected_wins = projected_wins_fix_one_thing
    projected_record = f"{projected_wins}-{total_games - projected_wins}"

    # Calculate what's needed to maintain current record (if luck was positive)
    wins_needed_to_maintain = 0
    if total_luck_impact > 0:
        # You were lucky! To maintain current record, you need to improve skill to offset luck loss
        wins_needed_to_maintain = total_luck_impact

    # STEP 5: Calculate playoff teams efficiency benchmark

    # Get all teams with their wins and lineup efficiency
    all_teams_efficiency = []
    for tk in calc.teams.keys():
        # Get card_3 for efficiency and timelines data
        team_card_3 = calc.calculate_card_3(tk)
        team_wins = team_card_3.get('timelines', {}).get('actual', {}).get('wins', 0)
        team_efficiency = team_card_3.get('efficiency', {}).get('lineup_efficiency_pct', 75.0)
        all_teams_efficiency.append({
            'team_key': tk,
            'wins': team_wins,
            'efficiency': team_efficiency
        })

    # Sort by wins to identify playoff teams (top 6)
    all_teams_efficiency.sort(key=lambda x: x['wins'], reverse=True)
    playoff_teams = all_teams_efficiency[:6]

    # Calculate playoff teams average efficiency
    playoff_avg_efficiency = sum(t['efficiency'] for t in playoff_teams) / len(playoff_teams) if playoff_teams else 0

    # Get this manager's efficiency
    manager_efficiency = card_2.get('efficiency', {}).get('lineup_efficiency_pct', 75.0)  # Default estimate
    efficiency_gap = playoff_avg_efficiency - manager_efficiency

    # STEP 6: Killer weeks and buzzsaw analysis
    killer_weeks = []
    buzzsaw_weeks = []
    regular_season_weeks = calc.get_regular_season_weeks()

    for week in regular_season_weeks:
        week_key = f'week_{week}'

        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        manager_points = week_data.get('actual_points', 0)
        opponent_points = week_data.get('opponent_points', 0)
        manager_won = manager_points > opponent_points

        # Get all teams' scores for this week
        all_scores = []
        for tk in calc.teams.keys():
            if week_key in calc.weekly_data.get(tk, {}):
                team_week = calc.weekly_data[tk][week_key]
                all_scores.append({
                    'team_key': tk,
                    'team_name': calc.teams[tk].get('manager_name', 'Unknown'),
                    'points': team_week.get('actual_points', 0)
                })

        # Sort to get rankings
        all_scores.sort(key=lambda x: x['points'], reverse=True)

        # Find manager's rank
        manager_rank = next((i + 1 for i, s in enumerate(all_scores) if s['team_key'] == team_key), None)

        # Killer week: would have beaten everyone
        if manager_rank == 1:
            killer_weeks.append({
                'week': week,
                'points': round(manager_points, 1),
                'second_place_points': round(all_scores[1]['points'], 1) if len(all_scores) > 1 else 0,
                'margin': round(manager_points - all_scores[1]['points'], 1) if len(all_scores) > 1 else 0
            })

        # Buzzsaw week: top 3 score but still lost
        if manager_rank and manager_rank <= 3 and not manager_won:
            opponent_name = calc.teams.get(week_data.get('opponent_id', ''), {}).get('manager_name', 'Unknown')
            opponent_rank = next((i + 1 for i, s in enumerate(all_scores) if s['points'] == opponent_points), None)

            buzzsaw_weeks.append({
                'week': week,
                'your_points': round(manager_points, 1),
                'your_rank': manager_rank,
                'opponent_points': round(opponent_points, 1),
                'opponent_rank': opponent_rank,
                'opponent_name': opponent_name,
                'margin': round(opponent_points - manager_points, 1)
            })

    # STEP 7: Final summary

    return {
        'manager_name': team['manager_name'],
        'actual_record': {
            'wins': actual_wins,
            'losses': actual_losses,
            'record': actual_record['record']
        },
        'all_play_record': all_play_data,  # PRIMARY METRIC - True team strength
        'win_attribution': {
            # NEW: Separated skill from luck
            'baseline_wins': round(baseline_wins, 1),
            'skill_factors': skill_factors,  # Draft, Lineups, Waivers
            'luck_factors': luck_factors,  # Schedule, Opponent Mistakes, Random
            'total_skill_impact': round(total_skill_impact, 1),
            'total_luck_impact': round(total_luck_impact, 1),
            'true_skill_record': f"{int(round(baseline_wins + total_skill_impact))}-{total_games - int(round(baseline_wins + total_skill_impact))}",
            'breakdown': {
                'draft': round(draft_impact_wins, 1),
                'lineups': round(lineup_impact_wins, 1),
                'waivers': round(waiver_impact_wins, 1),
                'schedule_luck': round(schedule_luck_wins, 1),
                'opponent_mistakes': round(opponent_mistake_wins, 1),
                'random_luck': round(random_luck_wins, 1)
            },
            'explanation': f"{actual_wins}-{actual_losses} = {round(baseline_wins, 1)} baseline + {round(total_skill_impact, 1)} skill + {round(total_luck_impact, 1)} luck"
        },
        'the_one_thing': {
            'factor': the_one_thing,
            'current_grade': skill_factors_sorted[0]['grade'],
            'impact': round(the_one_thing_impact, 1),
            'diagnosis': f"Your {the_one_thing.lower()} was the biggest drag on your season",
            'best_roi_factor': best_roi_factor['factor'],
            'best_roi_value': best_roi_factor.get('roi', 0),
            'note': f"{best_roi_factor['factor']} gives best return on effort invested"
        },
        'improvement_checklist': improvement_checklist,
        'projected_2026_record': {
            # NEW: Multiple scenarios with luck regression
            'scenarios': {
                'no_change': {
                    'record': f"{projected_wins_no_change}-{total_games - projected_wins_no_change}",
                    'wins': projected_wins_no_change,
                    'note': 'If you change nothing (luck regresses to mean)'
                },
                'fix_one_thing': {
                    'record': f"{projected_wins_fix_one_thing}-{total_games - projected_wins_fix_one_thing}",
                    'wins': projected_wins_fix_one_thing,
                    'note': f"If you fix {the_one_thing} (recommended)"
                },
                'fix_all_weaknesses': {
                    'record': f"{projected_wins_fix_all}-{total_games - projected_wins_fix_all}",
                    'wins': projected_wins_fix_all,
                    'note': 'If you fix all skill weaknesses (optimistic)'
                }
            },
            'record': projected_record,  # Default (fix one thing)
            'wins': projected_wins,
            'improvement': projected_wins - actual_wins,
            'wins_needed_to_maintain': wins_needed_to_maintain,
            'reality_check': f"You were +{round(total_luck_impact, 1)} lucky wins this year. That won't repeat. To maintain {actual_wins}-{actual_losses}, you need +{wins_needed_to_maintain} skill improvement." if total_luck_impact > 1 else "Your record reflects your skill level."
        },
        'insights': {
            'biggest_opportunity': skill_factors_by_roi[0] if skill_factors_by_roi else None,
            'total_checklist_items': len(improvement_checklist),
            'high_priority_items': len([i for i in improvement_checklist if i['priority'] == 'High']),
            'luck_dependent': total_luck_impact > 2,  # Record is luck-dependent if >2 lucky wins
            'skill_baseline': f"{int(round(baseline_wins + total_skill_impact))}-{total_games - int(round(baseline_wins + total_skill_impact))}"
        },
        'playoff_benchmark': {
            'playoff_teams_avg_efficiency': round(playoff_avg_efficiency, 1),
            'your_efficiency': round(manager_efficiency, 1),
            'efficiency_gap': round(efficiency_gap, 1),
            'note': 'Playoff teams (top 6) averaged this lineup efficiency'
        },
        'memorable_weeks': {
            'killer_weeks': killer_weeks,
            'killer_weeks_count': len(killer_weeks),
            'buzzsaw_weeks': buzzsaw_weeks,
            'buzzsaw_weeks_count': len(buzzsaw_weeks),
            'note': 'Killer weeks: beat everyone. Buzzsaw weeks: top-3 score but still lost to a titan.'
        }
    }
