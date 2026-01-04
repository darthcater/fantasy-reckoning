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
                'description': 'Constantly adjusting, never satisfied'
            },
            'dimension_breakdown': {
                'draft': {'percentile': 8},
                'lineups': {'percentile': 31},
                'bye_week': {'percentile': 62},
                'waivers': {'percentile': 85}
            },
            'overall_percentile': 46
        },
        'card_2_ledger': {
            'draft': {'total_points': 1352, 'rank': 13},
            'waivers': {'total_points_started': 516, 'rank': 2},
            'trades': {
                'net_started_impact': -3,
                'rank': 12,
                'rank_is_tied': False,
                'trades': [
                    {
                        'players_out': [{'player_name': 'Chuba Hubbard'}],
                        'players_in': [{'player_name': 'Tetairoa McMillan'}],
                        'net_started_impact': 61.7,
                        'rank': 3
                    },
                    {
                        'players_out': [{'player_name': 'Xavier Worthy'}],
                        'players_in': [{'player_name': 'Trey Benson'}],
                        'net_started_impact': -64.7,
                        'rank': 12
                    }
                ]
            },
            'costly_drops': {
                'total_value_given_away': 332,
                'rank': 8,
                'most_costly_drop': {
                    'player_name': 'Stefon Diggs',
                    'started_pts': 107,
                    'weeks_away': 12,
                    'rank': 4
                }
            },
            'steals': [{'player_name': 'Bryce Young', 'cost': 2, 'points': 196, 'value': 97.8, 'rank': 1}],
            'busts': [{'player_name': 'Travis Hunter', 'cost': 11, 'points': 50, 'value': 4.5, 'rank': 8}],
            'best_adds': [{'player_name': 'Jake Bates', 'points_started': 97, 'weeks_started': 13, 'rank': 5}]
        },
        'card_3_lineups': {
            'efficiency': {
                'lineup_efficiency_pct': 89.6,
                'league_rank_numeric': 7
            },
            'position_units': {
                'strongest': {'position': 'QB', 'rank': 6},
                'weakest': {'position': 'WR', 'rank': 12}
            },
            'timelines': {
                'actual': {'record': '7-7', 'rank': 8},
                'optimal_lineup': {'record': '10-4', 'rank': 4}
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
                'true_skill_record': '7-7',
                'luck_factors': [
                    {
                        'factor': 'Schedule Luck',
                        'impact': 0,
                        'narrative': ['Average schedule difficulty']
                    },
                    {
                        'factor': 'Opponent Mistakes',
                        'impact': 2,
                        'narrative': ['Week 7: Won by 14.7 pts, opponent left 21.5 on bench', 'Week 14: Won by 3.2 pts, opponent left 3.3 on bench']
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


def _percentile_color(pct: float) -> str:
    """Return color based on percentile: green for high, red for low, cream for middle."""
    if pct >= 67:
        return '#6fa86f'  # Green - top third
    elif pct <= 33:
        return '#c96c6c'  # Red - bottom third
    return '#e8d5b5'  # Cream - middle


def _rank_color(rank: int, num_teams: int = 14, invert: bool = False) -> str:
    """Get color based on rank (lower is better, unless inverted)."""
    if invert:
        # For negative metrics (bust, drop): high rank = good, low rank = bad
        if rank <= num_teams // 3:
            return '#c96c6c'  # Red - top third (bad for negative metrics)
        elif rank > num_teams - (num_teams // 3):
            return '#6fa86f'  # Green - bottom third (good for negative metrics)
        return '#e8d5b5'  # Cream - middle (neutral)
    else:
        # Normal: low rank = good, high rank = bad
        if rank <= num_teams // 3:
            return '#6fa86f'  # Green - top third (good)
        elif rank > num_teams - (num_teams // 3):
            return '#c96c6c'  # Red - bottom third (bad)
        return '#e8d5b5'  # Cream - middle (neutral)


def generate_card_1_overview(data: dict) -> str:
    """Generate Card 1: The Leader (Overview) preview HTML."""
    card = data['cards']['card_1_overview']
    archetype = card['archetype']
    dims = card['dimension_breakdown']
    overall_pct = card['overall_percentile']

    draft_pct = dims['draft']['percentile']
    lineups_pct = dims['lineups']['percentile']
    bye_week_pct = dims['bye_week']['percentile']
    waivers_pct = dims['waivers']['percentile']

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Leader</h3>
                <p class="card-description">Your management style measured</p>

                <div class="card-data">
                    <div style="margin-bottom: 0.75rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.35rem; letter-spacing: 0.05em; text-align: center;">MANAGER ARCHETYPE</div>
                        <div style="text-align: center;">
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{archetype['name']}</div>
                            <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8; margin-top: 0.2rem; font-style: italic;">{archetype['description']}</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">SKILL PERCENTILES VS LEAGUE</div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Draft Performance</span>
                                <span style="font-family: 'EB Garamond', serif;">{draft_pct:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {draft_pct:.0f}%;"></div>
                            </div>
                        </div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Lineup Efficiency</span>
                                <span style="font-family: 'EB Garamond', serif;">{lineups_pct:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {lineups_pct:.0f}%;"></div>
                            </div>
                        </div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Bye Week Management</span>
                                <span style="font-family: 'EB Garamond', serif;">{bye_week_pct:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {bye_week_pct:.0f}%;"></div>
                            </div>
                        </div>

                        <div class="dimension-row">
                            <div class="dimension-label">
                                <span>Waiver Activity</span>
                                <span style="font-family: 'EB Garamond', serif;">{waivers_pct:.0f}%</span>
                            </div>
                            <div class="dimension-bar">
                                <div class="dimension-fill" style="width: {waivers_pct:.0f}%;"></div>
                            </div>
                        </div>

                        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">
                            <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.35rem; text-align: center;">OVERALL PERCENTILE</div>
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{_ordinal(int(overall_pct))}</div>
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
    if trade_impact > 0:
        trade_color = '#6fa86f'
        trade_sign = '+'
    elif trade_impact < 0:
        trade_color = '#c96c6c'
        trade_sign = ''
    else:
        trade_color = '#e8d5b5'  # Neutral for zero
        trade_sign = ''

    # Format costly drops
    costly_value = costly['total_value_given_away']

    # Prepare formatted values for key moves table
    steal_name = steal['player_name'] if steal else '—'
    steal_cost = f" (${steal['cost']})" if steal and steal.get('cost') else ''
    steal_pts = f"{steal['points']:.0f}" if steal else '—'
    steal_value = f"{steal['value']:.1f}" if steal and steal.get('value') else '—'
    steal_rank = steal.get('rank', 0) if steal else 0

    bust_name = bust['player_name'] if bust else '—'
    bust_cost = f" (${bust['cost']})" if bust and bust.get('cost') else ''
    bust_pts = f"{bust['points']:.0f}" if bust else '—'
    bust_value = f"{bust['value']:.1f}" if bust and bust.get('value') else '—'
    bust_rank = bust.get('rank', 0) if bust else 0

    add_name = best_add['player_name'] if best_add else '—'
    add_pts = f"{best_add['points_started']:.0f}" if best_add else '—'
    add_rank = best_add.get('rank', 0) if best_add else 0

    # Trade Win/Loss logic - show Trade Win if any trade has positive impact
    trades_list = trades.get('trades', [])
    if trades_list:
        best_trade = max(trades_list, key=lambda t: t.get('net_started_impact', 0))
        worst_trade = min(trades_list, key=lambda t: t.get('net_started_impact', 0))
        if best_trade.get('net_started_impact', 0) > 0:
            featured_trade = best_trade
            trade_label = "Trade Win"
        else:
            featured_trade = worst_trade
            trade_label = "Trade Loss"
        # Format trade player names (with +N for multi-player trades)
        players_out = featured_trade.get('players_out', [])
        players_in = featured_trade.get('players_in', [])
        if players_out and players_in:
            out_full = players_out[0].get('player_name', '?') if isinstance(players_out[0], dict) else players_out[0]
            in_full = players_in[0].get('player_name', '?') if isinstance(players_in[0], dict) else players_in[0]
            # Use last names only for better fit
            out_name = out_full.split()[-1] if out_full else '?'
            in_name = in_full.split()[-1] if in_full else '?'
            # Add "+N" suffix for multi-player trades
            out_extra = f" +{len(players_out) - 1}" if len(players_out) > 1 else ""
            in_extra = f" +{len(players_in) - 1}" if len(players_in) > 1 else ""
            trade_player = f"{out_name}{out_extra} → {in_name}{in_extra}"
        else:
            trade_player = '—'
        trade_pts_val = featured_trade.get('net_started_impact', 0)
        # Add * indicator for multi-player trades
        is_multi = featured_trade.get('is_multi_player', False) or (len(players_out) != len(players_in))
        multi_indicator = "*" if is_multi else ""
        trade_pts = f"{'+' if trade_pts_val > 0 else ''}{trade_pts_val:.0f}{multi_indicator}" if trade_pts_val else f'0{multi_indicator}'
        trade_pts_color = '#6fa86f' if trade_pts_val >= 0 else '#c96c6c'
        trade_move_rank = featured_trade.get('rank', 0)
    else:
        trade_label = "Trade Win"  # Default label when no trades
        trade_player = '—'
        trade_pts = '—'
        trade_pts_color = '#e8d5b5'
        trade_move_rank = 0

    drop = costly.get('most_costly_drop', {})
    drop_name = drop.get('player_name', '—') if drop else '—'
    drop_pts_val = drop.get('started_pts', 0) or drop.get('points_to_opponent', 0) if drop else 0
    drop_pts = f"{drop_pts_val:.0f}" if drop_pts_val else '—'
    drop_rank = drop.get('rank', 0) if drop else 0

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Ledger</h3>
                <p class="card-description">Points earned, and points forsaken</p>

                <div class="card-data">
                    <div style="margin-bottom: 0.75rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.4rem; letter-spacing: 0.05em; text-align: center;">YOUR BALANCE</div>
                        <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Draft</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{draft['total_points']:,.0f} pts <span style="color: {_rank_color(draft['rank'])};">({_ordinal(draft['rank'])})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Waivers</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{waivers['total_points_started']:,.0f} pts <span style="color: {_rank_color(waivers['rank'])};">({_ordinal(waivers['rank'])})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Trades</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{trade_sign}{trade_impact} pts <span style="color: {_rank_color(trades['rank'])};">({_ordinal(trades['rank'])})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.3rem 0;">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Costly Drops</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">-{costly_value} pts <span style="color: {_rank_color(costly['rank'], invert=True)};">({_ordinal(costly['rank'])})</span></span>
                        </div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.7rem; opacity: 0.5; margin-top: 0.15rem; font-style: italic; text-align: right;">
                            points gifted to your rivals
                        </div>
                    </div>

                    <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.4rem; letter-spacing: 0.05em; text-align: center;">KEY MOVES</div>

                        <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 0.35rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; text-align: left;">Best Value</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600; text-align: center;">{steal_name}{steal_cost}</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #e8d5b5; text-align: right;">{steal_value} pts/${f' <span style="color: {_rank_color(steal_rank)};">({_ordinal(steal_rank)})</span>' if steal_rank > 0 else ''}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 0.35rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; text-align: left;">Biggest Bust</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600; text-align: center;">{bust_name}{bust_cost}</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #e8d5b5; text-align: right;">{bust_value} pts/${f' <span style="color: {_rank_color(bust_rank, invert=True)};">({_ordinal(bust_rank)})</span>' if bust_rank > 0 else ''}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 0.35rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; text-align: left;">Best Add</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600; text-align: center;">{add_name}</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #e8d5b5; text-align: right;">{add_pts} pts{f' <span style="color: {_rank_color(add_rank)};">({_ordinal(add_rank)})</span>' if add_rank > 0 else ''}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 0.35rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; text-align: left;">{trade_label}</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600; text-align: center;">{trade_player}</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #e8d5b5; text-align: right;">{trade_pts} pts{f' <span style="color: {_rank_color(trade_move_rank)};">({_ordinal(trade_move_rank)})</span>' if trade_move_rank > 0 else ''}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 0.35rem; padding: 0.3rem 0;">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; text-align: left;">Costly Drop</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600; text-align: center;">{drop_name}</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #e8d5b5; text-align: right;">{drop_pts} pts{f' <span style="color: {_rank_color(drop_rank, invert=True)};">({_ordinal(drop_rank)})</span>' if drop_rank > 0 else ''}</span>
                        </div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.7rem; opacity: 0.5; margin-top: 0.35rem; font-style: italic;">
                            Efficiency: pts/$, pts/start. *Multi-player trade.
                        </div>
                    </div>
                </div>
            </div>'''


def _ordinal(n: int) -> str:
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def generate_card_3_lineups(data: dict) -> str:
    """Generate Card 3: The Lineup preview HTML."""
    card = data['cards']['card_3_lineups']
    eff = card['efficiency']
    timelines = card['timelines']
    pivotal = card['pivotal_moments']

    # Get efficiency rank
    efficiency_rank = eff.get('league_rank_numeric', 0)

    # Get record ranks
    actual_record_rank = timelines['actual'].get('rank', 0)
    optimal_record_rank = timelines['optimal_lineup'].get('rank', 0)

    # Position units data
    position_units = card.get('position_units', {})
    strongest = position_units.get('strongest', {})
    weakest = position_units.get('weakest', {})

    pos_names = {'QB': 'QBs', 'RB': 'RBs', 'WR': 'WRs', 'TE': 'TEs'}
    strongest_pos = pos_names.get(strongest.get('position', ''), 'N/A')
    strongest_rank = strongest.get('rank', 0)
    weakest_pos = pos_names.get(weakest.get('position', ''), 'N/A')
    weakest_rank = weakest.get('rank', 0)

    # Color ranks: green for top 4, red for bottom 4, cream for middle
    def rank_color(rank, num_teams=12):
        if rank <= num_teams // 3:
            return '#6fa86f'  # Green - top third
        elif rank > num_teams - (num_teams // 3):
            return '#c96c6c'  # Red - bottom third
        return '#e8d5b5'  # Cream - middle

    # Determine if showing fatal error or clutch call
    moment_type = pivotal['moment_type']
    is_fatal = moment_type == 'fatal_error'
    moment = pivotal.get('the_fatal_error' if is_fatal else 'the_clutch_call', {})

    moment_html = ''
    if moment:
        section_title = 'THE BLUNDER' if is_fatal else 'THE RALLY'
        margin_label = 'Lost by' if is_fatal else 'Won by'

        moment_html = f'''
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">{section_title}</div>

                        <div style="padding: 0.75rem; text-align: center;">
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; margin-bottom: 0.5rem;">Week {moment.get('week', '?')}</div>

                            <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; line-height: 1.6; opacity: 0.9;">
                                <div>Started: <span style="color: #b8864f; font-weight: 600;">{moment.get('started_player', 'N/A')}</span> (<span style="color: #e8d5b5;">{moment.get('started_points', 0):.1f} pts</span>)</div>
                                <div>Benched: <span style="color: #b8864f; font-weight: 600;">{moment.get('benched_player', 'N/A')}</span> (<span style="color: #e8d5b5;">{moment.get('benched_points', 0):.1f} pts</span>)</div>
                                <div>{margin_label}: <span style="color: #e8d5b5;">{moment.get('margin', 0):.1f} pts</span></div>
                            </div>
                        </div>
                    </div>'''

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Lineup</h3>
                <p class="card-description">How you played your pieces on the board</p>

                <div class="card-data">
                    <div style="margin-bottom: 1rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">THE DEPLOYMENT</div>
                        <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Lineup Efficiency</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{eff['lineup_efficiency_pct']:.1f}%{f' <span style="color: {rank_color(efficiency_rank)};">({_ordinal(efficiency_rank)})</span>' if efficiency_rank > 0 else ''}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Actual Record</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{timelines['actual']['record']}{f' <span style="color: {rank_color(actual_record_rank)};">({_ordinal(actual_record_rank)})</span>' if actual_record_rank > 0 else ''}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Perfect Lineups</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{timelines['optimal_lineup']['record']}{f' <span style="color: {rank_color(optimal_record_rank)};">({_ordinal(optimal_record_rank)})</span>' if optimal_record_rank > 0 else ''}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Strongest Unit</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{strongest_pos} <span style="color: {rank_color(strongest_rank)};">({_ordinal(strongest_rank)})</span></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 0.35rem 0;">
                            <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Weakest Unit</span>
                            <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{weakest_pos} <span style="color: {rank_color(weakest_rank)};">({_ordinal(weakest_rank)})</span></span>
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

    # Format luck impacts - zero should be neutral
    sched_impact = schedule_luck['impact']
    if sched_impact > 0:
        sched_color = '#6fa86f'
        sched_sign = '+'
    elif sched_impact < 0:
        sched_color = '#c96c6c'
        sched_sign = ''
    else:
        sched_color = '#e8d5b5'
        sched_sign = ''

    opp_impact = opp_mistakes['impact']
    if opp_impact > 0:
        opp_color = '#6fa86f'
        opp_sign = '+'
    elif opp_impact < 0:
        opp_color = '#c96c6c'
        opp_sign = ''
    else:
        opp_color = '#e8d5b5'
        opp_sign = ''

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
        # Color and label based on result
        if agent['result'] == 'W':
            outcome_color = '#6fa86f'
            result_label = '1 Win'
        else:
            outcome_color = '#c96c6c'
            result_label = '1 Loss'
        agent_html = f'''
                    <!-- Agent of Chaos -->
                    <div style="margin-bottom: 0.5rem; text-align: center;">
                        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.2rem; text-transform: uppercase;">
                            <span style="color: #e8d5b5;">Agent of Chaos:</span>
                            <span style="color: {outcome_color};">{result_label}</span>
                        </div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600;">{agent['player_name']}</div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8;">
                            • {agent['points']:.0f} pts ({dev_sign}{deviation:.0f} vs avg) &bull; Week {agent['week']}
                        </div>
                    </div>'''

    # Opponent blunders - use count instead of impact
    opp_count = int(opp_impact) if opp_impact > 0 else 0
    opp_wins_text = "win" if opp_count == 1 else "wins"

    # Opponent blunders section (only show if count > 0)
    opp_html = ''
    if opp_count > 0:
        opp_html = f'''
                    <div style="margin-bottom: 0.5rem; text-align: center;">
                        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.2rem; text-transform: uppercase;">
                            <span style="color: #e8d5b5;">Opponent Blunders:</span>
                            <span style="color: #6fa86f;">{opp_count} {opp_wins_text}</span>
                        </div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8;">
                            • Wins gifted by your rivals' mistakes
                        </div>
                    </div>'''

    return f'''            <div class="card-preview">
                <h3 class="card-title">The Legend</h3>
                <p class="card-description">How fate and folly intertwined</p>

                <div class="card-data">
                    <div style="margin-bottom: 0.75rem;">
                        <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.35rem; text-align: center;">THE RECKONING</div>
                        <div style="text-align: center;">
                            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{true_skill}</div>
                            <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.7; margin-top: 0.2rem;">Your true record laid bare</div>
                        </div>
                    </div>

                    <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">FORTUNE'S HAND</div>

                    <div style="margin-bottom: 0.5rem; text-align: center;">
                        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.3rem; text-transform: uppercase;">
                            <span style="color: #e8d5b5;">Schedule Luck:</span>
                            <span style="color: {sched_color};">{sched_sign}{sched_impact:.0f} wins</span>
                        </div>
                        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8; line-height: 1.5;">
                            {sched_narrative_html}
                        </div>
                    </div>{opp_html}{agent_html}
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
