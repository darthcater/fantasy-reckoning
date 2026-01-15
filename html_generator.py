"""
HTML Generator for Fantasy Reckoning League Pages
Renders all managers' cards into a shareable HTML page
"""

import json
from typing import List, Dict, Any


def _get_last_name(full_name: str) -> str:
    """Extract last name, handling suffixes like Jr., Sr., II, III, IV, V."""
    if not full_name:
        return '?'

    suffixes = {'jr.', 'jr', 'sr.', 'sr', 'ii', 'iii', 'iv', 'v'}
    parts = full_name.split()

    if len(parts) == 1:
        return parts[0]

    # If last part is a suffix, use second-to-last
    if parts[-1].lower().rstrip('.') in suffixes or parts[-1].lower() in suffixes:
        return parts[-2] if len(parts) > 1 else parts[0]

    return parts[-1]


def generate_league_html(league_name: str, league_id: str, season: int, managers_data: List[Dict], team_map: Dict[str, str] = None) -> str:
    """
    Generate complete HTML page for a league with all managers' cards

    Args:
        league_name: Name of the fantasy league
        league_id: Yahoo league ID
        season: Season year
        managers_data: List of manager card data (from fantasy_wrapped_*.json files)
        team_map: Optional dict mapping manager_name -> team_name

    Returns:
        Complete HTML string
    """

    # Sort managers by manager name (will use team name for display)
    managers_data = sorted(managers_data, key=lambda m: m.get('manager_name', ''))

    # Generate cards HTML for all managers
    managers_html = ""
    for manager_data in managers_data:
        managers_html += generate_manager_section(manager_data, team_map)

    # Build complete HTML page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{league_name} - Fantasy Reckoning {season}</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=Playfair+Display:wght@400;700;900&family=EB+Garamond:wght@400;500;600;700&family=League+Gothic&display=swap" rel="stylesheet">

    <style>
        {get_css()}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="league-header">
        <h1 class="wordmark">FANTASY RECKONING</h1>
        <h2 class="league-title">{league_name}</h2>
        <p class="league-subtitle">Season {season} • League ID: {league_id}</p>
    </header>

    <!-- Managers Section -->
    <main class="managers-container">
        {managers_html}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <p class="footer-text">&copy; 2025 Fantasy Reckoning</p>
        <p class="footer-text">Generated on {_get_timestamp()}</p>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js"></script>
    <script>
        {get_javascript()}
    </script>
</body>
</html>"""

    return html


def generate_manager_section(manager_data: Dict, team_map: Dict[str, str] = None) -> str:
    """Generate HTML for one manager's 4 cards"""

    manager_name = manager_data.get('manager_name', 'Unknown')
    # Use team_name from data if available, fall back to team_map, then manager_name
    display_name = manager_data.get('team_name') or (team_map.get(manager_name) if team_map else None) or manager_name
    cards = manager_data.get('cards', {})

    # Extract card data
    card1 = cards.get('card_1_overview', {})
    card2 = cards.get('card_2_ledger', {})
    card3 = cards.get('card_3_lineups', {})
    card4 = cards.get('card_4_story', {})

    html = f"""
    <section class="manager-section" id="manager-{_slugify(manager_name)}">
        <div class="manager-header">
            <h2 class="manager-name">{display_name}</h2>
            <button class="download-btn" onclick="shareCards('{display_name}')">
                Share Cards
            </button>
        </div>

        <div class="cards-grid" data-manager="{_slugify(manager_name)}">
            {generate_card_1(card1)}
            {generate_card_2(card2)}
            {generate_card_3(card3)}
            {generate_card_4(card4)}
        </div>
    </section>
    """

    return html


def generate_card_1(card_data: Dict) -> str:
    """Generate Card 1: The Leader"""

    archetype = card_data.get('archetype', {})
    archetype_name = archetype.get('name', 'The Manager')
    archetype_desc = archetype.get('description', '')

    # Get percentiles (convert to whole numbers)
    dimension_breakdown = card_data.get('dimension_breakdown', {})
    draft_pct = int(round(dimension_breakdown.get('draft', {}).get('percentile', 50)))
    lineups_pct = int(round(dimension_breakdown.get('lineups', {}).get('percentile', 50)))
    bye_week_pct = int(round(dimension_breakdown.get('bye_week', {}).get('percentile', 50)))
    waivers_pct = int(round(dimension_breakdown.get('waivers', {}).get('percentile', 50)))

    league_pct = int(round(card_data.get('league_percentile', 50)))

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Leader</h3>
        <p class="card-description">Your management style measured</p>

        <div class="card-data">
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.35rem; letter-spacing: 0.05em; text-align: center;">MANAGER ARCHETYPE</div>
                <div style="text-align: center;">
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{archetype_name}</div>
                    <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8; margin-top: 0.2rem; font-style: italic;">{archetype_desc}</div>
                </div>
            </div>

            <div style="margin-bottom: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">SKILL PERCENTILES VS LEAGUE</div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Draft Performance</span>
                        <span style="font-family: 'EB Garamond', serif;">{draft_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {draft_pct}%;"></div>
                    </div>
                </div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Lineup Efficiency</span>
                        <span style="font-family: 'EB Garamond', serif;">{lineups_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {lineups_pct}%;"></div>
                    </div>
                </div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Bye Week Management</span>
                        <span style="font-family: 'EB Garamond', serif;">{bye_week_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {bye_week_pct}%;"></div>
                    </div>
                </div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Waiver Activity</span>
                        <span style="font-family: 'EB Garamond', serif;">{waivers_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {waivers_pct}%;"></div>
                    </div>
                </div>

                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">
                    <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.35rem; text-align: center;">LEAGUE PERCENTILE</div>
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{_ordinal(league_pct)}</div>
                </div>
            </div>
        </div>
    </div>
    """


def generate_card_2(card_data: Dict) -> str:
    """Generate Card 2: The Ledger"""

    # Get balance data
    draft_data = card_data.get('draft', {})
    waiver_data = card_data.get('waivers', {})
    trade_data = card_data.get('trades', {})
    costly_drops_data = card_data.get('costly_drops', {})

    # Draft points and rank
    draft_points = draft_data.get('total_points', 0)
    draft_rank = draft_data.get('rank', 0)

    # Waiver points - use total_points_started
    waiver_points = waiver_data.get('total_points_started', 0)
    waiver_rank = waiver_data.get('rank', 1)

    # Trade impact - use net_started_impact
    trade_impact = trade_data.get('net_started_impact', 0)
    trade_rank = trade_data.get('rank', 1)
    trade_rank_tied = trade_data.get('rank_is_tied', False)

    # Costly drops - use total_value_given_away
    costly_drops_impact = costly_drops_data.get('total_value_given_away', 0)
    costly_drops_rank = costly_drops_data.get('rank', 1)

    # Get key moves data
    best_value = draft_data.get('steals', [{}])[0] if draft_data.get('steals') else {}
    biggest_bust = draft_data.get('busts', [{}])[0] if draft_data.get('busts') else {}
    best_waiver = waiver_data.get('best_adds', [{}])[0] if waiver_data.get('best_adds') else {}

    # Get best/worst trade based on impact
    trades_list = trade_data.get('trades', [])
    if trades_list:
        best_trade = max(trades_list, key=lambda t: t.get('net_started_impact', 0))
        worst_trade = min(trades_list, key=lambda t: t.get('net_started_impact', 0))
        # Show Trade Win if any trade has positive impact, else show Trade Loss
        if best_trade.get('net_started_impact', 0) > 0:
            featured_trade = best_trade
            trade_label = "Trade Win"
        else:
            featured_trade = worst_trade
            trade_label = "Trade Loss"
    else:
        featured_trade = {}
        trade_label = "Trade Win"  # Default label when no trades

    # Get most costly drop
    worst_drop = costly_drops_data.get('most_costly_drop', {})

    # Build key moves table rows
    key_moves_html = _render_key_moves_table([
        ("Best Value", best_value, "draft"),
        ("Biggest Bust", biggest_bust, "bust"),
        ("Best Waiver", best_waiver, "waiver"),
        (trade_label, featured_trade, "trade"),
        ("Costly Drop", worst_drop, "drop"),
    ])

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Ledger</h3>
        <p class="card-description">Points earned, and points forsaken</p>

        <div class="card-data">
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.4rem; letter-spacing: 0.05em; text-align: center;">YOUR BALANCE</div>

                <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Draft</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{_format_points(draft_points)} <span style="color: {_rank_color(draft_rank)};">({_ordinal(draft_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Waivers</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{_format_points(waiver_points)} <span style="color: {_rank_color(waiver_rank)};">({_ordinal(waiver_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Trades</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{_format_delta(trade_impact)} <span style="color: {_rank_color(trade_rank)};">({'T-' if trade_rank_tied else ''}{_ordinal(trade_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.3rem 0;">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Costly Drops</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{'-' if costly_drops_impact > 0 else ''}{_format_points(costly_drops_impact)} <span style="color: {_rank_color(costly_drops_rank, invert=True)};">({_ordinal(costly_drops_rank)})</span></span>
                </div>
                <div style="font-family: 'EB Garamond', serif; font-size: 0.7rem; opacity: 0.5; text-align: right; font-style: italic; margin-top: 0.15rem;">points gifted to your rivals</div>
            </div>

            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.4rem; letter-spacing: 0.05em; text-align: center;">KEY MOVES</div>
                {key_moves_html}
            </div>
        </div>
    </div>
    """


def generate_card_3(card_data: Dict) -> str:
    """Generate Card 3: The Lineup"""

    # Get efficiency data
    efficiency_data = card_data.get('efficiency', {})
    efficiency = efficiency_data.get('lineup_efficiency_pct', 0)
    efficiency_rank = efficiency_data.get('league_rank_numeric', 0)

    # Get position units data
    position_units = card_data.get('position_units', {})
    strongest = position_units.get('strongest', {})
    weakest = position_units.get('weakest', {})

    # Position display names
    pos_names = {'QB': 'QBs', 'RB': 'RBs', 'WR': 'WRs', 'TE': 'TEs'}

    strongest_pos = pos_names.get(strongest.get('position', ''), 'N/A')
    strongest_rank = strongest.get('rank', 0)
    weakest_pos = pos_names.get(weakest.get('position', ''), 'N/A')
    weakest_rank = weakest.get('rank', 0)

    # Get timelines data for records
    timelines = card_data.get('timelines', {})
    actual_timeline = timelines.get('actual', {})
    optimal_timeline = timelines.get('optimal_lineup', {})

    actual_record = actual_timeline.get('record', '0-0')
    actual_record_rank = actual_timeline.get('rank', 0)
    optimal_record = optimal_timeline.get('record', '0-0')
    optimal_record_rank = optimal_timeline.get('rank', 0)

    # Get pivotal moment
    pivotal_moments = card_data.get('pivotal_moments', {})
    moment_type = pivotal_moments.get('moment_type', 'fatal_error')

    # Get the appropriate moment data
    if moment_type == 'fatal_error':
        moment = pivotal_moments.get('the_fatal_error', {})
    else:
        moment = pivotal_moments.get('the_clutch_call', {})

    week = moment.get('week', 1)
    # Pivotal moment has flat structure, not nested
    started = {
        'name': moment.get('started_player', 'N/A'),
        'points': moment.get('started_points', 0)
    }
    benched = {
        'name': moment.get('benched_player', 'N/A'),
        'points': moment.get('benched_points', 0)
    }
    margin = moment.get('margin', 0)

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Lineup</h3>
        <p class="card-description">How you played your pieces on the board</p>

        <div class="card-data">
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">THE DEPLOYMENT</div>

                <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Lineup Efficiency</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{efficiency:.1f}% <span style="color: {_rank_color(efficiency_rank)};">({_ordinal(efficiency_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Actual Record</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{actual_record}{f' <span style="color: {_rank_color(actual_record_rank)};">({_ordinal(actual_record_rank)})</span>' if actual_record_rank > 0 else ''}</span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Perfect Lineups</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{optimal_record}{f' <span style="color: {_rank_color(optimal_record_rank)};">({_ordinal(optimal_record_rank)})</span>' if optimal_record_rank > 0 else ''}</span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Strongest Unit</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{strongest_pos} <span style="color: {_rank_color(strongest_rank)};">({_ordinal(strongest_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.35rem 0;">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Weakest Unit</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.9rem;">{weakest_pos} <span style="color: {_rank_color(weakest_rank)};">({_ordinal(weakest_rank)})</span></span>
                </div>
            </div>

            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">{"THE BLUNDER" if moment_type == "fatal_error" else "THE RALLY"}</div>

                <div style="padding: 0.75rem; text-align: center;">
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; margin-bottom: 0.5rem;">Week {week}</div>

                    <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; line-height: 1.6;">
                        <div>Started: <span style="color: #b8864f; font-weight: 600;">{started.get('name', 'N/A')}</span> ({_format_points(started.get('points', 0))})</div>
                        <div>Benched: <span style="color: #b8864f; font-weight: 600;">{benched.get('name', 'N/A')}</span> ({_format_points(benched.get('points', 0))})</div>
                        <div>{"Lost" if moment_type == "fatal_error" else "Won"} by: {abs(margin):.1f} pts</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def generate_card_4(card_data: Dict) -> str:
    """Generate Card 4: The Legend"""

    # Get win attribution data
    win_attribution = card_data.get('win_attribution', {})
    true_record = win_attribution.get('true_skill_record', '0-0')

    # Extract luck factors from win_attribution
    luck_factors = win_attribution.get('luck_factors', [])
    schedule_luck = next((f for f in luck_factors if f['factor'] == 'Schedule Luck'), {})
    injury_toll = next((f for f in luck_factors if f['factor'] == 'Injury Toll'), {})
    opponent_mistakes = next((f for f in luck_factors if f['factor'] == 'Opponent Mistakes'), {})

    # Get agent of chaos
    agent = win_attribution.get('agent_of_chaos', {})
    agent_html = _render_agent_of_chaos(agent) if agent else ""

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Legend</h3>
        <p class="card-description">How fate and folly intertwined</p>

        <div class="card-data">
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.35rem; text-align: center;">THE RECKONING</div>
                <div style="text-align: center;">
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{true_record}</div>
                    <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.7; margin-top: 0.2rem;">Your true record laid bare</div>
                </div>
            </div>

            <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em; padding-top: 1rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">FORTUNE'S HAND</div>

            {_render_luck_factor("Schedule Luck", schedule_luck)}
            {_render_injury_toll(injury_toll)}
            {_render_opponent_mistakes(opponent_mistakes)}
            {agent_html}
        </div>
    </div>
    """


def _render_agent_of_chaos(agent: Dict) -> str:
    """Render the Agent of Chaos section"""
    if not agent:
        return ""

    player_name = agent.get('player_name', 'Unknown')
    week = agent.get('week', 0)
    points = agent.get('points', 0)
    avg = agent.get('season_avg', 0)
    deviation = agent.get('deviation', 0)
    chaos_type = agent.get('type', 'boom')
    is_yours = agent.get('is_yours', True)
    result = agent.get('result', '')
    win_impact = agent.get('win_impact', '')

    # Color logic: green for wins, red for losses
    if result == 'W':
        outcome_color = "#6fa86f"
        result_label = "1 Win"
    else:
        outcome_color = "#c96c6c"
        result_label = "1 Loss"

    return f"""
    <div style="margin-bottom: 0.5rem; text-align: center;">
        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.2rem; text-transform: uppercase;">
            <span style="color: #e8d5b5;">Agent of Chaos:</span>
            <span style="color: {outcome_color};">{result_label}</span>
        </div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600;">{player_name}</div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8;">
            • {points:.0f} pts ({'+' if deviation > 0 else ''}{deviation:.0f} vs avg) &bull; Week {week}
        </div>
    </div>
    """


# Helper functions

def _render_key_move(title: str, move_data: Dict, is_negative: bool = False, is_trade: bool = False, is_drop: bool = False) -> str:
    """Render a key move card"""

    if not move_data:
        return f"""
        <div class="key-move-item">
            <div style="font-family: 'League Gothic', sans-serif; font-size: 1.0rem; color: #e8d5b5; margin-bottom: 0.4rem; letter-spacing: 0.05em; text-transform: uppercase;">{title}</div>
            <div style="font-family: 'EB Garamond', serif; font-size: 1.0rem; color: #b8864f; margin-bottom: 0.25rem; font-weight: 600;">N/A</div>
            <div style="font-family: 'EB Garamond', serif; font-size: 0.95rem; line-height: 1.3; opacity: 0.6;">No data</div>
        </div>
        """

    if is_trade:
        # Format trade: "Player Out → Player In" (with +N for multi-player trades)
        players_out = move_data.get('players_out', [])
        players_in = move_data.get('players_in', [])
        if players_out and players_in:
            out_full = players_out[0].get('player_name', 'Unknown') if isinstance(players_out[0], dict) else players_out[0]
            in_full = players_in[0].get('player_name', 'Unknown') if isinstance(players_in[0], dict) else players_in[0]
            # Use last names only for better fit (handles Jr., Sr., etc.)
            out_name = _get_last_name(out_full)
            in_name = _get_last_name(in_full)
            # Add "+N" suffix for multi-player trades
            out_extra = f" +{len(players_out) - 1}" if len(players_out) > 1 else ""
            in_extra = f" +{len(players_in) - 1}" if len(players_in) > 1 else ""
            player_text = f"{out_name}{out_extra} → {in_name}{in_extra}"
        else:
            player_text = "N/A"
        impact = move_data.get('net_started_impact', 0)
        stat_text = f'<span style="color: {_color_for_value(impact)};">{_format_delta(impact)}</span> net gain'
    elif is_drop:
        player_text = move_data.get('player_name', 'N/A')
        points_lost = move_data.get('started_pts', 0)  # Use started_pts field
        stat_text = f'<span style="color: #c96c6c;">{_format_points(points_lost)}</span> to opponent'
    else:
        player_text = f"{move_data.get('player_name', 'N/A')}"
        if 'cost' in move_data:
            player_text += f" - ${move_data['cost']}"
        points = move_data.get('points', 0)
        ppd = move_data.get('per_point', 0)
        cost = move_data.get('cost', 1)
        stat_text = f"{_format_points(points)}<br>"
        if cost > 0:
            stat_text += f'<span style="color: {"#c96c6c" if is_negative else "#6fa86f"};">{points/cost:.1f} pts/$</span>'

    return f"""
    <div class="key-move-item">
        <div style="font-family: 'League Gothic', sans-serif; font-size: 1.0rem; color: #e8d5b5; margin-bottom: 0.4rem; letter-spacing: 0.05em; text-transform: uppercase;">{title}</div>
        <div style="font-family: 'EB Garamond', serif; font-size: 1.0rem; color: #b8864f; margin-bottom: 0.25rem; font-weight: 600;">{player_text}</div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.95rem; line-height: 1.3;">{stat_text}</div>
    </div>
    """


def _render_key_moves_table(moves: list) -> str:
    """Render key moves as a grid: Label (left) | Player (center) | Value + Rank (right)"""

    rows_html = ""
    is_snake_draft = False  # Track draft type for dynamic footnote
    for label, data, move_type in moves:
        # Get rank from data
        rank = data.get('rank', 0) if data else 0
        # Negative metrics need inverted rank colors (low rank = bad)
        invert_rank = move_type in ('bust', 'drop')

        # All values use neutral color - only ranks are colored
        pts_color = "#e8d5b5"

        # Get player name and points based on move type
        if not data:
            player = "N/A"
            points = ""
        elif move_type == "draft":
            player = data.get('player_name', '—')
            value_type = data.get('value_type', 'pts/$')
            value = data.get('value', 0)
            if value_type == 'vs Rd Avg':
                # Snake draft: show round and points (footnote explains "vs Rd Avg")
                is_snake_draft = True
                rnd = data.get('round', 0)
                player += f" (Rd {rnd})" if rnd else ""
                points = f"+{value:.0f}" if value >= 0 else f"{value:.0f}"
            else:
                # Auction: show cost and pts/$
                cost = data.get('cost', 0)
                player += f" (${cost})" if cost else ""
                points = f"{value:.1f} pts/$" if value else "— pts/$"
        elif move_type == "bust":
            player = data.get('player_name', '—')
            value_type = data.get('value_type', 'pts/$')
            value = data.get('value', 0)
            if value_type == 'vs Rd Avg':
                # Snake draft: show round and points (footnote explains "vs Rd Avg")
                is_snake_draft = True
                rnd = data.get('round', 0)
                player += f" (Rd {rnd})" if rnd else ""
                points = f"{value:.0f}"  # Will be negative
            else:
                # Auction: show cost and pts/$
                cost = data.get('cost', 0)
                player += f" (${cost})" if cost else ""
                points = f"{value:.1f} pts/$" if value else "— pts/$"
        elif move_type == "waiver":
            player = data.get('player_name', '—')
            pts = data.get('points_started', 0)
            points = f"{pts:.0f} pts" if pts else "— pts"
        elif move_type == "trade":
            players_out = data.get('players_out', [])
            players_in = data.get('players_in', [])
            if players_out and players_in:
                out_full = players_out[0].get('player_name', '?') if isinstance(players_out[0], dict) else players_out[0]
                in_full = players_in[0].get('player_name', '?') if isinstance(players_in[0], dict) else players_in[0]
                # Use last names only for better fit (handles Jr., Sr., etc.)
                out_name = _get_last_name(out_full)
                in_name = _get_last_name(in_full)
                # Add "+N" suffix for multi-player trades
                out_extra = f" +{len(players_out) - 1}" if len(players_out) > 1 else ""
                in_extra = f" +{len(players_in) - 1}" if len(players_in) > 1 else ""
                player = f"{out_name}{out_extra} → {in_name}{in_extra}"
            else:
                player = "N/A"
            pts = data.get('net_started_impact', 0)
            # Add * indicator for multi-player trades
            is_multi = data.get('is_multi_player', False) or (len(players_out) != len(players_in))
            multi_indicator = "*" if is_multi else ""
            if pts > 0:
                points = f"+{pts:.0f} pts{multi_indicator}"
            elif pts < 0:
                points = f"{pts:.0f} pts{multi_indicator}"
            else:
                points = f"0 pts{multi_indicator}"
        elif move_type == "drop":
            player = data.get('player_name', '—')
            pts = data.get('started_pts', 0) or data.get('points_to_opponent', 0)
            weeks_away = data.get('weeks_away', 0)
            if weeks_away > 0 and pts > 0:
                pts_per_week = pts / weeks_away
                points = f"{pts_per_week:.1f} pts/wk"
            else:
                points = "— pts/wk"
        else:
            player = "—"
            points = "— pts"

        # Override if no data
        if not data or player == "N/A":
            player = "N/A"
            points = ""
            rank = 0

        # Add rank display if available (inverted for negative metrics)
        rank_html = f' <span style="color: {_rank_color(rank, invert=invert_rank)};">({_ordinal(rank)})</span>' if rank > 0 else ""

        rows_html += f"""
                <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 0.35rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5; text-align: left; white-space: nowrap;">{label}</span>
                    <span class="truncate" style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: #b8864f; font-weight: 600; text-align: center; min-width: 0;">{player}</span>
                    <span style="font-family: 'EB Garamond', serif; font-size: 0.85rem; color: {pts_color}; text-align: right; white-space: nowrap;">{points}{rank_html}</span>
                </div>"""

    # Footnotes - vary based on draft type
    if is_snake_draft:
        footnote = "Best Value/Bust = pts vs round avg<br>*Net of all players in trade"
    else:
        footnote = "Points started for Best Add/Costly Drop<br>*Net of all players in trade"

    return f"""
                <div style="margin-top: 0.25rem;">
                    {rows_html}
                </div>
                <div style="font-family: 'EB Garamond', serif; font-size: 0.7rem; opacity: 0.5; margin-top: 0.35rem; text-align: center; font-style: italic; line-height: 1.4;">
                    {footnote}
                </div>"""


def _render_luck_factor(title: str, factor_data: Dict) -> str:
    """Render a luck factor with narrative"""

    if not factor_data:
        return ""

    impact = factor_data.get('impact', 0)
    narrative = factor_data.get('narrative', [])

    narrative_html = "<br>".join([f"• {line}" for line in narrative])

    return f"""
    <div style="margin-bottom: 0.5rem; text-align: center;">
        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.3rem; text-transform: uppercase;">
            <span style="color: #e8d5b5;">{title}:</span>
            <span style="color: {_color_for_value(impact)};">{_format_delta(impact, suffix=' wins')}</span>
        </div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8; line-height: 1.5;">
            {narrative_html}
        </div>
    </div>
    """


def _render_opponent_mistakes(factor_data: Dict) -> str:
    """Render opponent mistakes as a fun fact (not added to luck total)"""

    if not factor_data:
        return ""

    count = int(factor_data.get('impact', 0))

    if count == 0:
        return ""  # Don't show if no opponent mistakes

    wins_text = "win" if count == 1 else "wins"

    return f"""
    <div style="margin-bottom: 0.5rem; text-align: center;">
        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.2rem; text-transform: uppercase;">
            <span style="color: #e8d5b5;">Opponent Blunders:</span>
            <span style="color: #6fa86f;">{count} {wins_text}</span>
        </div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8;">
            • Wins gifted by your rivals' mistakes
        </div>
    </div>
    """


def _render_injury_toll(factor_data: Dict) -> str:
    """Render injury toll as a luck factor - always shows for consistency"""

    if not factor_data:
        factor_data = {}

    impact = factor_data.get('impact', 0)  # Already negative for losses
    man_games = factor_data.get('man_games_lost', 0)
    most_costly = factor_data.get('most_costly', {})

    # Format the impact (games lost)
    games_lost = abs(impact)
    if games_lost > 0:
        impact_text = f"{games_lost} {'loss' if games_lost == 1 else 'losses'}"
        impact_color = "#c96c6c"  # Red for losses
    else:
        impact_text = "0 losses"
        impact_color = "#e8d5b5"  # Neutral

    # Build narrative - single clear message
    if games_lost > 0 and most_costly:
        # Injuries cost games - show who cost you
        player = most_costly.get('player_name', 'Unknown')
        status = most_costly.get('status', 'IR')
        week = most_costly.get('week', 0)
        narrative_html = f"• {player} ({status}) cost you Week {week}"
    elif man_games > 0:
        # Injuries happened but didn't cost games
        narrative_html = f"• {man_games} injured {'start' if man_games == 1 else 'starts'}, none decisive"
    else:
        # No injuries
        narrative_html = "• Your roster stayed healthy"

    return f"""
    <div style="margin-bottom: 0.5rem; text-align: center;">
        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.9rem; letter-spacing: 0.05em; margin-bottom: 0.3rem; text-transform: uppercase;">
            <span style="color: #e8d5b5;">Injury Toll:</span>
            <span style="color: {impact_color};">{impact_text}</span>
        </div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.8rem; opacity: 0.8; line-height: 1.5;">
            {narrative_html}
        </div>
    </div>
    """


def _format_points(value: float) -> str:
    """Format points value"""
    return f"{value:.0f} pts" if value else "0 pts"


def _format_delta(value: float, suffix: str = " pts") -> str:
    """Format delta value with +/- sign"""
    # Treat values that round to 0 as exactly 0
    rounded = round(value)
    if rounded > 0:
        return f"+{rounded:.0f}{suffix}"
    elif rounded < 0:
        return f"{rounded:.0f}{suffix}"
    else:
        return f"0{suffix}"


def _color_for_value(value: float) -> str:
    """Get color based on positive/negative value"""
    # Treat values that round to 0 as neutral
    rounded = round(value)
    if rounded > 0:
        return "#6fa86f"
    elif rounded < 0:
        return "#c96c6c"
    else:
        return "#e8d5b5"


def _rank_color(rank: int, num_teams: int = 14, invert: bool = False) -> str:
    """Get color based on rank (lower is better, unless inverted)"""
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


def _percentile_color(pct: int) -> str:
    """Get color based on percentile (higher is better)"""
    if pct >= 67:
        return '#6fa86f'  # Green - top third (good)
    elif pct <= 33:
        return '#c96c6c'  # Red - bottom third (bad)
    return '#e8d5b5'  # Cream - middle (neutral)


def _ordinal(n: int) -> str:
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def _get_timestamp() -> str:
    """Get current timestamp"""
    from datetime import datetime
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")


def get_css() -> str:
    """Get CSS styles for the page"""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'EB Garamond', serif;
            background-color: #252a34;
            color: #e8d5b5;
            line-height: 1.6;
            overflow-x: hidden;
            position: relative;
        }

        /* Fixed background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(180deg, rgba(37, 42, 52, 0.95) 0%, rgba(61, 68, 80, 0.95) 100%);
            z-index: -1;
        }

        /* Header */
        .league-header {
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(180deg, rgba(37, 42, 52, 0.8) 0%, rgba(61, 68, 80, 0.5) 100%);
            border-bottom: 2px solid rgba(184, 134, 79, 0.3);
        }

        .wordmark {
            font-family: 'Pirata One', cursive;
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 400;
            letter-spacing: 0.02em;
            margin-bottom: 0.5rem;
            color: #e8d5b5;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
        }

        .league-title {
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.5rem, 4vw, 2.5rem);
            font-weight: 700;
            color: #b8864f;
            margin-bottom: 0.5rem;
        }

        .league-subtitle {
            font-size: 1rem;
            opacity: 0.7;
        }

        /* Managers Container */
        .managers-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        .manager-section {
            margin-bottom: 4rem;
            padding: 2rem 1rem;
            background: rgba(61, 68, 80, 0.3);
            border: 1px solid rgba(232, 213, 181, 0.1);
            border-radius: 8px;
        }

        .manager-header {
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(184, 134, 79, 0.3);
        }

        .manager-name {
            font-family: 'Pirata One', cursive;
            font-size: clamp(2rem, 5vw, 3rem);
            color: #b8864f;
            text-transform: uppercase;
        }

        .download-btn {
            margin-top: 1rem;
            padding: 0.75rem 1.5rem;
            font-family: 'League Gothic', sans-serif;
            font-size: 1rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            background: linear-gradient(180deg, #b8864f 0%, #9e6f47 100%);
            color: #252a34;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(184, 134, 79, 0.4);
        }

        .download-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        /* Cards Grid */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            justify-content: center;
        }

        @media (max-width: 1200px) {
            .cards-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 600px) {
            .cards-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
                padding: 0 0.5rem;
            }
        }

        .card-preview {
            background-color: #252a34;
            padding: 1.5rem 1.25rem;
            border: 1px solid rgba(232, 213, 181, 0.2);
            min-height: 480px;
            overflow: hidden;
            position: relative;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease, border-color 0.3s ease;
            font-size: 14px;
        }

        @media (max-width: 600px) {
            .card-preview {
                min-height: auto;
                padding: 1.25rem 1rem;
            }
        }

        /* Text overflow protection */
        .truncate {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .card-data {
            overflow: hidden;
        }

        .card-preview:hover {
            transform: translateY(-4px);
            border-color: rgba(232, 213, 181, 0.4);
        }

        .card-title {
            font-family: 'Pirata One', cursive;
            font-size: 1.2rem;
            font-weight: 400;
            margin-bottom: 0.35rem;
            color: #e8d5b5;
            text-align: center;
        }

        .card-description {
            font-size: 0.8rem;
            opacity: 0.8;
            line-height: 1.3;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .card-data {
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(232, 213, 181, 0.2);
            flex: 1;
            font-size: 0.8rem;
        }

        /* Dimension bars */
        .dimension-row {
            margin: 0.5rem 0;
        }

        .dimension-label {
            display: flex;
            justify-content: space-between;
            font-family: 'League Gothic', sans-serif;
            font-size: 0.9rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }

        .dimension-bar {
            height: 6px;
            background: rgba(232, 213, 181, 0.1);
            border-radius: 3px;
            overflow: hidden;
        }

        .dimension-fill {
            height: 100%;
            background: linear-gradient(90deg, #b8864f, #9e6f47);
            transition: width 0.3s ease;
        }

        /* Key moves grid */
        .key-moves-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-top: 0.75rem;
        }

        .key-move-item {
            padding: 0.75rem;
            text-align: center;
        }

        .key-move-header {
            font-family: 'League Gothic', sans-serif;
            font-size: 0.95rem;
            color: #e8d5b5;
            margin-bottom: 0.5rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .key-move-player {
            font-family: 'League Gothic', sans-serif;
            font-size: 0.9rem;
            letter-spacing: 0.08em;
            color: #b8864f;
            margin-bottom: 0.3rem;
            text-transform: uppercase;
        }

        .key-move-stat {
            font-family: 'League Gothic', sans-serif;
            font-size: 0.9rem;
            line-height: 1.4;
            letter-spacing: 0.05em;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            background: rgba(37, 42, 52, 0.8);
            border-top: 1px solid rgba(232, 213, 181, 0.1);
        }

        .footer-text {
            opacity: 0.6;
            font-size: 0.875rem;
            margin: 0.25rem 0;
        }

        /* Responsive - manager section */
        @media (max-width: 768px) {
            .manager-section {
                padding: 1rem 0.5rem;
            }
        }
    """


def get_javascript() -> str:
    """Get JavaScript for interactivity"""
    return """
        // Smooth scroll to manager sections
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Fantasy Reckoning page loaded');

            // Add scroll animations
            const cards = document.querySelectorAll('.card-preview');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, { threshold: 0.1 });

            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(card);
            });
        });

        // Share cards URL
        async function shareCards(managerName) {
            const btn = event.target;
            const url = window.location.href;
            const text = `Check out ${managerName}'s Fantasy Reckoning cards!`;

            // Try Web Share API first (works on mobile)
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Fantasy Reckoning',
                        text: text,
                        url: url
                    });
                    return;
                } catch (err) {
                    // User cancelled or error - fall through to clipboard
                }
            }

            // Fallback: copy to clipboard
            try {
                await navigator.clipboard.writeText(url);
                const originalText = btn.textContent;
                btn.textContent = 'Link Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            } catch (err) {
                // Final fallback: prompt
                prompt('Copy this link:', url);
            }
        }

        // Download all cards for a manager
        async function downloadAllCards(managerId, managerName) {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Generating...';

            try {
                // Wait for fonts to load
                await document.fonts.ready;

                const grid = document.querySelector(`[data-manager="${managerId}"]`);
                const cards = grid.querySelectorAll('.card-preview');
                const cardNames = ['leader', 'ledger', 'lineup', 'legend'];

                for (let i = 0; i < cards.length; i++) {
                    btn.textContent = `Downloading ${i + 1}/4...`;

                    const card = cards[i];

                    // Capture directly from the card element
                    const dataUrl = await htmlToImage.toPng(card, {
                        width: 1080,
                        height: 1920,
                        backgroundColor: '#252a34',
                        pixelRatio: 1,
                        style: {
                            width: '1080px',
                            height: '1920px',
                            minHeight: '1920px',
                            maxWidth: 'none',
                            padding: '80px 60px',
                            fontSize: '38px',
                            transform: 'none',
                            opacity: '1'
                        }
                    });

                    // Download
                    const link = document.createElement('a');
                    const safeName = managerName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
                    link.download = `${safeName}_${cardNames[i]}.png`;
                    link.href = dataUrl;
                    link.click();

                    // Small delay between downloads
                    await new Promise(r => setTimeout(r, 300));
                }

                btn.textContent = 'Done!';
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }, 2000);

            } catch (error) {
                console.error('Download failed:', error);
                btn.textContent = 'Error - Try Again';
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }, 2000);
            }
        }
    """
