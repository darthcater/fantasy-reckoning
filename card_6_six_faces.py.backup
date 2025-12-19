"""
Card 6: The Six Faces - Manager Excellence Score
Composite analysis combining all dimensions of fantasy performance
"""

from league_metrics import get_grade_from_percentile


def calculate_card_6_excellence(calc, team_key: str, other_cards: dict) -> dict:
    """
    Calculate Card 6: The Six Faces - Overall Excellence Score

    Combines metrics from Cards 1-5 to create a holistic view of manager performance:
    - Card 1: Draft Performance
    - Card 2: Lineup Efficiency
    - Card 3: Bench Management (inverted - lower is better)
    - Card 4: Waiver Activity
    - Card 5: True Team Strength (All-Play Record)

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key
        other_cards: Dict containing Cards 1-5 data

    Returns:
        Dict with overall excellence score and manager profile
    """
    team = calc.teams[team_key]

    # Get data from other cards
    card_1 = other_cards.get('card_1_draft', {})
    card_2 = other_cards.get('card_2_identity', {})
    card_3 = other_cards.get('card_3_inflection', {})
    card_4 = other_cards.get('card_4_ecosystem', {})
    card_5 = other_cards.get('card_5_ledger', {})

    # ================================================================
    # Extract percentiles from each card
    # ================================================================

    # Card 1: Draft Performance
    # Assuming Card 1 has a VOR rank that we can convert to percentile
    draft_rank = card_1.get('rank', 7)
    num_teams = len(calc.teams)
    draft_percentile = ((num_teams - draft_rank + 1) / num_teams) * 100

    # Card 2: Lineup Efficiency
    lineup_percentile = card_2.get('efficiency', {}).get('percentile', 50)

    # Card 3: Bench Management (lower bench gap is better, so percentile already accounts for this)
    bench_percentile = card_3.get('bench_gap_metric', {}).get('percentile', 50)

    # Card 4: Waiver Activity
    waiver_percentile = card_4.get('waiver_contribution', {}).get('percentile', 50)

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

    # Calculate league rank based on excellence score
    all_team_scores = {}
    for tk in calc.teams.keys():
        # Calculate excellence score for each team
        tk_card_1 = calc.calculate_card_1(tk)
        tk_card_2 = calc.calculate_card_2(tk)
        tk_card_3 = calc.calculate_card_3(tk)
        tk_card_4 = calc.calculate_card_4(tk)
        tk_card_5 = calc.calculate_card_5(tk, {
            'card_1_draft': tk_card_1,
            'card_2_identity': tk_card_2,
            'card_3_inflection': tk_card_3,
            'card_4_ecosystem': tk_card_4
        })

        # Extract percentiles
        tk_draft_rank = tk_card_1.get('rank', 7)
        tk_draft_pct = ((num_teams - tk_draft_rank + 1) / num_teams) * 100
        tk_lineup_pct = tk_card_2.get('efficiency', {}).get('percentile', 50)
        tk_bench_pct = tk_card_3.get('bench_gap_metric', {}).get('percentile', 50)
        tk_waiver_pct = tk_card_4.get('waiver_contribution', {}).get('percentile', 50)
        tk_all_play_pct = tk_card_5.get('all_play_record', {}).get('percentile', 50)

        # Calculate weighted score
        tk_score = (
            tk_draft_pct * weights['draft'] +
            tk_lineup_pct * weights['lineups'] +
            tk_bench_pct * weights['bench'] +
            tk_waiver_pct * weights['waivers'] +
            tk_all_play_pct * weights['all_play']
        )
        all_team_scores[tk] = tk_score

    # Rank teams by excellence score
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

    # Determine primary archetype based on strengths
    if strongest_dimension[0] == 'draft' and strongest_dimension[1] >= 75:
        primary_archetype = "Draft Elite"
        archetype_description = "You crushed the draft and built a strong foundation"
    elif strongest_dimension[0] == 'lineups' and strongest_dimension[1] >= 80:
        primary_archetype = "Lineup Optimizer"
        archetype_description = "Your weekly lineup decisions were consistently excellent"
    elif strongest_dimension[0] == 'waivers' and strongest_dimension[1] >= 75:
        primary_archetype = "Waiver Wire Hunter"
        archetype_description = "You dominated the waiver wire and improved your roster"
    elif strongest_dimension[0] == 'all_play' and strongest_dimension[1] >= 75:
        primary_archetype = "Consistent Performer"
        archetype_description = "Your team was consistently strong week after week"
    elif waiver_percentile < 25:
        primary_archetype = "Waiver Wire Passive"
        archetype_description = "You relied too heavily on your draft"
    else:
        primary_archetype = "Balanced Manager"
        archetype_description = "You showed competence across multiple dimensions"

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
        'overall_rank': f"{overall_rank}/{num_teams}",
        'overall_rank_numeric': overall_rank,
        'overall_percentile': round(overall_percentile, 1),

        'dimension_breakdown': dimension_breakdown,

        'manager_profile': {
            'primary_archetype': primary_archetype,
            'description': archetype_description,
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
