"""
Card 1: The Reckoning - Season Overview
Executive summary with spider chart, season stats, and manager archetype
"""

from league_metrics import get_grade_from_percentile
from archetypes import determine_manager_archetype


def get_medieval_label_from_grade(grade: str) -> str:
    """
    Convert letter grade to medieval-style excellence label
    Using selections from Reckoning Scribe
    """
    grade_labels = {
        'A+': "Crowned Above All",
        'A': "Peerless in This Campaign",
        'A-': "Sovereign of the Season",
        'B+': "Counted Among the Able",
        'B': "Well-Proven in the Lists",
        'B-': "A Cut Above the Common",
        'C+': "Neither Shamed nor Sung",
        'C': "A Season of Little Note",
        'C-': "Of Modest Repute",
        'D+': "Found Wanting",
        'D': "Measured and Found Light",
        'D-': "A Record of Faded Hopes",
        'F': "Unworthy of Song or Story"
    }
    return grade_labels.get(grade, "Of Modest Repute")


def calculate_card_1_reckoning(calc, team_key: str, other_cards: dict = None) -> dict:
    """
    Calculate Card 1: The Reckoning - Overall Excellence Score & Overview

    Combines metrics from all other cards to create an executive summary:
    - Season summary (record, standings, playoffs)
    - Spider chart with dimensional analysis
    - Manager archetype and profile
    - Overall excellence score

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key
        other_cards: Dict containing other cards' data (may be None on first pass)

    Returns:
        Dict with overview, spider chart, and excellence score
    """
    # Handle case where other_cards is not yet available
    if other_cards is None:
        other_cards = {}
    team = calc.teams[team_key]

    # Get data from other cards
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_campaign', {})
    card_4 = other_cards.get('card_4_design', {})
    card_5 = other_cards.get('card_5_legacy', {})

    # ================================================================
    # Extract percentiles from each card
    # ================================================================

    # Card 2: Draft Performance
    # Get draft rank from card_2_roster
    draft_rank = card_2.get('draft', {}).get('rank', 7)
    num_teams = len(calc.teams)
    draft_percentile = ((num_teams - draft_rank + 1) / num_teams) * 100

    # Card 3: Lineup Efficiency
    lineup_percentile = card_3.get('efficiency', {}).get('percentile', 50)

    # Card 3: Bench Management (lower bench gap is better, so percentile already accounts for this)
    bench_percentile = card_3.get('bench_gap_metric', {}).get('percentile', 50)

    # Card 4: Waiver Activity
    # Calculate waiver percentile by comparing all teams
    # Use cached waiver scores if available, otherwise calculate once

    if not hasattr(calc, '_waiver_scores_cache'):
        # Calculate waiver scores for all teams once
        from card_2_ledger import calculate_card_2_ledger
        calc._waiver_scores_cache = {}

        for tk in calc.teams.keys():
            # Get waiver data for this team
            tk_card2 = calculate_card_2_ledger(calc, tk)
            tk_waiver_pts = tk_card2.get('waivers', {}).get('total_points_started', 0)
            tk_costly_drops = tk_card2.get('costly_drops', {}).get('total_value_given_away', 0)

            # Net waiver score = points added via waivers - points given away via drops
            tk_waiver_score = tk_waiver_pts - tk_costly_drops
            calc._waiver_scores_cache[tk] = tk_waiver_score

    # Calculate percentile based on ranking
    this_team_score = calc._waiver_scores_cache[team_key]
    teams_below = sum(1 for score in calc._waiver_scores_cache.values() if score < this_team_score)
    waiver_percentile = (teams_below / (num_teams - 1)) * 100 if num_teams > 1 else 50

    # Card 5: All-Play Record (True Skill)
    all_play_percentile = card_5.get('all_play_record', {}).get('percentile', 50)

    # ================================================================
    # Calculate weighted excellence score
    # ================================================================

    # Weights for each dimension
    weights = {
        'draft': 0.20,       # 20% - Foundation of your team
        'lineups': 0.20,     # 20% - Weekly decision-making
        'bench': 0.10,       # 10% - Lineup optimization
        'waivers': 0.25,     # 25% - Roster improvement (most impactful)
        'all_play': 0.25     # 25% - True strength measure
    }

    # Calculate weighted average
    excellence_score = (
        draft_percentile * weights['draft'] +
        lineup_percentile * weights['lineups'] +
        bench_percentile * weights['bench'] +
        waiver_percentile * weights['waivers'] +
        all_play_percentile * weights['all_play']
    )

    # Calculate letter grade
    overall_grade = get_grade_from_percentile(excellence_score)

    # Calculate league rank based on wins (simple, no recursion)
    # FIX: Don't recursively calculate all cards - causes infinite recursion
    # Instead, rank by wins which is simpler and already calculated
    all_team_scores = {}
    for tk in calc.teams.keys():
        tk_stats = calc.calculate_team_stats_from_weekly_data(tk)
        # Use win percentage as proxy for excellence
        tk_win_pct = tk_stats['wins'] / (tk_stats['wins'] + tk_stats['losses']) if (tk_stats['wins'] + tk_stats['losses']) > 0 else 0
        all_team_scores[tk] = tk_win_pct * 100

    # Rank teams by win percentage
    sorted_teams = sorted(all_team_scores.items(), key=lambda x: x[1], reverse=True)
    overall_rank = next((i + 1 for i, (tk, _) in enumerate(sorted_teams) if tk == team_key), num_teams)
    overall_percentile = ((num_teams - overall_rank) / num_teams) * 100

    # ================================================================
    # Identify manager archetype based on dimension strengths
    # ================================================================

    dimension_scores = {
        'draft': draft_percentile,
        'lineups': lineup_percentile,
        'bench': bench_percentile,
        'waivers': waiver_percentile,
        'all_play': all_play_percentile
    }

    # Find strongest and weakest dimensions
    sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
    strongest_dimension = sorted_dimensions[0]
    weakest_dimension = sorted_dimensions[-1]

    # Determine manager archetype (ONE personality based on play style)
    archetype = determine_manager_archetype(calc, team_key, other_cards)
    primary_archetype = archetype['name']
    archetype_tagline = archetype['tagline']
    archetype_description = archetype['description']

    # Identify weakness
    weakness = ""
    if weakest_dimension[1] < 25:
        if weakest_dimension[0] == 'draft':
            weakness = "Draft Struggles"
        elif weakest_dimension[0] == 'lineups':
            weakness = "Lineup Mistakes"
        elif weakest_dimension[0] == 'waivers':
            weakness = "Waiver Inactivity"
        elif weakest_dimension[0] == 'all_play':
            weakness = "Inconsistent Performance"
        elif weakest_dimension[0] == 'bench':
            weakness = "Poor Bench Management"

    # ================================================================
    # Calculate improvement potential
    # ================================================================

    # If you improved your weakest dimension to 70th percentile, what would your score be?
    target_percentile = 70
    potential_improvement = max(0, target_percentile - weakest_dimension[1])

    ceiling_score = excellence_score + (potential_improvement * weights[weakest_dimension[0]])

    # Calculate what rank that would give you
    ceiling_rank = sum(1 for score in all_team_scores.values() if score > ceiling_score) + 1

    # ================================================================
    # Create dimension breakdown
    # ================================================================

    dimension_breakdown = {
        'draft': {
            'percentile': round(draft_percentile, 1),
            'grade': get_grade_from_percentile(draft_percentile),
            'weight': weights['draft'],
            'contribution': round(draft_percentile * weights['draft'], 1),
            'label': 'Draft Performance'
        },
        'lineups': {
            'percentile': round(lineup_percentile, 1),
            'grade': get_grade_from_percentile(lineup_percentile),
            'weight': weights['lineups'],
            'contribution': round(lineup_percentile * weights['lineups'], 1),
            'label': 'Lineup Efficiency'
        },
        'bench': {
            'percentile': round(bench_percentile, 1),
            'grade': get_grade_from_percentile(bench_percentile),
            'weight': weights['bench'],
            'contribution': round(bench_percentile * weights['bench'], 1),
            'label': 'Bench Management'
        },
        'waivers': {
            'percentile': round(waiver_percentile, 1),
            'grade': get_grade_from_percentile(waiver_percentile),
            'weight': weights['waivers'],
            'contribution': round(waiver_percentile * weights['waivers'], 1),
            'label': 'Waiver Activity'
        },
        'all_play': {
            'percentile': round(all_play_percentile, 1),
            'grade': get_grade_from_percentile(all_play_percentile),
            'weight': weights['all_play'],
            'contribution': round(all_play_percentile * weights['all_play'], 1),
            'label': 'True Strength'
        }
    }

    # ================================================================
    # Generate manager summary narrative
    # ================================================================

    # Count strong dimensions (>=60th percentile)
    strong_dimensions = [k for k, v in dimension_scores.items() if v >= 60]
    weak_dimensions = [k for k, v in dimension_scores.items() if v < 40]

    if len(strong_dimensions) >= 4:
        manager_summary = "Well-rounded excellence across multiple dimensions"
    elif len(strong_dimensions) >= 2:
        manager_summary = f"Strong in {len(strong_dimensions)} areas, but inconsistent"
    elif len(weak_dimensions) >= 3:
        manager_summary = "Struggled across multiple fundamental areas"
    else:
        manager_summary = "One-dimensional performance with clear gaps"

    return {
        'manager_name': team['manager_name'],
        'overall_excellence_score': round(excellence_score, 1),
        'overall_grade': overall_grade,

        # Manager archetype (replaces medieval label)
        'archetype': {
            'name': primary_archetype,
            'tagline': archetype_tagline,
            'description': archetype_description,
        },
        'overall_rank': f"{overall_rank}/{num_teams}",
        'overall_rank_numeric': overall_rank,
        'overall_percentile': round(overall_percentile, 1),

        'dimension_breakdown': dimension_breakdown,

        'manager_profile': {
            'primary_archetype': primary_archetype,  # Deprecated, use archetype at root level
            'archetype_tagline': archetype_tagline,  # Deprecated
            'strongest_dimension': strongest_dimension[0],
            'strongest_percentile': round(strongest_dimension[1], 1),
            'weakest_dimension': weakest_dimension[0],
            'weakest_percentile': round(weakest_dimension[1], 1),
            'weakness_label': weakness if weakness else "No major weakness",
            'manager_summary': manager_summary
        },

        'improvement_potential': {
            'biggest_opportunity': weakest_dimension[0],
            'current_percentile': round(weakest_dimension[1], 1),
            'target_percentile': target_percentile,
            'potential_gain': round(potential_improvement, 1),
            'ceiling_score': round(ceiling_score, 1),
            'ceiling_rank': f"{ceiling_rank}/{num_teams}",
            'message': f"If you improve your {weakest_dimension[0]} from {weakest_dimension[1]:.0f}th to {target_percentile}th percentile, you'd jump to rank {ceiling_rank}/{num_teams}"
        },

        'league_context': {
            'num_teams': num_teams,
            'league_avg_score': round(sum(all_team_scores.values()) / num_teams, 1),
            'top_score': round(max(all_team_scores.values()), 1),
            'gap_to_top': round(max(all_team_scores.values()) - excellence_score, 1)
        }
    }
