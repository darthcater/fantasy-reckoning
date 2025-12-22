"""
Bye Week Management Calculation
Measures how well managers handle bye weeks - planning, depth, and execution

Strategy: Identify bye weeks by detecting when rostered players score 0 points
despite being healthy starters. Compare replacement performance to league average.
"""


def get_player_bye_weeks_from_data(calc) -> dict:
    """
    Infer bye weeks from player scoring patterns.

    When a player is on your roster but scores 0 across the league,
    they're likely on bye (or injured, which we filter out).

    Returns:
        dict: {player_id: [list of bye weeks]}
    """
    player_bye_weeks = {}

    # For each player, look at their weekly scores across all teams
    for player_id, weekly_points in calc.player_points_by_week.items():
        bye_weeks = []

        # Check each week
        for week, points in weekly_points.items():
            # If player scored exactly 0, they were likely on bye or injured
            # We'll track all 0-point weeks and filter later by context
            if points == 0:
                week_num = int(week.replace('week_', ''))
                bye_weeks.append(week_num)

        if bye_weeks:
            player_bye_weeks[player_id] = bye_weeks

    return player_bye_weeks


def calculate_bye_week_management(calc, team_key: str) -> dict:
    """
    Calculate bye week management score for a team.

    Identifies weeks when starters were on bye and measures replacement performance.

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Dict with bye week performance metrics and details
    """
    team = calc.teams[team_key]
    regular_season_weeks = calc.get_regular_season_weeks()

    bye_week_details = []
    replacement_performances = []

    for week in regular_season_weeks:
        week_key = f'week_{week}'

        if week_key not in calc.weekly_data.get(team_key, {}):
            continue

        week_data = calc.weekly_data[team_key][week_key]
        roster = week_data.get('roster', {})
        starters = roster.get('starters', [])
        bench = roster.get('bench', [])

        # Identify starters who were on bye (scored 0 points)
        starters_on_bye = []
        for starter in starters:
            player_id = str(starter.get('player_id', ''))
            points = starter.get('actual_points', 0)

            # If starter scored 0, check if it was a bye week
            # (player scored 0 this week but had points in other weeks)
            if points == 0 and player_id in calc.player_points_by_week:
                season_points = sum(calc.player_points_by_week[player_id].values())
                # If they scored points in other weeks, this was likely a bye
                if season_points > 0:
                    starters_on_bye.append({
                        'player_id': player_id,
                        'player_name': calc.player_names.get(player_id, 'Unknown'),
                        'position': starter.get('selected_position', 'UNKNOWN')
                    })

        # If 2+ starters were on bye, this is a "bye week" to evaluate
        if len(starters_on_bye) >= 2:
            week_points = week_data.get('actual_points', 0)

            bye_week_details.append({
                'week': week,
                'players_on_bye': starters_on_bye,
                'total_points': week_points,
                'bye_count': len(starters_on_bye)
            })

            replacement_performances.append(week_points)

    # Calculate average replacement performance
    avg_replacement_points = (
        sum(replacement_performances) / len(replacement_performances)
        if replacement_performances else 0
    )

    return {
        'bye_week_count': len(bye_week_details),
        'bye_week_details': bye_week_details,
        'avg_replacement_points': round(avg_replacement_points, 1),
        'replacement_performances': replacement_performances
    }


def calculate_league_bye_week_percentile(calc, team_key: str) -> float:
    """
    Calculate percentile ranking for bye week management across league.

    Compares each manager's average bye week replacement performance
    against the league. Higher replacement points = better bye week management.

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key

    Returns:
        Percentile (0-100) for bye week management
    """
    # Calculate bye week scores for all teams
    team_scores = {}

    for tk in calc.teams.keys():
        bye_data = calculate_bye_week_management(calc, tk)
        # Use average replacement points as the score
        # Higher is better (better replacements during bye weeks)
        team_scores[tk] = bye_data['avg_replacement_points']

    # Calculate percentile based on ranking
    this_team_score = team_scores[team_key]
    teams_below = sum(1 for score in team_scores.values() if score < this_team_score)
    percentile = (teams_below / (len(team_scores) - 1)) * 100 if len(team_scores) > 1 else 50

    return percentile
