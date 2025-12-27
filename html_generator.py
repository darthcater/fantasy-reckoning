"""
HTML Generator for Fantasy Reckoning League Pages
Renders all managers' cards into a shareable HTML page
"""

import json
from typing import List, Dict, Any


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

    <script>
        {get_javascript()}
    </script>
</body>
</html>"""

    return html


def generate_manager_section(manager_data: Dict, team_map: Dict[str, str] = None) -> str:
    """Generate HTML for one manager's 4 cards"""

    manager_name = manager_data.get('manager_name', 'Unknown')
    # Use team name if available, otherwise use manager name
    display_name = team_map.get(manager_name, manager_name) if team_map else manager_name
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
        </div>

        <div class="cards-grid">
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

    overall_pct = int(round(card_data.get('overall_percentile', 50)))

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Leader</h3>
        <p class="card-description">How you played and stacked up against your rivals</p>

        <div class="card-data">
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">MANAGER ARCHETYPE</div>
                <div style="text-align: center;">
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 1.75rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{archetype_name}</div>
                    <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem; font-style: italic;">{archetype_desc}</div>
                </div>
            </div>

            <div style="margin-bottom: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em; text-align: center;">SKILL PERCENTILES VS LEAGUE</div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Draft Performance</span>
                        <span>{draft_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {draft_pct}%;"></div>
                    </div>
                </div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Lineup Efficiency</span>
                        <span>{lineups_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {lineups_pct}%;"></div>
                    </div>
                </div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Bye Week Management</span>
                        <span>{bye_week_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {bye_week_pct}%;"></div>
                    </div>
                </div>

                <div class="dimension-row">
                    <div class="dimension-label">
                        <span>Waiver Activity</span>
                        <span>{waivers_pct}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: {waivers_pct}%;"></div>
                    </div>
                </div>

                <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">
                    <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-align: center;">OVERALL PERCENTILE</div>
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 1.5rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{_ordinal(overall_pct)}</div>
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
    waiver_rank = waiver_data.get('rank', 1)  # Need to add this to calculator

    # Trade impact - use net_started_impact
    trade_impact = trade_data.get('net_started_impact', 0)
    trade_rank = trade_data.get('rank', 1)  # Need to add this to calculator

    # Costly drops - use total_value_given_away
    costly_drops_impact = costly_drops_data.get('total_value_given_away', 0)
    costly_drops_rank = costly_drops_data.get('rank', 1)  # Need to add this to calculator

    # Get key moves
    best_value = draft_data.get('steals', [{}])[0] if draft_data.get('steals') else {}
    biggest_bust = draft_data.get('busts', [{}])[0] if draft_data.get('busts') else {}

    # Get best trade from trades list
    trades_list = trade_data.get('trades', [])
    best_trade = max(trades_list, key=lambda t: t.get('net_started_impact', 0)) if trades_list else {}

    # Get most costly drop
    worst_drop = costly_drops_data.get('most_costly_drop', {})

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Ledger</h3>
        <p class="card-description">Where your points came from (and where they went)</p>

        <div class="card-data">
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em; text-align: center;">YOUR BALANCE</div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Draft</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{_format_points(draft_points)} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(draft_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Waivers</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{_format_points(waiver_points)} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(waiver_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Trades</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: {_color_for_value(trade_impact)};">{_format_delta(trade_impact)} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(trade_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Costly Drops</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #c96c6c;">-{_format_points(costly_drops_impact)} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(costly_drops_rank)})</span></span>
                </div>
            </div>

            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.5rem; letter-spacing: 0.05em; text-align: center;">KEY MOVES</div>

                <div class="key-moves-grid">
                    {_render_key_move("Best Value", best_value)}
                    {_render_key_move("Biggest Bust", biggest_bust, is_negative=True)}
                    {_render_key_move("Trade Win", best_trade, is_trade=True)}
                    {_render_key_move("Costly Drop", worst_drop, is_drop=True)}
                </div>
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
    bench_wasted = efficiency_data.get('total_bench_points_left', 0)

    # Get timelines data for records
    timelines = card_data.get('timelines', {})
    actual_timeline = timelines.get('actual', {})
    optimal_timeline = timelines.get('optimal_lineup', {})

    actual_record = actual_timeline.get('record', '0-0')
    actual_rank = 0  # Need to calculate from standings

    optimal_record = optimal_timeline.get('record', '0-0')
    optimal_rank = 0  # Need to calculate

    # Calculate bench rank (need total teams)
    bench_rank = efficiency_rank  # Approximation for now

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
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em; text-align: center;">THE DEPLOYMENT</div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Lineup Efficiency</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{efficiency:.1f}% <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(efficiency_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Actual Record</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{actual_record} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(actual_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(232, 213, 181, 0.1);">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Perfect Lineups</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{optimal_record} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(optimal_rank)})</span></span>
                </div>

                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase; color: #e8d5b5;">Bench Points Wasted</span>
                    <span style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">{_format_points(bench_wasted)} <span style="opacity: 0.6; font-size: 0.8rem;">({_ordinal(bench_rank)} most)</span></span>
                </div>
            </div>

            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2);">
                <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 0.75rem; letter-spacing: 0.05em; text-align: center;">{"FATAL ERROR" if moment_type == "fatal_error" else "CLUTCH CALL"}</div>

                <div style="padding: 1.25rem; text-align: center;">
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 1.1rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f; margin-bottom: 0.75rem;">Week {week}</div>

                    <div style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; line-height: 1.8; opacity: 0.9;">
                        <div>Started: <span style="text-transform: uppercase; color: #b8864f;">{started.get('name', 'N/A')}</span> ({_format_points(started.get('points', 0))})</div>
                        <div>Benched: <span style="text-transform: uppercase; color: #b8864f;">{benched.get('name', 'N/A')}</span> ({_format_points(benched.get('points', 0))})</div>
                        <div>{"Lost" if moment_type == "fatal_error" else "Won"} by: <span style="color: {_color_for_value(margin if moment_type != 'fatal_error' else -margin)};">{abs(margin):.1f} pts</span></div>
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
    opponent_mistakes = next((f for f in luck_factors if f['factor'] == 'Opponent Mistakes'), {})
    random_luck = next((f for f in luck_factors if f['factor'] == 'Random Luck'), {})

    return f"""
    <div class="card-preview">
        <h3 class="card-title">The Legend</h3>
        <p class="card-description">How fate and folly intertwined</p>

        <div class="card-data">
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; opacity: 0.6; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-align: center;">THE RECKONING</div>
                <div style="text-align: center;">
                    <div style="font-family: 'League Gothic', sans-serif; font-size: 2.5rem; letter-spacing: 0.05em; text-transform: uppercase; color: #b8864f;">{true_record}</div>
                    <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; opacity: 0.7; margin-top: 0.25rem;">Your true skill record, stripped of fortune's favor</div>
                </div>
            </div>

            <div style="font-size: 0.85rem; opacity: 0.6; margin-bottom: 1rem; letter-spacing: 0.05em; padding-top: 1.5rem; border-top: 1px solid rgba(232, 213, 181, 0.2); text-align: center;">WIN ATTRIBUTION</div>

            {_render_luck_factor("Schedule Luck", schedule_luck)}
            {_render_luck_factor("Opponent Mistakes", opponent_mistakes)}
            {_render_luck_factor("Random Luck", random_luck)}
        </div>
    </div>
    """


# Helper functions

def _render_key_move(title: str, move_data: Dict, is_negative: bool = False, is_trade: bool = False, is_drop: bool = False) -> str:
    """Render a key move card"""

    if not move_data:
        return f"""
        <div class="key-move-item">
            <div class="key-move-header">{title}</div>
            <div class="key-move-player">N/A</div>
            <div class="key-move-stat" style="opacity: 0.6;">No data</div>
        </div>
        """

    if is_trade:
        # Format trade: "Player Out → Player In"
        players_out = move_data.get('players_out', [])
        players_in = move_data.get('players_in', [])
        if players_out and players_in:
            out_name = players_out[0].get('player_name', 'Unknown') if isinstance(players_out[0], dict) else players_out[0]
            in_name = players_in[0].get('player_name', 'Unknown') if isinstance(players_in[0], dict) else players_in[0]
            player_text = f"{out_name} → {in_name}"
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
        <div class="key-move-header">{title}</div>
        <div class="key-move-player">{player_text}</div>
        <div class="key-move-stat" style="opacity: 0.8;">{stat_text}</div>
    </div>
    """


def _render_luck_factor(title: str, factor_data: Dict) -> str:
    """Render a luck factor with narrative"""

    if not factor_data:
        return ""

    impact = factor_data.get('impact', 0)
    narrative = factor_data.get('narrative', [])

    narrative_html = "<br>".join([f"• {line}" for line in narrative])

    return f"""
    <div style="margin-bottom: 0.75rem;">
        <div style="font-family: 'League Gothic', sans-serif; font-size: 0.95rem; letter-spacing: 0.05em; margin-bottom: 0.5rem; text-transform: uppercase;">
            <span style="color: #b8864f;">{title}:</span>
            <span style="color: {_color_for_value(impact)};">{_format_delta(impact, suffix=' wins')}</span>
        </div>
        <div style="font-family: 'EB Garamond', serif; font-size: 0.85rem; opacity: 0.8; line-height: 1.6;">
            {narrative_html}
        </div>
    </div>
    """


def _format_points(value: float) -> str:
    """Format points value"""
    return f"{value:.0f} pts" if value else "0 pts"


def _format_delta(value: float, suffix: str = " pts") -> str:
    """Format delta value with +/- sign"""
    if value > 0:
        return f"+{value:.0f}{suffix}"
    elif value < 0:
        return f"{value:.0f}{suffix}"
    else:
        return f"0{suffix}"


def _color_for_value(value: float) -> str:
    """Get color based on positive/negative value"""
    if value > 0:
        return "#6fa86f"
    elif value < 0:
        return "#c96c6c"
    else:
        return "#e8d5b5"


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

        /* Cards Grid */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 400px));
            gap: 2rem;
            justify-content: center;
        }

        .card-preview {
            background-color: #252a34;
            padding: 1.5rem 1.25rem;
            border: 1px solid rgba(232, 213, 181, 0.2);
            aspect-ratio: 9 / 16;
            max-width: 400px;
            overflow: hidden;
            position: relative;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .card-preview:hover {
            transform: translateY(-4px);
            border-color: rgba(232, 213, 181, 0.4);
        }

        .card-title {
            font-family: 'Pirata One', cursive;
            font-size: 1.25rem;
            font-weight: 400;
            margin-bottom: 0.5rem;
            color: #e8d5b5;
            text-align: center;
        }

        .card-description {
            font-size: 0.85rem;
            opacity: 0.8;
            line-height: 1.4;
            margin-bottom: 0.75rem;
            text-align: center;
        }

        .card-data {
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(232, 213, 181, 0.2);
            flex: 1;
            font-size: 0.85rem;
        }

        /* Dimension bars */
        .dimension-row {
            margin: 0.75rem 0;
        }

        .dimension-label {
            display: flex;
            justify-content: space-between;
            font-family: 'League Gothic', sans-serif;
            font-size: 0.95rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }

        .dimension-bar {
            height: 8px;
            background: rgba(232, 213, 181, 0.1);
            border-radius: 4px;
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

        /* Responsive */
        @media (max-width: 768px) {
            .cards-grid {
                grid-template-columns: 1fr;
            }

            .key-moves-grid {
                grid-template-columns: 1fr;
            }

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
    """
