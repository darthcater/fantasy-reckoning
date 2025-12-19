"""
Achievement & Badge System for Card V: The Legacy
Defines all badges (honors) and marks (shames) that managers can earn
"""

# ====================================================================================
# ACHIEVEMENT DEFINITIONS
# Each achievement has:
# - id: unique identifier
# - name: display name
# - description: what it means
# - type: 'badge' (good) or 'mark' (bad)
# - category: which aspect of play
# - tier: rank within category (1=lowest, 4=highest)
# - icon: suggested emoji/symbol for visual
# ====================================================================================

ACHIEVEMENTS = {
    # ================================================================================
    # TRADING PROWESS
    # ================================================================================
    'trade_emperor': {
        'id': 'trade_emperor',
        'name': 'Trade Emperor',
        'description': 'Dominated the league through masterful trades',
        'type': 'badge',
        'category': 'trading',
        'tier': 4,
        'icon': '👑',
        'criteria': lambda data: (
            data.get('trade_count', 0) >= 5 and
            data.get('trade_rank', 14) <= 3
        )
    },
    'trade_baron': {
        'id': 'trade_baron',
        'name': 'Trade Baron',
        'description': 'Built a dynasty through shrewd dealings',
        'type': 'badge',
        'category': 'trading',
        'tier': 3,
        'icon': '🏆',
        'criteria': lambda data: (
            data.get('trade_count', 0) >= 3 and
            data.get('trade_net_impact', 0) >= 20
        )
    },
    'trade_merchant': {
        'id': 'trade_merchant',
        'name': 'Trade Merchant',
        'description': 'Found profit in the marketplace of talent',
        'type': 'badge',
        'category': 'trading',
        'tier': 2,
        'icon': '💰',
        'criteria': lambda data: (
            data.get('trade_count', 0) >= 2 and
            data.get('trade_net_impact', 0) > 0
        )
    },
    'trade_novice': {
        'id': 'trade_novice',
        'name': 'Trade Novice',
        'description': 'Dipped a toe into the trading waters',
        'type': 'badge',
        'category': 'trading',
        'tier': 1,
        'icon': '🤝',
        'criteria': lambda data: (
            data.get('trade_count', 0) == 1 and
            data.get('trade_net_impact', 0) >= 0
        )
    },
    'eternally_swindled': {
        'id': 'eternally_swindled',
        'name': 'The Eternally Swindled',
        'description': 'Lost the league\'s most lopsided trades',
        'type': 'mark',
        'category': 'trading',
        'tier': 4,
        'icon': '⛓️',
        'criteria': lambda data: (
            data.get('trade_count', 0) >= 2 and
            data.get('trade_rank', 14) == 14
        )
    },
    'brand_of_ruin': {
        'id': 'brand_of_ruin',
        'name': 'Brand of Ruin',
        'description': 'Surrendered great value through foolish trades',
        'type': 'mark',
        'category': 'trading',
        'tier': 3,
        'icon': '🔥',
        'criteria': lambda data: (
            data.get('trade_count', 0) >= 1 and
            data.get('trade_net_impact', 0) <= -30
        )
    },
    'mark_of_the_fleeced': {
        'id': 'mark_of_the_fleeced',
        'name': 'Mark of the Fleeced',
        'description': 'Got the worse end of the bargain',
        'type': 'mark',
        'category': 'trading',
        'tier': 2,
        'icon': '⚠️',
        'criteria': lambda data: (
            data.get('trade_count', 0) >= 1 and
            data.get('trade_net_impact', 0) < 0
        )
    },

    # ================================================================================
    # WAIVER WIRE MASTERY
    # ================================================================================
    'wire_lord': {
        'id': 'wire_lord',
        'name': 'Lord of the Wire',
        'description': 'None claimed treasure from waivers like you',
        'type': 'badge',
        'category': 'waivers',
        'tier': 4,
        'icon': '⚡',
        'criteria': lambda data: data.get('waiver_rank', 14) == 1
    },
    'waiver_predator': {
        'id': 'waiver_predator',
        'name': 'Waiver Predator',
        'description': 'Stalked the wire with deadly precision',
        'type': 'badge',
        'category': 'waivers',
        'tier': 3,
        'icon': '🦅',
        'criteria': lambda data: data.get('waiver_rank', 14) <= 3
    },
    'waiver_hunter': {
        'id': 'waiver_hunter',
        'name': 'Waiver Hunter',
        'description': 'Found consistent value on the wire',
        'type': 'badge',
        'category': 'waivers',
        'tier': 2,
        'icon': '🎯',
        'criteria': lambda data: (
            data.get('waiver_points', 0) >= 30 or
            data.get('waiver_rank', 14) <= 7
        )
    },
    'waiver_wanderer': {
        'id': 'waiver_wanderer',
        'name': 'Waiver Wanderer',
        'description': 'Discovered a gem or two on the wire',
        'type': 'badge',
        'category': 'waivers',
        'tier': 1,
        'icon': '🔍',
        'criteria': lambda data: data.get('waiver_points', 0) >= 15
    },
    'costly_dropper': {
        'id': 'costly_dropper',
        'name': 'The Costly Dropper',
        'description': 'Armed thy enemies with dropped talent',
        'type': 'mark',
        'category': 'waivers',
        'tier': 4,
        'icon': '💀',
        'criteria': lambda data: data.get('costly_drops', 0) >= 100
    },
    'brand_of_the_blind': {
        'id': 'brand_of_the_blind',
        'name': 'Brand of the Blind',
        'description': 'Active on waivers, yet blind to value',
        'type': 'mark',
        'category': 'waivers',
        'tier': 3,
        'icon': '🔴',
        'criteria': lambda data: (
            data.get('waiver_moves', 0) >= 10 and
            data.get('waiver_rank', 14) >= 12
        )
    },
    'mark_of_missed_chances': {
        'id': 'mark_of_missed_chances',
        'name': 'Mark of Missed Chances',
        'description': 'Let opportunity slip through idle hands',
        'type': 'mark',
        'category': 'waivers',
        'tier': 2,
        'icon': '⏳',
        'criteria': lambda data: (
            data.get('waiver_moves', 0) <= 5 and
            data.get('waiver_rank', 14) >= 10
        )
    },

    # ================================================================================
    # DRAFT EXCELLENCE
    # ================================================================================
    'master_of_draft_table': {
        'id': 'master_of_draft_table',
        'name': 'Master of the Draft Table',
        'description': 'Crafted the league\'s finest draft',
        'type': 'badge',
        'category': 'draft',
        'tier': 4,
        'icon': '🎖️',
        'criteria': lambda data: data.get('draft_rank', 14) == 1
    },
    'draft_savant': {
        'id': 'draft_savant',
        'name': 'Draft Savant',
        'description': 'Drafted with wisdom and foresight',
        'type': 'badge',
        'category': 'draft',
        'tier': 3,
        'icon': '📜',
        'criteria': lambda data: data.get('draft_rank', 14) <= 3
    },
    'draft_strategist': {
        'id': 'draft_strategist',
        'name': 'Draft Strategist',
        'description': 'Selected talent with careful planning',
        'type': 'badge',
        'category': 'draft',
        'tier': 2,
        'icon': '⚔️',
        'criteria': lambda data: data.get('draft_rank', 14) <= 5
    },
    'draft_dabbler': {
        'id': 'draft_dabbler',
        'name': 'Draft Dabbler',
        'description': 'Found respectable value at the draft',
        'type': 'badge',
        'category': 'draft',
        'tier': 1,
        'icon': '📋',
        'criteria': lambda data: data.get('draft_rank', 14) <= 10
    },
    'the_ruinous_draft': {
        'id': 'the_ruinous_draft',
        'name': 'The Ruinous Draft',
        'description': 'Built a foundation of sand and disappointment',
        'type': 'mark',
        'category': 'draft',
        'tier': 4,
        'icon': '💩',
        'criteria': lambda data: data.get('draft_rank', 14) == 14
    },
    'brand_of_wasted_coin': {
        'id': 'brand_of_wasted_coin',
        'name': 'Brand of Wasted Coin',
        'description': 'Squandered coin on empty promises',
        'type': 'mark',
        'category': 'draft',
        'tier': 3,
        'icon': '🪙',
        'criteria': lambda data: (
            data.get('draft_type', '') == 'AUCTION' and
            data.get('draft_rank', 14) >= 12
        )
    },
    'mark_of_poor_preparation': {
        'id': 'mark_of_poor_preparation',
        'name': 'Mark of Poor Preparation',
        'description': 'Stumbled through the draft unprepared',
        'type': 'mark',
        'category': 'draft',
        'tier': 2,
        'icon': '📉',
        'criteria': lambda data: data.get('draft_rank', 14) >= 10
    },

    # ================================================================================
    # LINEUP MANAGEMENT
    # ================================================================================
    'perfect_seer': {
        'id': 'perfect_seer',
        'name': 'The Perfect Seer',
        'description': 'Set lineups with supernatural precision',
        'type': 'badge',
        'category': 'lineup',
        'tier': 4,
        'icon': '🔮',
        'criteria': lambda data: data.get('efficiency_pct', 0) >= 90
    },
    'lineup_sage': {
        'id': 'lineup_sage',
        'name': 'Lineup Sage',
        'description': 'Managed thy lineup with great wisdom',
        'type': 'badge',
        'category': 'lineup',
        'tier': 3,
        'icon': '🧙',
        'criteria': lambda data: data.get('efficiency_pct', 0) >= 85
    },
    'keeper_of_order': {
        'id': 'keeper_of_order',
        'name': 'Keeper of Order',
        'description': 'Maintained discipline in thy lineup choices',
        'type': 'badge',
        'category': 'lineup',
        'tier': 2,
        'icon': '⚖️',
        'criteria': lambda data: data.get('efficiency_pct', 0) >= 80
    },
    'steady_hand': {
        'id': 'steady_hand',
        'name': 'Steady Hand',
        'description': 'Set lineups with reliable consistency',
        'type': 'badge',
        'category': 'lineup',
        'tier': 1,
        'icon': '🤲',
        'criteria': lambda data: data.get('efficiency_pct', 0) >= 70
    },
    'the_perpetually_wrong': {
        'id': 'the_perpetually_wrong',
        'name': 'The Perpetually Wrong',
        'description': 'Started the wrong players week after week',
        'type': 'mark',
        'category': 'lineup',
        'tier': 4,
        'icon': '🤦',
        'criteria': lambda data: data.get('efficiency_pct', 0) < 50
    },
    'brand_of_bench_folly': {
        'id': 'brand_of_bench_folly',
        'name': 'Brand of Bench Folly',
        'description': 'Left thy best players rotting on the bench',
        'type': 'mark',
        'category': 'lineup',
        'tier': 3,
        'icon': '🪑',
        'criteria': lambda data: data.get('efficiency_pct', 0) < 60
    },
    'mark_of_indecision': {
        'id': 'mark_of_indecision',
        'name': 'Mark of Indecision',
        'description': 'Second-guessed thyself into suboptimal lineups',
        'type': 'mark',
        'category': 'lineup',
        'tier': 2,
        'icon': '🤷',
        'criteria': lambda data: data.get('efficiency_pct', 0) < 70
    },

    # ================================================================================
    # SEASON PERFORMANCE
    # ================================================================================
    'champion_eternal': {
        'id': 'champion_eternal',
        'name': 'Champion Eternal',
        'description': 'Ascended to the throne of glory',
        'type': 'badge',
        'category': 'performance',
        'tier': 4,
        'icon': '🏆',
        'criteria': lambda data: data.get('won_championship', False)
    },
    'playoff_warrior': {
        'id': 'playoff_warrior',
        'name': 'Playoff Warrior',
        'description': 'Earned thy place among the elite',
        'type': 'badge',
        'category': 'performance',
        'tier': 3,
        'icon': '⚔️',
        'criteria': lambda data: data.get('made_playoffs', False)
    },
    'worthy_contender': {
        'id': 'worthy_contender',
        'name': 'Worthy Contender',
        'description': 'Competed with honor throughout the season',
        'type': 'badge',
        'category': 'performance',
        'tier': 2,
        'icon': '🛡️',
        'criteria': lambda data: data.get('final_rank', 14) <= 8
    },
    'the_forsaken': {
        'id': 'the_forsaken',
        'name': 'The Forsaken',
        'description': 'Abandoned by fortune, skill, and the gods',
        'type': 'mark',
        'category': 'performance',
        'tier': 4,
        'icon': '☠️',
        'criteria': lambda data: data.get('final_rank', 14) == 14
    },
    'brand_of_last_place': {
        'id': 'brand_of_last_place',
        'name': 'Brand of Last Place',
        'description': 'Dwelt among the dregs of the standings',
        'type': 'mark',
        'category': 'performance',
        'tier': 3,
        'icon': '⬇️',
        'criteria': lambda data: data.get('final_rank', 14) >= 12
    },
    'mark_of_mediocrity': {
        'id': 'mark_of_mediocrity',
        'name': 'Mark of Mediocrity',
        'description': 'Neither champion nor condemned, just... there',
        'type': 'mark',
        'category': 'performance',
        'tier': 2,
        'icon': '😐',
        'criteria': lambda data: (
            data.get('final_rank', 14) >= 9 and
            data.get('final_rank', 14) <= 11
        )
    },

    # ================================================================================
    # CONSISTENCY & SCORING POWER
    # ================================================================================
    'rock_of_ages': {
        'id': 'rock_of_ages',
        'name': 'Rock of Ages',
        'description': 'Scored with unwavering consistency',
        'type': 'badge',
        'category': 'consistency',
        'tier': 4,
        'icon': '🗿',
        'criteria': lambda data: (
            data.get('scoring_variance', 100) < 150 and
            data.get('ppg', 0) >= 100
        )
    },
    'reliable_pillar': {
        'id': 'reliable_pillar',
        'name': 'Reliable Pillar',
        'description': 'Provided steady scoring week to week',
        'type': 'badge',
        'category': 'consistency',
        'tier': 2,
        'icon': '🏛️',
        'criteria': lambda data: data.get('scoring_variance', 100) < 200
    },
    'mark_of_chaos': {
        'id': 'mark_of_chaos',
        'name': 'Mark of Chaos',
        'description': 'Swung wildly between triumph and disaster',
        'type': 'mark',
        'category': 'consistency',
        'tier': 3,
        'icon': '🌪️',
        'criteria': lambda data: data.get('scoring_variance', 0) >= 300
    },
    'the_unpredictable': {
        'id': 'the_unpredictable',
        'name': 'The Unpredictable',
        'description': 'None could forecast thy chaos',
        'type': 'mark',
        'category': 'consistency',
        'tier': 4,
        'icon': '🎲',
        'criteria': lambda data: data.get('scoring_variance', 0) >= 400
    },

    # ================================================================================
    # SPECIAL ACHIEVEMENTS
    # ================================================================================
    'iron_throne': {
        'id': 'iron_throne',
        'name': 'The Iron Throne',
        'description': 'Ruled as points leader from start to finish',
        'type': 'badge',
        'category': 'special',
        'tier': 4,
        'icon': '👑',
        'criteria': lambda data: (
            data.get('pf_rank', 14) == 1 and
            data.get('final_rank', 14) <= 3
        )
    },
    'glass_cannon': {
        'id': 'glass_cannon',
        'name': 'The Glass Cannon',
        'description': 'Scored mightily, yet fell to misfortune',
        'type': 'badge',
        'category': 'special',
        'tier': 3,
        'icon': '💥',
        'criteria': lambda data: (
            data.get('pf_rank', 14) <= 3 and
            not data.get('made_playoffs', False)
        )
    },
    'schedule_blessed': {
        'id': 'schedule_blessed',
        'name': 'The Schedule-Blessed',
        'description': 'The gods smiled upon thy matchups',
        'type': 'badge',
        'category': 'special',
        'tier': 2,
        'icon': '🍀',
        'criteria': lambda data: (
            data.get('allplay_rank', 14) >= 8 and
            data.get('made_playoffs', False)
        )
    },
    'mark_of_stolen_valor': {
        'id': 'mark_of_stolen_valor',
        'name': 'Mark of Stolen Valor',
        'description': 'Stumbled into playoffs despite weakness',
        'type': 'mark',
        'category': 'special',
        'tier': 3,
        'icon': '🎭',
        'criteria': lambda data: (
            data.get('allplay_rank', 14) >= 10 and
            data.get('made_playoffs', False)
        )
    },
    'schedule_cursed': {
        'id': 'schedule_cursed',
        'name': 'The Schedule-Cursed',
        'description': 'Faced the strongest foes week after week',
        'type': 'mark',
        'category': 'special',
        'tier': 3,
        'icon': '🗡️',
        'criteria': lambda data: (
            data.get('allplay_rank', 14) <= 6 and
            not data.get('made_playoffs', False)
        )
    },
}


def evaluate_manager_achievements(calc, team_key: str, other_cards: dict = None) -> list:
    """
    Evaluate a manager across all achievement criteria and select the 3 most relevant.

    Returns a list of 3 achievement dicts, mixing badges and marks based on performance.
    """
    if other_cards is None:
        other_cards = {}

    # Gather all necessary data for achievement evaluation
    card_1 = other_cards.get('card_1_reckoning', {})
    card_2 = other_cards.get('card_2_ledger', {})
    card_3 = other_cards.get('card_3_campaign', {})
    card_4 = other_cards.get('card_4_design', {})

    team = calc.teams[team_key]
    team_stats = calc.calculate_team_stats_from_weekly_data(team_key)

    # Build data dict for achievement criteria
    achievement_data = {
        # Trading
        'trade_count': len(card_2.get('trades', {}).get('all_trades', [])),
        'trade_net_impact': card_2.get('trades', {}).get('net_started_impact', 0),
        'trade_rank': card_2.get('trades', {}).get('rank', 14),

        # Waivers
        'waiver_points': card_2.get('waivers', {}).get('total_points_started', 0),
        'waiver_moves': len(card_2.get('waivers', {}).get('adds', [])),
        'waiver_rank': card_1.get('dimension_breakdown', {}).get('waivers', {}).get('rank', 14),
        'costly_drops': card_2.get('costly_drops', {}).get('total_value_given_away', 0),

        # Draft
        'draft_rank': card_2.get('draft', {}).get('rank', 14),
        'draft_type': calc.league.get('draft_type', ''),

        # Lineup
        'efficiency_pct': card_3.get('efficiency', {}).get('lineup_efficiency_pct', 0),

        # Performance
        'won_championship': team_stats.get('won_championship', False),
        'made_playoffs': team_stats.get('made_playoffs', False),
        'final_rank': team_stats.get('final_rank', 14),

        # Scoring
        'pf_rank': card_4.get('scoring_power', {}).get('rank', 14),
        'ppg': team_stats.get('points_for', 0) / max(calc.league.get('current_week', 1), 1),
        'scoring_variance': card_4.get('scoring_power', {}).get('variance', 0),

        # All-play
        'allplay_rank': card_4.get('true_strength', {}).get('all_play_record', {}).get('rank', 14),
    }

    # Evaluate all achievements
    earned_achievements = []
    for ach_id, ach in ACHIEVEMENTS.items():
        try:
            if ach['criteria'](achievement_data):
                # Create a copy without the criteria function (for JSON serialization)
                ach_clean = {k: v for k, v in ach.items() if k != 'criteria'}
                earned_achievements.append(ach_clean)
        except Exception as e:
            # Skip if criteria evaluation fails
            continue

    # Select the 3 most relevant achievements
    # Prioritize by tier (higher tier = more important)
    # Ensure a mix of badges and marks when possible

    earned_achievements.sort(key=lambda x: x['tier'], reverse=True)

    badges = [a for a in earned_achievements if a['type'] == 'badge']
    marks = [a for a in earned_achievements if a['type'] == 'mark']

    selected = []

    # Strategy: Pick highest tier achievements, but ensure variety
    # Strong seasons: 2-3 badges, 0-1 marks
    # Weak seasons: 0-1 badges, 2-3 marks
    # Average: 1-2 of each

    if len(badges) >= 3 and len(marks) == 0:
        # Great season - all badges
        selected = badges[:3]
    elif len(marks) >= 3 and len(badges) == 0:
        # Terrible season - all marks
        selected = marks[:3]
    elif len(badges) >= 2 and len(marks) >= 1:
        # Good season - 2 badges, 1 mark
        selected = badges[:2] + marks[:1]
    elif len(badges) >= 1 and len(marks) >= 2:
        # Poor season - 1 badge, 2 marks
        selected = badges[:1] + marks[:2]
    else:
        # Mixed - take whatever we have
        selected = earned_achievements[:3]

    # Ensure we have exactly 3
    while len(selected) < 3:
        selected.append({
            'id': 'participant',
            'name': 'Participant',
            'description': 'You were there',
            'type': 'badge',
            'category': 'participation',
            'tier': 1,
            'icon': '📌'
        })

    return selected[:3]
