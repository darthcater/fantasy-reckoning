"""
Card V: The Legacy
Season narrative, achievements, lessons learned, and final reflections
"""

from datetime import datetime
from league_metrics import (
    calculate_league_ranking,
    get_grade_from_percentile,
    get_playoff_teams
)
from achievements import evaluate_manager_achievements


def calculate_card_5_legacy(calc, team_key: str, other_cards: dict = None) -> dict:
    """
    Calculate Card 5: The Legacy - Season narrative and reflections

    Synthesizes the entire season into a narrative arc with:
    - Season story (beginning, middle, end)
    - Key achievements and milestones
    - Defining moments
    - Lessons learned
    - Manager archetype and legacy

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key
        other_cards: Dict containing other card results for synthesis

    Returns:
        Dict with season narrative and legacy analysis
    """
    if other_cards is None:
        other_cards = {}

    team = calc.teams[team_key]
    manager_name = team['manager_name']
    team_name = team['team_name']
    current_week = calc.league['current_week']
    regular_season_weeks = calc.get_regular_season_weeks()

    # Get data from other cards
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_campaign', {})
    card_4 = other_cards.get('card_4_design', {})

    # Calculate season record
    team_stats = calc.calculate_team_stats_from_weekly_data(team_key)
    wins = team_stats['wins']
    losses = team_stats['losses']
    ties = team_stats['ties']
    points_for = team_stats['points_for']
    points_against = team_stats['points_against']

    # Determine playoff status
    playoff_teams = get_playoff_teams(calc)
    made_playoffs = team_key in playoff_teams

    # ====================================================================================
    # SEASON ARC: The Three Acts
    # ====================================================================================

    # Act 1: The Beginning (Weeks 1-4)
    early_weeks = list(regular_season_weeks)[:4]
    early_wins = 0
    early_points = 0.0
    for week in early_weeks:
        week_key = f'week_{week}'
        if week_key in calc.weekly_data.get(team_key, {}):
            week_data = calc.weekly_data[team_key][week_key]
            early_points += week_data.get('actual_points', 0)
            if week_data.get('actual_points', 0) > week_data.get('opponent_points', 0):
                early_wins += 1

    # Act 2: The Middle (Weeks 5-10)
    mid_weeks = list(regular_season_weeks)[4:10]
    mid_wins = 0
    mid_points = 0.0
    for week in mid_weeks:
        week_key = f'week_{week}'
        if week_key in calc.weekly_data.get(team_key, {}):
            week_data = calc.weekly_data[team_key][week_key]
            mid_points += week_data.get('actual_points', 0)
            if week_data.get('actual_points', 0) > week_data.get('opponent_points', 0):
                mid_wins += 1

    # Act 3: The End (Weeks 11-14)
    late_weeks = list(regular_season_weeks)[10:]
    late_wins = 0
    late_points = 0.0
    for week in late_weeks:
        week_key = f'week_{week}'
        if week_key in calc.weekly_data.get(team_key, {}):
            week_data = calc.weekly_data[team_key][week_key]
            late_points += week_data.get('actual_points', 0)
            if week_data.get('actual_points', 0) > week_data.get('opponent_points', 0):
                late_wins += 1

    # Determine season arc narrative
    if early_wins >= 3 and late_wins >= 2:
        arc_type = "The Champion's Journey"
        arc_description = f"You started strong ({early_wins}-{len(early_weeks)-early_wins}) and finished stronger. This was a season of dominance."
    elif early_wins <= 1 and late_wins >= 3:
        arc_type = "The Phoenix Rising"
        arc_description = f"You started in the ashes ({early_wins}-{len(early_weeks)-early_wins}) but rose to glory. A remarkable comeback story."
    elif early_wins >= 3 and late_wins <= 1:
        arc_type = "The Fallen Star"
        arc_description = f"You blazed bright early ({early_wins}-{len(early_weeks)-early_wins}) but faded when it mattered. A cautionary tale."
    elif mid_wins >= 4:
        arc_type = "The Consistent Competitor"
        arc_description = f"Steady throughout, you found your rhythm in the middle stretch. Reliability defined your season."
    else:
        arc_type = "The Tumultuous Voyage"
        arc_description = "Your season was a rollercoaster. Highs and lows, but never boring."

    # ====================================================================================
    # BADGES & MARKS: The Legacy System
    # ====================================================================================
    # Evaluate manager and award 3 achievements (mix of badges and marks)
    # Badges = honors, marks = shames

    # Extract metrics needed for both achievements and legacy narrative
    draft_grade = card_2.get('draft', {}).get('grade', 'N/A')
    trade_verdict = card_2.get('trades', {}).get('overall_verdict', '')
    efficiency_pct = card_3.get('efficiency', {}).get('lineup_efficiency_pct', 0)
    waiver_efficiency = card_2.get('waivers', {}).get('efficiency_rate', 0)

    legacy_achievements = evaluate_manager_achievements(calc, team_key, other_cards)

    # ====================================================================================
    # DEFINING MOMENTS
    # ====================================================================================

    defining_moments = []

    # Best week
    best_week = None
    best_week_score = 0
    for week in regular_season_weeks:
        week_key = f'week_{week}'
        if week_key in calc.weekly_data.get(team_key, {}):
            week_data = calc.weekly_data[team_key][week_key]
            score = week_data.get('actual_points', 0)
            if score > best_week_score:
                best_week_score = score
                best_week = week

    if best_week:
        defining_moments.append({
            'week': best_week,
            'title': 'Peak Performance',
            'description': f'Scored {best_week_score:.1f} points in Week {best_week} - your highest output of the season'
        })

    # The Fatal Error (from Card 3)
    fatal_error = card_3.get('pivotal_moments', {}).get('the_fatal_error', {})
    if fatal_error:
        defining_moments.append({
            'week': fatal_error.get('week', 0),
            'title': 'The One That Got Away',
            'description': f"Week {fatal_error.get('week', 0)}: {fatal_error.get('what_happened', 'A pivotal mistake')}"
        })

    # Best trade (from Card 2)
    trades = card_2.get('trades', {}).get('trades', [])
    if trades:
        best_trade = max(trades, key=lambda t: t.get('net_started_impact', 0))
        if best_trade.get('net_started_impact', 0) > 10:
            defining_moments.append({
                'week': best_trade.get('trade_week', 0),
                'title': 'The Heist',
                'description': f"Week {best_trade.get('trade_week', 0)} trade netted you +{best_trade.get('net_started_impact', 0):.1f} started points"
            })

    # ====================================================================================
    # LESSONS LEARNED
    # ====================================================================================

    lessons = []

    # From draft performance
    if draft_grade in ['D', 'F']:
        lessons.append({
            'category': 'Draft',
            'lesson': 'The draft sets your foundation. Study player values and avoid reaches.',
            'action': 'Use auction values or ADP data to identify steals and avoid busts.'
        })

    # From lineup efficiency
    if efficiency_pct < 80:
        lessons.append({
            'category': 'Lineup Management',
            'lesson': f'You left {card_3.get("efficiency", {}).get("total_bench_points_left", 0):.1f} points on your bench. Set lineups carefully.',
            'action': 'Check injury reports, weather, and matchups before each week.'
        })

    # From trading
    if 'Poor trader' in trade_verdict:
        lessons.append({
            'category': 'Trading',
            'lesson': 'Trade smarter, not harder. Focus on players you\'ll actually start.',
            'action': 'Target players with favorable playoff schedules and high usage rates.'
        })

    # From waiver wire
    waiver_efficiency = card_2.get('waivers', {}).get('efficiency_rate', 0)
    if waiver_efficiency < 40:
        lessons.append({
            'category': 'Waiver Wire',
            'lesson': 'Most of your pickups didn\'t pan out. Be more selective.',
            'action': 'Target players with clear paths to volume, not just hype.'
        })

    # Generic wisdom if no specific lessons
    if not lessons:
        lessons.append({
            'category': 'General',
            'lesson': 'You managed your team well. Keep refining your process.',
            'action': 'Study your league\'s scoring tendencies and exploit market inefficiencies.'
        })

    # ====================================================================================
    # MANAGER ARCHETYPE & LEGACY
    # ====================================================================================

    # Determine primary strength
    strengths = []
    if draft_grade in ['A', 'A+', 'B']:
        strengths.append('Draft')
    if efficiency_pct >= 85:
        strengths.append('Lineups')
    if 'Good trader' in trade_verdict or 'Elite trader' in trade_verdict:
        strengths.append('Trading')
    if waiver_efficiency >= 60:
        strengths.append('Waivers')

    # Determine archetype
    if len(strengths) >= 3:
        archetype = "The Complete Manager"
        archetype_desc = "You excel in all phases of the game. A true fantasy virtuoso."
    elif 'Draft' in strengths and 'Lineups' in strengths:
        archetype = "The Fundamentalist"
        archetype_desc = "You win with preparation and execution. Draft well, set lineups carefully."
    elif 'Trading' in strengths or 'Waivers' in strengths:
        archetype = "The Opportunist"
        archetype_desc = "You thrive on the wire and in trades. Always looking for an edge."
    elif draft_grade in ['A', 'A+']:
        archetype = "The Draft Savant"
        archetype_desc = "You dominate draft day. If only the season ended there."
    elif efficiency_pct >= 85:
        archetype = "The Lineup Tactician"
        archetype_desc = "You set lineups with precision. Maximizing your roster weekly."
    else:
        archetype = "The Survivor"
        archetype_desc = "You made it through the season. Sometimes that's enough."

    # Legacy statement
    if made_playoffs and wins >= (losses + 2):
        legacy = f"{manager_name} built a {team_name} dynasty. {wins}-{losses}. Playoffs. Respect earned."
    elif made_playoffs:
        legacy = f"{manager_name} and {team_name} clawed into the playoffs. {wins}-{losses}. The journey continues."
    elif wins > losses:
        legacy = f"{manager_name} ran {team_name} above .500 ({wins}-{losses}) but fell short. Lessons learned."
    else:
        legacy = f"{manager_name}'s {team_name} struggled ({wins}-{losses}), but every champion has fallen before rising."

    # ====================================================================================
    # RETURN RESULT
    # ====================================================================================

    return {
        'manager_name': manager_name,
        'team_name': team_name,
        'card_name': 'The Legacy',

        # Season summary
        'season_summary': {
            'record': f"{wins}-{losses}" + (f"-{ties}" if ties > 0 else ""),
            'points_for': round(points_for, 1),
            'points_against': round(points_against, 1),
            'playoff_status': 'Made Playoffs' if made_playoffs else 'Missed Playoffs',
        },

        # The Three Acts
        'season_arc': {
            'arc_type': arc_type,
            'arc_description': arc_description,
            'act_1': {
                'title': 'The Beginning',
                'weeks': f'Weeks {early_weeks[0]}-{early_weeks[-1]}',
                'record': f'{early_wins}-{len(early_weeks)-early_wins}',
                'points': round(early_points, 1),
                'ppg': round(early_points / len(early_weeks), 1)
            },
            'act_2': {
                'title': 'The Middle',
                'weeks': f'Weeks {mid_weeks[0]}-{mid_weeks[-1]}' if mid_weeks else 'N/A',
                'record': f'{mid_wins}-{len(mid_weeks)-mid_wins}' if mid_weeks else 'N/A',
                'points': round(mid_points, 1),
                'ppg': round(mid_points / len(mid_weeks), 1) if mid_weeks else 0
            },
            'act_3': {
                'title': 'The End',
                'weeks': f'Weeks {late_weeks[0]}-{late_weeks[-1]}' if late_weeks else 'N/A',
                'record': f'{late_wins}-{len(late_weeks)-late_wins}' if late_weeks else 'N/A',
                'points': round(late_points, 1),
                'ppg': round(late_points / len(late_weeks), 1) if late_weeks else 0
            },
        },

        # Legacy Achievements (Badges & Marks)
        'legacy_achievements': legacy_achievements,

        # Defining moments
        'defining_moments': defining_moments,

        # Lessons learned
        'lessons_learned': lessons,

        # Manager archetype
        'archetype': {
            'type': archetype,
            'description': archetype_desc,
            'strengths': strengths if strengths else ['Perseverance'],
            'primary_strength': strengths[0] if strengths else 'Determination',
        },

        # Legacy statement
        'legacy': legacy,

        # Final reflection
        'final_reflection': {
            'what_went_right': f"Your {strengths[0] if strengths else 'resilience'} carried you this season." if strengths else "You made it through a challenging season.",
            'what_went_wrong': lessons[0]['lesson'] if lessons else "Even the best have room to grow.",
            'next_season_goal': f"Improve your {lessons[0]['category'].lower()} game." if lessons else "Run it back and dominate."
        }
    }
