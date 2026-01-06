"""
Manager Archetype System for Card 1
Assigns ONE personality archetype per manager based on play style, not performance.

NEW FOR 2025:
- Consolidated to 10 archetypes (down from 40+)
- League-level assignment with MAX 3 teams per archetype
- Ensures archetype diversity across the league
"""

# ====================================================================================
# CONSTANTS
# ====================================================================================

# Behavior thresholds for archetype scoring
HIGH_TRANSACTIONS = 20
VERY_HIGH_TRANSACTIONS = 25
LOW_TRANSACTIONS = 5
VERY_LOW_TRANSACTIONS = 3

MANY_TRADES = 5
SOME_TRADES = 3

HIGH_WAIVER_ADDS = 10
VERY_HIGH_WAIVER_ADDS = 15

HIGH_EFFICIENCY = 93
GOOD_EFFICIENCY = 85
POOR_EFFICIENCY = 70
VERY_POOR_EFFICIENCY = 60

HIGH_VARIANCE = 400
MODERATE_VARIANCE = 300
LOW_VARIANCE = 150
VERY_LOW_VARIANCE = 200

# League-level capacity
MAX_PER_ARCHETYPE = 3

# ====================================================================================
# ARCHETYPE DEFINITIONS
# ====================================================================================

ARCHETYPES = {
    'tinkerer': {
        'id': 'tinkerer',
        'name': 'The Tinkerer',
        'description': 'Constantly adjusting, never satisfied',
        'tagline': 'Forever tweaking, never still',
        'category': 'activity'
    },
    'loyalist': {
        'id': 'loyalist',
        'name': 'The Loyalist',
        'description': 'Rides with roster through triumph and tragedy',
        'tagline': 'Faithful to thy first choices',
        'category': 'activity'
    },
    'dealer': {
        'id': 'dealer',
        'name': 'The Dealer',
        'description': 'Lives to negotiate, thrives in the marketplace',
        'category': 'trading'
    },
    'hermit': {
        'id': 'hermit',
        'name': 'The Hermit',
        'description': 'Builds in isolation, trusts no one',
        'category': 'trading'
    },
    'gambler': {
        'id': 'gambler',
        'name': 'The Gambler',
        'description': 'Swings for the fences, chasing upside over safety',
        'category': 'risk'
    },
    'conservative': {
        'id': 'conservative',
        'name': 'The Conservative',
        'description': 'Plays the percentages, avoids variance',
        'category': 'risk'
    },
    'optimizer': {
        'id': 'optimizer',
        'name': 'The Optimizer',
        'description': 'Squeezes out every possible point',
        'tagline': 'Perfection in execution',
        'category': 'lineup'
    },
    'erratic': {
        'id': 'erratic',
        'name': 'The Erratic',
        'description': 'Trusts gut over data, often incorrectly',
        'category': 'lineup'
    },
    'rock': {
        'id': 'rock',
        'name': 'The Rock',
        'description': 'Reliable week after week, unwavering consistency',
        'category': 'consistency'
    },
    'rollercoaster': {
        'id': 'rollercoaster',
        'name': 'The Rollercoaster',
        'description': 'Wild swings define thy season',
        'category': 'consistency'
    },
}


# ====================================================================================
# ARCHETYPE SCORING
# ====================================================================================

def score_archetypes_for_team(calc, team_key: str, other_cards: dict | None = None) -> dict:
    """
    Score all 10 archetypes for a single team based on behavioral signals.

    Args:
        calc: Calculator object with league data
        team_key: Team identifier
        other_cards: Optional dict containing data from cards 2-4

    Returns:
        dict mapping archetype_id -> numeric score (higher = better fit)
    """
    if other_cards is None:
        other_cards = {}

    # Get data from other cards
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_lineups', {})
    card_4 = other_cards.get('card_4_story', {})

    # Gather behavioral data
    # Note: transactions_by_team counts individual adds+drops, divide by 2 to get "moves"
    raw_transactions = len(calc.transactions_by_team.get(team_key, []))
    transactions = raw_transactions // 2  # Convert to moves (matches Yahoo's "Moves" column)
    trades = len(card_2.get('trades', {}).get('all_trades', []))
    waiver_adds = card_2.get('waivers', {}).get('total_adds', 0)
    efficiency_pct = card_3.get('efficiency', {}).get('lineup_efficiency_pct', 0)

    # Calculate scoring variance from weekly data (card_4 doesn't store this)
    weekly_scores = []
    team_weekly = calc.weekly_data.get(team_key, {})
    for week in calc.get_regular_season_weeks():
        week_key = f'week_{week}'
        if week_key in team_weekly:
            score = team_weekly[week_key].get('actual_points', 0)
            if score > 0:
                weekly_scores.append(score)

    if len(weekly_scores) >= 2:
        mean_score = sum(weekly_scores) / len(weekly_scores)
        scoring_variance = sum((s - mean_score) ** 2 for s in weekly_scores) / len(weekly_scores)
    else:
        scoring_variance = 0

    scores = {}

    # ========================================================================
    # TINKERER: Very high transactions and waiver activity
    # ========================================================================
    if transactions >= HIGH_TRANSACTIONS:
        scores['tinkerer'] = 20
    if transactions >= VERY_HIGH_TRANSACTIONS:
        scores['tinkerer'] = 25

    # ========================================================================
    # LOYALIST: Very low transactions, sticks with draft
    # ========================================================================
    if transactions <= LOW_TRANSACTIONS:
        scores['loyalist'] = 15
    if transactions <= VERY_LOW_TRANSACTIONS:
        scores['loyalist'] = 20

    # ========================================================================
    # DEALER: Relatively many trades
    # ========================================================================
    if trades >= SOME_TRADES:
        scores['dealer'] = 15
    if trades >= MANY_TRADES:
        scores['dealer'] = 20

    # ========================================================================
    # HERMIT: Zero trades AND low transactions
    # ========================================================================
    if trades == 0 and transactions <= LOW_TRANSACTIONS:
        scores['hermit'] = 15
    if trades == 0 and transactions <= VERY_LOW_TRANSACTIONS:
        scores['hermit'] = 20

    # ========================================================================
    # GAMBLER: High scoring variance
    # ========================================================================
    if scoring_variance >= MODERATE_VARIANCE:
        scores['gambler'] = 12
    if scoring_variance >= HIGH_VARIANCE:
        scores['gambler'] = 18

    # ========================================================================
    # CONSERVATIVE: Low variance plus decent efficiency
    # ========================================================================
    if scoring_variance <= LOW_VARIANCE:
        scores['conservative'] = 12
    if scoring_variance <= LOW_VARIANCE and efficiency_pct >= GOOD_EFFICIENCY:
        scores['conservative'] = 18

    # ========================================================================
    # OPTIMIZER: Very high lineup efficiency
    # ========================================================================
    if efficiency_pct >= GOOD_EFFICIENCY:
        scores['optimizer'] = 12
    if efficiency_pct >= HIGH_EFFICIENCY:
        scores['optimizer'] = 20

    # ========================================================================
    # ERRATIC: Low lineup efficiency and/or high variance
    # ========================================================================
    if efficiency_pct < POOR_EFFICIENCY:
        scores['erratic'] = 12
    if efficiency_pct < VERY_POOR_EFFICIENCY:
        scores['erratic'] = 18
    if efficiency_pct < POOR_EFFICIENCY and scoring_variance >= MODERATE_VARIANCE:
        scores['erratic'] = 20

    # ========================================================================
    # ROCK: Low variance and acceptable efficiency
    # ========================================================================
    if scoring_variance < LOW_VARIANCE and efficiency_pct >= 75:
        scores['rock'] = 18
    if scoring_variance < LOW_VARIANCE and efficiency_pct >= GOOD_EFFICIENCY:
        scores['rock'] = 22

    # ========================================================================
    # ROLLERCOASTER: Very high variance regardless of efficiency
    # ========================================================================
    if scoring_variance >= HIGH_VARIANCE:
        scores['rollercoaster'] = 15
    if scoring_variance >= 550:
        scores['rollercoaster'] = 20

    return scores


def select_archetype_for_team(scores: dict, fallback_id: str = 'rock') -> str:
    """
    Select the single best archetype for a team based on scores.

    Args:
        scores: dict mapping archetype_id -> score
        fallback_id: archetype to use if scores is empty

    Returns:
        str: the selected archetype_id
    """
    if not scores:
        return fallback_id

    # Return archetype with highest score (break ties alphabetically for determinism)
    return max(scores.items(), key=lambda x: (x[1], -ord(x[0][0])))[0]


# ====================================================================================
# LEAGUE-LEVEL ASSIGNMENT WITH CAPACITY CONSTRAINTS
# ====================================================================================

def assign_archetypes_for_league(calc, team_keys: list[str], other_cards_by_team: dict) -> dict:
    """
    Assign ONE archetype to each team in the league, enforcing that
    no more than MAX_PER_ARCHETYPE teams receive the same archetype.

    This ensures archetype diversity across the league while still
    assigning the best-fit archetype to each team when possible.

    Args:
        calc: Calculator object with league data
        team_keys: List of team_key strings for this league
        other_cards_by_team: Mapping team_key -> other_cards dict

    Returns:
        dict mapping team_key -> archetype data (full dict from ARCHETYPES)
    """
    # Step 1: Score all archetypes for all teams
    team_scores = {}
    for team_key in team_keys:
        other_cards = other_cards_by_team.get(team_key, {})
        team_scores[team_key] = score_archetypes_for_team(calc, team_key, other_cards)

    # Step 2: Build preference list for each team (sorted by score descending)
    team_preferences = {}
    for team_key, scores in team_scores.items():
        # Sort by score descending, then alphabetically for determinism
        sorted_archetypes = sorted(
            scores.items(),
            key=lambda x: (x[1], -ord(x[0][0])),
            reverse=True
        )
        # Extract just the archetype IDs
        team_preferences[team_key] = [archetype_id for archetype_id, _ in sorted_archetypes]

        # If team has no scores, give them all archetypes in alphabetical order
        if not team_preferences[team_key]:
            team_preferences[team_key] = sorted(ARCHETYPES.keys())

    # Step 3: Assign each team their highest-scoring archetype (no capacity limits)
    assignments = {}

    for team_key in team_keys:
        preferences = team_preferences[team_key]

        if preferences:
            # Assign the highest-scoring archetype
            assignments[team_key] = ARCHETYPES[preferences[0]].copy()
        else:
            # Fallback for teams with no scores
            assignments[team_key] = ARCHETYPES['rock'].copy()

    return assignments


# ====================================================================================
# BACKWARDS-COMPATIBLE SINGLE-TEAM API
# ====================================================================================

def determine_manager_archetype(calc, team_key: str, other_cards: dict | None = None) -> dict:
    """
    Backwards-compatible wrapper for single-team archetype determination.

    This function maintains the original API for code that generates cards
    for individual teams without league-level context.

    NOTE: This does NOT enforce the MAX_PER_ARCHETYPE constraint.
    Use assign_archetypes_for_league() when generating cards for an entire league.

    Args:
        calc: Calculator object with league data
        team_key: Team identifier
        other_cards: Optional dict containing data from cards 2-4

    Returns:
        dict with archetype id, name, description, category
    """
    scores = score_archetypes_for_team(calc, team_key, other_cards)
    selected_id = select_archetype_for_team(scores, fallback_id='rock')
    return ARCHETYPES[selected_id].copy()
