"""
Card 1: The Leader
How you played and stacked up against your rivals

Displays:
- Manager archetype
- 4 skill percentiles: Draft, Lineups, Bye Week Management, Waivers
- Overall percentile
"""

from league_metrics import get_grade_from_percentile
from archetypes import determine_manager_archetype


def calculate_card_1_overview(calc, team_key: str, other_cards: dict = None, assigned_archetype: dict = None) -> dict:
    """
    Calculate Card 1: The Leader - Manager archetype and skill percentiles

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key
        other_cards: Dict containing other cards' data
        assigned_archetype: Pre-assigned archetype (max 3 per archetype in league)

    Returns:
        Dict with manager archetype, skill percentiles, and overall rank
    """
    if other_cards is None:
        other_cards = {}

    team = calc.teams[team_key]
    num_teams = len(calc.teams)

    # Get data from other cards
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_lineups', {})

    # ================================================================
    # Calculate percentiles for each dimension
    # ================================================================

    # 1. DRAFT PERFORMANCE
    draft_rank = card_2.get('draft', {}).get('rank', 7)
    draft_percentile = ((num_teams - draft_rank) / (num_teams - 1)) * 100 if num_teams > 1 else 50

    # 2. LINEUP EFFICIENCY
    lineup_percentile = card_3.get('efficiency', {}).get('percentile', 50)

    # 3. BYE WEEK MANAGEMENT
    from bye_week_calculation import calculate_league_bye_week_percentile
    bye_week_percentile = calculate_league_bye_week_percentile(calc, team_key)

    # 4. WAIVER ACTIVITY
    # Calculate waiver scores for all teams once (cached)
    if not hasattr(calc, '_waiver_scores_cache'):
        from card_2_ledger import calculate_card_2_ledger
        calc._waiver_scores_cache = {}

        for tk in calc.teams.keys():
            tk_card2 = calculate_card_2_ledger(calc, tk)
            tk_waiver_pts = tk_card2.get('waivers', {}).get('total_points_started', 0)
            tk_costly_drops = tk_card2.get('costly_drops', {}).get('total_value_given_away', 0)
            # Net waiver score = points added - points given away
            tk_waiver_score = tk_waiver_pts - tk_costly_drops
            calc._waiver_scores_cache[tk] = tk_waiver_score

    # Calculate percentile based on ranking
    this_team_score = calc._waiver_scores_cache[team_key]
    teams_below = sum(1 for score in calc._waiver_scores_cache.values() if score < this_team_score)
    waiver_percentile = (teams_below / (num_teams - 1)) * 100 if num_teams > 1 else 50

    # ================================================================
    # Calculate overall percentile as average of 4 skill dimensions
    # ================================================================

    overall_percentile = (draft_percentile + lineup_percentile + bye_week_percentile + waiver_percentile) / 4

    # ================================================================
    # Determine manager archetype
    # ================================================================

    if assigned_archetype is not None:
        archetype = assigned_archetype
    else:
        archetype = determine_manager_archetype(calc, team_key, other_cards)

    # ================================================================
    # Build dimension breakdown
    # ================================================================

    dimension_breakdown = {
        'draft': {
            'percentile': round(draft_percentile, 1)
        },
        'lineups': {
            'percentile': round(lineup_percentile, 1)
        },
        'bye_week': {
            'percentile': round(bye_week_percentile, 1)
        },
        'waivers': {
            'percentile': round(waiver_percentile, 1)
        }
    }

    return {
        'manager_name': team['manager_name'],
        'archetype': {
            'name': archetype['name'],
            'description': archetype['description']
        },
        'dimension_breakdown': dimension_breakdown,
        'overall_percentile': round(overall_percentile, 1)
    }
