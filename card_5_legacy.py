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

    # Season arc removed - archetype is the primary identity now

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

    # Get archetype from Card 1 (the single source of truth)
    card_1 = other_cards.get('card_1_reckoning', {})
    archetype = card_1.get('archetype', {})
    archetype_name = archetype.get('name', 'The Survivor')
    archetype_tagline = archetype.get('tagline', 'Made it through the season')
    archetype_description = archetype.get('description', 'You made it through the season')

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

        # Manager archetype (from Card 1 - single source of truth)
        'archetype': {
            'name': archetype_name,
            'tagline': archetype_tagline,
            'description': archetype_description,
        },

        # Legacy Achievements (Badges & Marks)
        'legacy_achievements': legacy_achievements,

        # Defining moments
        'defining_moments': defining_moments,

        # Lessons learned
        'lessons_learned': lessons
    }
