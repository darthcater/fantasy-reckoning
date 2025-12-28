#!/usr/bin/env python3
"""
Generate Homepage Card Previews

Updates the website/index.html with sample card preview data.
Only modifies the section between CARD_PREVIEWS_START and CARD_PREVIEWS_END markers.
All other homepage content (hero, how it works, pricing, footer) remains untouched.

Edit SAMPLE_DATA below to change what appears on the homepage.
"""

import re
from pathlib import Path


def ordinal(n: int) -> str:
    """Return ordinal suffix for a number (1st, 2nd, 3rd, 4th, etc.)."""
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


# ============================================================================
# SAMPLE DATA FOR HOMEPAGE PREVIEWS
# Edit this to change what appears on the homepage card previews
# ============================================================================
SAMPLE_DATA = {
    'cards': {
        'card_1_overview': {
            'archetype': {
                'name': 'The Tinkerer',
                'description': 'Constantly adjusting, never satisfied with thy roster'
            },
            'dimension_breakdown': {
                'draft': {'percentile': 8},
                'lineups': {'percentile': 31},
                'bye_week': {'percentile': 62},
                'waivers': {'percentile': 85}
            },
            'overall_percentile': 38
        },
        'card_2_ledger': {
            'draft': {'total_points': 1352, 'rank': 13},
            'waivers': {'total_points_started': 203, 'rank': 3},
            'trades': {'net_started_impact': 0, 'rank': 7},
            'costly_drops': {'total_value_given_away': 0, 'rank': 9, 'most_costly_drop': {}},
            'steals': [{'player_name': 'Bryce Young', 'cost': 2, 'points': 196, 'value': 97.8}],
            'busts': [{'player_name': 'George Kittle', 'cost': 29, 'points': 106, 'value': 3.7}],
            'best_adds': [{'player_name': 'Woody Marks', 'points_started': 65.4, 'weeks_started': 7}]
        },
        'card_3_lineups': {
            'efficiency': {
                'lineup_efficiency_pct': 89.6,
                'total_bench_points_left': 169.4
            },
            'timelines': {
                'actual': {'record': '7-7'},
                'optimal_lineup': {'record': '10-4'}
            },
            'pivotal_moments': {
                'moment_type': 'fatal_error',
                'the_fatal_error': {
                    'week': 4,
                    'started_player': 'Trey Benson',
                    'started_points': 7.9,
                    'benched_player': 'Woody Marks',
                    'benched_points': 25.9,
                    'margin': 6.5
                },
                'the_clutch_call': {}
            }
        },
        'card_4_story': {
            'win_attribution': {
                'true_skill_record': '6-8',
                'luck_factors': [
                    {
                        'factor': 'Schedule Luck',
                        'impact': 0,
                        'narrative': ['Average schedule difficulty']
                    },
                    {
                        'factor': 'Opponent Mistakes',
                        'impact': 1,
                        'narrative': ['Week 7: Won by 14.7 pts, opponent left 21.5 on bench']
                    }
                ],
                'agent_of_chaos': {
                    'player_name': 'Bryce Young',
                    'week': 11,
                    'points': 38,
                    'deviation': 22,
                    'result': 'W',
                    'win_impact': 'won you the game'
                }
            }
        }
    }
}


def load_sample_data():
    """Return hardcoded sample data for homepage previews."""
    return SAMPLE_DATA


def generate_card_1_overview(data: dict) -> str:
    """Generate Card 1: The Leader (Overview) preview HTML."""
    card = data['cards']['card_1_overview']
    archetype = card['archetype']
    dims = card['dimension_breakdown']
    overall_pct = card['overall_percentile']

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Leader</h3>
                <p class="card-description">How you played and stacked up against your rivals</p>

                <div class="card-data">
                    <div style="margin-bottom: 1rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em;">MANAGER ARCHETYPE</div>
                        <div style="text-align: center;">
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{archetype['name']}</div>
                            <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem; font-style: italic;">{archetype['description']}</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em;">SKILL PERCENTILES VS LEAGUE</div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Draft Performance</span>
                                <span>{dims['draft']['percentile']:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {dims['draft']['percentile']:.0f}%;"></div>
                            </div>
                        </div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Lineup Efficiency</span>
                                <span>{dims['lineups']['percentile']:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {dims['lineups']['percentile']:.0f}%;"></div>
                            </div>
                        </div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Bye Week Management</span>
                                <span>{dims['bye_week']['percentile']:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {dims['bye_week']['percentile']:.0f}%;"></div>
                            </div>
                        </div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Waiver Activity</span>
                                <span>{dims['waivers']['percentile']:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {dims['waivers']['percentile']:.0f}%;"></div>
                            </div>
                        </div>

                        <!-- Overall Weighted Percentile -->
                        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">
                            <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.5rem;">OVERALL PERCENTILE</div>
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.5rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{overall_pct:.0f}th</div>
                        </div>
                    </div>
                </div>
            </div>'''


def generate_card_2_ledger(data: dict) -> str:
    """Generate Card 2: The Ledger preview HTML."""
    card = data['cards']['card_2_ledger']
    draft = card['draft']
    waivers = card['waivers']
    trades = card['trades']
    costly = card['costly_drops']

    # Get best steal and bust (check both card level and nested in draft/waivers)
    steals = card.get('steals') or draft.get('steals', [])
    busts = card.get('busts') or draft.get('busts', [])
    best_adds = card.get('best_adds') or waivers.get('best_adds', [])

    steal = steals[0] if steals else None
    bust = busts[0] if busts else None
    best_add = best_adds[0] if best_adds else None

    # Format trade impact
    trade_impact = trades['net_started_impact']
    trade_color = '#6fa86f' if trade_impact >= 0 else '#c96c6c'
    trade_sign = '+' if trade_impact >= 0 else ''

    # Format costly drops
    costly_value = costly['total_value_given_away']

    # Prepare formatted values
    steal_name = steal['player_name'] if steal else 'N/A'
    steal_cost = steal['cost'] if steal else 0
    steal_pts = f"{steal['points']:.0f}" if steal else "0"
    steal_value = f"{steal['value']:.1f}" if steal else "0"

    bust_name = bust['player_name'] if bust else 'N/A'
    bust_cost = bust['cost'] if bust else 0
    bust_pts = f"{bust['points']:.0f}" if bust else "0"
    bust_value = f"{bust['value']:.1f}" if bust else "0"

    add_name = best_add['player_name'] if best_add else 'N/A'
    add_pts = f"{best_add['points_started']:.1f}" if best_add else "0"
    add_weeks = best_add['weeks_started'] if best_add else 0

    drop_name = costly.get('most_costly_drop', {}).get('player_name', 'None')
    drop_pts = costly.get('most_costly_drop', {}).get('points_to_opponent', 0)

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Ledger</h3>
                <p class="card-description">Where your points came from (and where they went)</p>

                <div class="card-data">
                    <div style="margin-bottom: 1.5rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em;">YOUR BALANCE</div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Draft</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{draft['total_points']:,.0f} pts <span style="opacity: 0.6; font-size: 0.8rem;">({ordinal(draft['rank'])})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Waivers</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{waivers['total_points_started']:,.0f} pts <span style="opacity: 0.6; font-size: 0.8rem;">({ordinal(waivers['rank'])})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Trades</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: {trade_color};">{trade_sign}{trade_impact} pts <span style="opacity: 0.6; font-size: 0.8rem;">({ordinal(trades['rank'])})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Costly Drops</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #c96c6c;">-{costly_value} pts <span style="opacity: 0.6; font-size: 0.8rem;">({ordinal(costly['rank'])})</span></span>
                        </div>
                    </div>

                    <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em;">KEY MOVES</div>

                        <div class="key-moves-grid">
                            <div class="key-move-item">
                                <div class="key-move-header">Best Value</div>
                                <div class="key-move-player">{steal_name} - ${steal_cost}</div>
                                <div class="key-move-stat" style="opacity: 0.8;">{steal_pts} pts<br><span style="color: #6fa86f;">{steal_value} pts/$</span></div>
                            </div>

                            <div class="key-move-item">
                                <div class="key-move-header">Biggest Bust</div>
                                <div class="key-move-player">{bust_name} - ${bust_cost}</div>
                                <div class="key-move-stat" style="opacity: 0.8;">{bust_pts} pts<br><span style="color: #c96c6c;">{bust_value} pts/$</span></div>
                            </div>

                            <div class="key-move-item">
                                <div class="key-move-header">Best Waiver</div>
                                <div class="key-move-player">{add_name}</div>
                                <div class="key-move-stat" style="opacity: 0.8;"><span style="color: #6fa86f;">{add_pts} pts</span><br>{add_weeks} weeks</div>
                            </div>

                            <div class="key-move-item">
                                <div class="key-move-header">Costly Drop</div>
                                <div class="key-move-player">{drop_name}</div>
                                <div class="key-move-stat" style="opacity: 0.8;"><span style="color: #c96c6c;">{drop_pts} pts</span> to opponent</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>'''


def generate_card_3_lineups(data: dict) -> str:
    """Generate Card 3: The Lineup preview HTML."""
    card = data['cards']['card_3_lineups']
    eff = card['efficiency']
    timelines = card['timelines']
    pivotal = card['pivotal_moments']

    # Determine if showing fatal error or clutch call
    moment_type = pivotal['moment_type']
    is_fatal = moment_type == 'fatal_error'
    moment = pivotal.get('the_fatal_error' if is_fatal else 'the_clutch_call', {})

    moment_html = ''
    if moment:
        section_title = 'FATAL ERROR' if is_fatal else 'CLUTCH CALL'
        started_color = '#c96c6c' if is_fatal else '#6fa86f'
        benched_color = '#6fa86f' if is_fatal else '#c96c6c'
        margin_label = 'Lost by' if is_fatal else 'Won by'
        margin_color = '#c96c6c' if is_fatal else '#6fa86f'

        moment_html = f'''
                    <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em;">{section_title}</div>

                        <div style="padding: 1.25rem; text-align: center;">
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.1rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; margin-bottom: 0.75rem;">Week {moment.get('week', '?')}</div>

                            <div style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; line-height: 1.8; opacity: 0.9;">
                                <div>Started: <span style="text-transform: uppercase; color: #b8864f;">{moment.get('started_player', 'N/A')}</span> (<span style="color: {started_color};">{moment.get('started_points', 0):.1f} pts</span>)</div>
                                <div>Benched: <span style="text-transform: uppercase; color: #b8864f;">{moment.get('benched_player', 'N/A')}</span> (<span style="color: {benched_color};">{moment.get('benched_points', 0):.1f} pts</span>)</div>
                                <div>{margin_label}: <span style="color: {margin_color};">{moment.get('margin', 0):.1f} pts</span></div>
                            </div>
                        </div>
                    </div>'''

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Lineup</h3>
                <p class="card-description">How you played your pieces on the board</p>

                <div class="card-data">
                    <div style="margin-bottom: 1.5rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em;">THE DEPLOYMENT</div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Lineup Efficiency</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{eff['lineup_efficiency_pct']:.1f}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Actual Record</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{timelines['actual']['record']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Perfect Lineups</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{timelines['optimal_lineup']['record']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Bench Points Wasted</span>
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{eff['total_bench_points_left']:.1f} pts</span>
                        </div>
                    </div>{moment_html}
                </div>
            </div>'''


def generate_card_4_story(data: dict) -> str:
    """Generate Card 4: The Legend preview HTML."""
    card = data['cards']['card_4_story']
    attr = card['win_attribution']

    true_skill = attr['true_skill_record']
    schedule_luck = attr['luck_factors'][0]
    opp_mistakes = attr['luck_factors'][1]
    agent = attr.get('agent_of_chaos')

    # Format luck impacts
    sched_impact = schedule_luck['impact']
    sched_color = '#6fa86f' if sched_impact >= 0 else '#c96c6c'
    sched_sign = '+' if sched_impact >= 0 else ''

    opp_impact = opp_mistakes['impact']
    opp_color = '#6fa86f' if opp_impact >= 0 else '#c96c6c'
    opp_sign = '+' if opp_impact >= 0 else ''

    # Schedule narrative
    sched_narrative = schedule_luck.get('narrative', ['Average schedule difficulty'])
    sched_narrative_html = '<br>'.join([f'&bull; {n}' for n in sched_narrative])

    # Opponent narrative
    opp_narrative = opp_mistakes.get('narrative', ['Opponents set optimal lineups'])
    opp_narrative_html = '<br>'.join([f'&bull; {n}' for n in opp_narrative[:2]])

    # Agent of chaos section
    agent_html = ''
    if agent:
        deviation = agent['deviation']
        dev_sign = '+' if deviation > 0 else ''
        result_color = '#6fa86f' if agent['result'] == 'W' else '#c96c6c'
        agent_html = f'''
                    <!-- Agent of Chaos -->
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-transform: uppercase; color: #e8d5b5;">Agent of Chaos</div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.9rem; opacity: 0.9; line-height: 1.6;">
                            <span style="color: #b8864f; font-weight: 600;">{agent['player_name']}</span>: {agent['points']:.0f} pts ({dev_sign}{deviation:.0f} vs avg)<br>
                            Week {agent['week']} &bull; <span style="color: {result_color};">{agent['win_impact']}</span>
                        </div>
                    </div>'''

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Legend</h3>
                <p class="card-description">How fate and folly intertwined</p>

                <div class="card-data">
                    <!-- Top Section: The Reckoning (True Skill Record) -->
                    <div style="margin-bottom: 1rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.5rem;">THE RECKONING</div>
                        <div style="text-align: center;">
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 2.5rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{true_skill}</div>
                            <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; opacity: 0.7; margin-top: 0.25rem;">Your true skill record, stripped of fortune's favor</div>
                        </div>
                    </div>

                    <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 1rem; letter-spacing: 0.05em; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">FORTUNE'S HAND</div>

                    <!-- Schedule Luck with Narrative -->
                    <div style="margin-top: 0; margin-bottom: 0.75rem;">
                        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-transform: uppercase;"><span style="color: #e8d5b5;">Schedule Luck:</span> <span style="color: {sched_color};">{sched_sign}{sched_impact:.0f} wins</span></div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; opacity: 0.8; line-height: 1.6;">
                            {sched_narrative_html}
                        </div>
                    </div>

                    <!-- Opponent Mistakes with Narrative -->
                    <div style="margin-bottom: 0.75rem;">
                        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-transform: uppercase;"><span style="color: #e8d5b5;">Opponent Blunders:</span> <span style="color: {opp_color};">{opp_sign}{opp_impact:.0f} wins</span></div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; opacity: 0.8; line-height: 1.6;">
                            {opp_narrative_html}
                        </div>
                    </div>{agent_html}
                </div>
            </div>'''


def generate_card_previews(data: dict) -> str:
    """Generate all 4 card previews HTML."""
    cards = [
        generate_card_1_overview(data),
        generate_card_2_ledger(data),
        generate_card_3_lineups(data),
        generate_card_4_story(data),
    ]

    return f'''        <!-- CARD_PREVIEWS_START -->
        <div class="cards-grid">
{chr(10).join(cards)}

        </div>
        <!-- CARD_PREVIEWS_END -->'''


def update_homepage():
    """Update homepage with real card preview data."""
    # Load Dobbs' Decision data
    data = load_sample_data()

    # Generate new card previews
    new_previews = generate_card_previews(data)

    # Read existing homepage
    homepage_path = Path(__file__).parent / "website" / "index.html"
    with open(homepage_path, 'r') as f:
        html = f.read()

    # Replace card previews section
    pattern = r'        <!-- CARD_PREVIEWS_START -->.*?<!-- CARD_PREVIEWS_END -->'
    updated_html = re.sub(pattern, new_previews, html, flags=re.DOTALL)

    # Write updated homepage
    with open(homepage_path, 'w') as f:
        f.write(updated_html)

    print("Homepage updated with sample card previews.")
    print(f"  - Archetype: {data['cards']['card_1_overview']['archetype']['name']}")
    print(f"  - True Skill Record: {data['cards']['card_4_story']['win_attribution']['true_skill_record']}")
    print("\nEdit SAMPLE_DATA in generate_homepage.py to change preview content.")


if __name__ == '__main__':
    update_homepage()
