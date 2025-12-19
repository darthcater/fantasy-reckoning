"""
Manager Archetype System for Card I & Card V
Assigns ONE personality archetype per manager based on play style, not performance
"""

# ====================================================================================
# ARCHETYPE DEFINITIONS
# Each archetype has:
# - id: unique identifier
# - name: display name (e.g., "The Tinkerer")
# - description: what this personality means
# - tagline: one-line summary for display
# - category: what behavior this reflects
# ====================================================================================

ARCHETYPES = {
    # ================================================================================
    # ACTIVITY LEVEL - High
    # ================================================================================
    'tinkerer': {
        'id': 'tinkerer',
        'name': 'The Tinkerer',
        'description': 'Constantly adjusting, never satisfied with thy roster',
        'tagline': 'Forever tweaking, never still',
        'category': 'activity'
    },
    'hustler': {
        'id': 'hustler',
        'name': 'The Hustler',
        'description': 'Always working the waiver wire, seeking hidden gems',
        'tagline': 'The wire is thy kingdom',
        'category': 'activity'
    },
    'alchemist': {
        'id': 'alchemist',
        'name': 'The Alchemist',
        'description': 'Attempts to transmute trash into gold through sheer volume',
        'tagline': 'Seeking gold in the rubble',
        'category': 'activity'
    },

    # ================================================================================
    # ACTIVITY LEVEL - Low
    # ================================================================================
    'loyalist': {
        'id': 'loyalist',
        'name': 'The Loyalist',
        'description': 'Rides with drafted players through triumph and tragedy',
        'tagline': 'Faithful to thy first choices',
        'category': 'activity'
    },
    'drafted': {
        'id': 'drafted',
        'name': 'The Drafted',
        'description': 'Thy fate was written on draft day',
        'tagline': 'Lives or dies by the draft',
        'category': 'activity'
    },
    'passive_observer': {
        'id': 'passive_observer',
        'name': 'The Passive Observer',
        'description': 'Minimal engagement, letting fate guide thy team',
        'tagline': 'Watches from afar',
        'category': 'activity'
    },

    # ================================================================================
    # TRADING - Heavy
    # ================================================================================
    'dealer': {
        'id': 'dealer',
        'name': 'The Dealer',
        'description': 'Lives to negotiate, thrives in the marketplace',
        'tagline': 'Master of the deal',
        'category': 'trading'
    },
    'merchant': {
        'id': 'merchant',
        'name': 'The Merchant',
        'description': 'Always seeking value in every transaction',
        'tagline': 'Buys low, sells high',
        'category': 'trading'
    },
    'opportunist': {
        'id': 'opportunist',
        'name': 'The Opportunist',
        'description': 'Strikes when others are weak or desperate',
        'tagline': 'Exploits the vulnerable',
        'category': 'trading'
    },

    # ================================================================================
    # TRADING - Averse
    # ================================================================================
    'hermit': {
        'id': 'hermit',
        'name': 'The Hermit',
        'description': 'Builds in isolation, trusts no one',
        'tagline': 'Alone and unbending',
        'category': 'trading'
    },
    'isolationist': {
        'id': 'isolationist',
        'name': 'The Isolationist',
        'description': 'Refuses to negotiate or engage in trade talks',
        'tagline': 'Self-sufficient to a fault',
        'category': 'trading'
    },
    'self_made': {
        'id': 'self_made',
        'name': 'The Self-Made',
        'description': 'Will not rely on the charity of trades',
        'tagline': 'Forged by thy own hand',
        'category': 'trading'
    },

    # ================================================================================
    # RISK PROFILE - High
    # ================================================================================
    'gambler': {
        'id': 'gambler',
        'name': 'The Gambler',
        'description': 'Swings for the fences, chasing upside over safety',
        'tagline': 'Fortune favors the bold',
        'category': 'risk'
    },
    'contrarian': {
        'id': 'contrarian',
        'name': 'The Contrarian',
        'description': 'Zigs when the league zags',
        'tagline': 'Against the grain',
        'category': 'risk'
    },
    'maverick': {
        'id': 'maverick',
        'name': 'The Maverick',
        'description': 'Plays by their own rules, unconventional to the end',
        'tagline': 'Rules are for the timid',
        'category': 'risk'
    },

    # ================================================================================
    # RISK PROFILE - Low
    # ================================================================================
    'prudent': {
        'id': 'prudent',
        'name': 'The Prudent',
        'description': 'Values safety over ceiling in every decision',
        'tagline': 'Caution above all',
        'category': 'risk'
    },
    'calculated': {
        'id': 'calculated',
        'name': 'The Calculated',
        'description': 'Minimizes downside through careful analysis',
        'tagline': 'Every move measured',
        'category': 'risk'
    },
    'conservative': {
        'id': 'conservative',
        'name': 'The Conservative',
        'description': 'Plays the percentages, avoids variance',
        'tagline': 'The safe path',
        'category': 'risk'
    },

    # ================================================================================
    # LINEUP MANAGEMENT - High Efficiency
    # ================================================================================
    'optimizer': {
        'id': 'optimizer',
        'name': 'The Optimizer',
        'description': 'Squeezes every possible point from thy roster',
        'tagline': 'Perfection in execution',
        'category': 'lineup'
    },
    'scholar': {
        'id': 'scholar',
        'name': 'The Scholar',
        'description': 'Studies matchups with scholarly devotion',
        'tagline': 'Knowledge is power',
        'category': 'lineup'
    },
    'perfectionist': {
        'id': 'perfectionist',
        'name': 'The Perfectionist',
        'description': 'Cannot abide points left on the bench',
        'tagline': 'Flawless or failure',
        'category': 'lineup'
    },

    # ================================================================================
    # LINEUP MANAGEMENT - Low Efficiency
    # ================================================================================
    'erratic': {
        'id': 'erratic',
        'name': 'The Erratic',
        'description': 'Trusts gut over data, often incorrectly',
        'tagline': 'Unpredictable chaos',
        'category': 'lineup'
    },
    'chaos_agent': {
        'id': 'chaos_agent',
        'name': 'The Chaos Agent',
        'description': 'Lineup decisions defy logic and reason',
        'tagline': 'Servant of chaos',
        'category': 'lineup'
    },
    'indecisive': {
        'id': 'indecisive',
        'name': 'The Indecisive',
        'description': 'Second-guesses every choice, usually wrong',
        'tagline': 'Paralyzed by doubt',
        'category': 'lineup'
    },

    # ================================================================================
    # CONSISTENCY - Steady
    # ================================================================================
    'rock': {
        'id': 'rock',
        'name': 'The Rock',
        'description': 'Reliable week after week, unwavering consistency',
        'tagline': 'Steady as stone',
        'category': 'consistency'
    },
    'steady_hand': {
        'id': 'steady_hand',
        'name': 'The Steady Hand',
        'description': 'Consistent approach yields consistent results',
        'tagline': 'Reliable and true',
        'category': 'consistency'
    },
    'fundamentalist': {
        'id': 'fundamentalist',
        'name': 'The Fundamentalist',
        'description': 'Textbook play, no deviations from the script',
        'tagline': 'By the book',
        'category': 'consistency'
    },

    # ================================================================================
    # CONSISTENCY - Volatile
    # ================================================================================
    'boom_bust': {
        'id': 'boom_bust',
        'name': 'The Boom-Bust',
        'description': 'Hero one week, zero the next',
        'tagline': 'Feast or famine',
        'category': 'consistency'
    },
    'rollercoaster': {
        'id': 'rollercoaster',
        'name': 'The Rollercoaster',
        'description': 'Wild swings define thy season',
        'tagline': 'Thrills and despair',
        'category': 'consistency'
    },
    'unpredictable': {
        'id': 'unpredictable',
        'name': 'The Unpredictable',
        'description': 'No one knows what comes next, including thee',
        'tagline': 'Impossible to forecast',
        'category': 'consistency'
    },

    # ================================================================================
    # ROSTER PHILOSOPHY - Hoarder
    # ================================================================================
    'collector': {
        'id': 'collector',
        'name': 'The Collector',
        'description': 'Deep bench, refuses to release anyone',
        'tagline': 'Gathers and never lets go',
        'category': 'roster'
    },
    'protector': {
        'id': 'protector',
        'name': 'The Protector',
        'description': 'Will not give opponents a single useful drop',
        'tagline': 'Denies all enemies',
        'category': 'roster'
    },

    # ================================================================================
    # ROSTER PHILOSOPHY - Churner
    # ================================================================================
    'streamer': {
        'id': 'streamer',
        'name': 'The Streamer',
        'description': 'Weekly roster turnover, no attachment',
        'tagline': 'Constant flux',
        'category': 'roster'
    },
    'hot_hand': {
        'id': 'hot_hand',
        'name': 'The Hot Hand',
        'description': 'Chases recent performance above all else',
        'tagline': 'Rides the wave',
        'category': 'roster'
    },

    # ================================================================================
    # SPECIAL ARCHETYPES
    # ================================================================================
    'survivor': {
        'id': 'survivor',
        'name': 'The Survivor',
        'description': 'Made it through by sheer will alone',
        'tagline': 'Bloodied but standing',
        'category': 'special'
    },
    'underachiever': {
        'id': 'underachiever',
        'name': 'The Underachiever',
        'description': 'Talent exceeded results by vast margin',
        'tagline': 'Squandered potential',
        'category': 'special'
    },
    'overachiever': {
        'id': 'overachiever',
        'name': 'The Overachiever',
        'description': 'Results exceeded talent through will and luck',
        'tagline': 'More than the sum',
        'category': 'special'
    },
    'tragic_figure': {
        'id': 'tragic_figure',
        'name': 'The Tragic Figure',
        'description': 'Bad luck and misfortune defined the season',
        'tagline': 'Cursed by fate',
        'category': 'special'
    },
    'inevitable': {
        'id': 'inevitable',
        'name': 'The Inevitable',
        'description': 'Domination was never in question',
        'tagline': 'Destiny fulfilled',
        'category': 'special'
    },
    'pretender': {
        'id': 'pretender',
        'name': 'The Pretender',
        'description': 'Lucky schedule masked fundamental weakness',
        'tagline': 'False throne',
        'category': 'special'
    },
}


def determine_manager_archetype(calc, team_key: str, other_cards: dict = None) -> dict:
    """
    Determine the ONE archetype that best defines this manager's play style.

    Uses a scoring system to evaluate behavior across multiple dimensions,
    then selects the archetype with the highest score.

    Returns:
        Dict with archetype id, name, description, tagline
    """
    if other_cards is None:
        other_cards = {}

    # Get data from other cards
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_campaign', {})
    card_4 = other_cards.get('card_4_design', {})

    team = calc.teams[team_key]

    # Gather behavioral data
    transactions = len(calc.transactions_by_team.get(team_key, []))
    trades = len(card_2.get('trades', {}).get('all_trades', []))
    waiver_adds = card_2.get('waivers', {}).get('total_adds', 0)
    efficiency_pct = card_3.get('efficiency', {}).get('lineup_efficiency_pct', 0)
    scoring_variance = card_4.get('scoring_power', {}).get('variance', 0)

    # Get rankings for special archetypes
    allplay_rank = card_4.get('true_strength', {}).get('all_play_record', {}).get('rank', 14)
    pf_rank = card_4.get('scoring_power', {}).get('rank', 14)
    final_rank = calc.calculate_team_stats_from_weekly_data(team_key).get('final_rank', 14)
    made_playoffs = calc.calculate_team_stats_from_weekly_data(team_key).get('made_playoffs', False)

    num_teams = len(calc.teams)

    # Score each archetype (higher = better fit)
    scores = {}

    # ========================================================================
    # ACTIVITY LEVEL (increased weight)
    # ========================================================================
    if transactions >= 20:
        scores['tinkerer'] = 12
    if transactions >= 15 and waiver_adds >= 10:
        scores['hustler'] = 11
    if transactions >= 25:
        scores['alchemist'] = 10

    if transactions <= 5:
        scores['loyalist'] = 12
        scores['drafted'] = 11
    if transactions <= 3:
        scores['passive_observer'] = 12

    # ========================================================================
    # TRADING (reduced weight - most leagues don't trade much)
    # ========================================================================
    if trades >= 5:
        scores['dealer'] = 12
    if trades >= 3:
        scores['merchant'] = 10
        scores['opportunist'] = 9

    # Only assign trading-averse archetypes if they're LOW activity overall
    if trades == 0 and transactions <= 5:
        scores['hermit'] = 8
        scores['isolationist'] = 7
    if trades == 0 and transactions <= 3:
        scores['self_made'] = 9

    # ========================================================================
    # RISK PROFILE (based on variance and roster volatility)
    # ========================================================================
    if scoring_variance >= 400:
        scores['gambler'] = 10
        scores['maverick'] = 8
    if scoring_variance >= 300 and transactions >= 15:
        scores['contrarian'] = 7

    if scoring_variance <= 150:
        scores['prudent'] = 10
        scores['conservative'] = 9
    if scoring_variance <= 200 and efficiency_pct >= 80:
        scores['calculated'] = 8

    # ========================================================================
    # LINEUP MANAGEMENT
    # ========================================================================
    if efficiency_pct >= 90:
        scores['optimizer'] = 10
        scores['perfectionist'] = 9
    if efficiency_pct >= 85:
        scores['scholar'] = 8

    if efficiency_pct < 60:
        scores['erratic'] = 10
        scores['chaos_agent'] = 9
    if efficiency_pct < 70 and scoring_variance >= 300:
        scores['indecisive'] = 7

    # ========================================================================
    # CONSISTENCY (increased weight)
    # ========================================================================
    if scoring_variance < 150 and efficiency_pct >= 75:
        scores['rock'] = 11
        scores['steady_hand'] = 10
        scores['fundamentalist'] = 9

    if scoring_variance >= 400:
        scores['boom_bust'] = 11
        scores['rollercoaster'] = 10
    if scoring_variance >= 350 and efficiency_pct < 70:
        scores['unpredictable'] = 9

    # ========================================================================
    # ROSTER PHILOSOPHY
    # ========================================================================
    # Hoarder: low drops relative to adds
    drops = transactions - waiver_adds - (trades * 2)  # Rough estimate
    if waiver_adds >= 10 and drops <= 5:
        scores['collector'] = 8
        scores['protector'] = 7

    # Churner: high add/drop ratio
    if waiver_adds >= 15:
        scores['streamer'] = 8
        scores['hot_hand'] = 7

    # ========================================================================
    # SPECIAL ARCHETYPES (only awarded in specific scenarios)
    # ========================================================================

    # Survivor: finished poorly with low engagement
    if final_rank >= 10 and transactions <= 8:
        scores['survivor'] = 12

    # Underachiever: strong team (allplay) but poor results
    if allplay_rank <= 5 and not made_playoffs:
        scores['underachiever'] = 15

    # Overachiever: weak team (allplay) but good results
    if allplay_rank >= 10 and made_playoffs:
        scores['overachiever'] = 15

    # Tragic Figure: top 3 in scoring but missed playoffs
    if pf_rank <= 3 and not made_playoffs:
        scores['tragic_figure'] = 15

    # Inevitable: dominated in both allplay and actual record
    if allplay_rank == 1 and final_rank <= 2:
        scores['inevitable'] = 15

    # Pretender: playoffs despite weak allplay
    if made_playoffs and allplay_rank >= 8:
        scores['pretender'] = 15

    # ========================================================================
    # SELECT ARCHETYPE WITH HIGHEST SCORE
    # ========================================================================

    if not scores:
        # Default: assign based on final rank
        if final_rank <= 3:
            selected_id = 'rock'
        elif final_rank >= 12:
            selected_id = 'survivor'
        else:
            selected_id = 'steady_hand'
    else:
        # Get archetype with highest score
        selected_id = max(scores, key=scores.get)

    # Return full archetype data
    archetype = ARCHETYPES[selected_id].copy()
    return archetype
