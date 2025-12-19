"""
League Metrics Helper Module
Calculates league rankings, percentiles, and comparative statistics
"""

def calculate_league_ranking(team_values, target_team_key, reverse=True):
    """
    Calculate where a team ranks among all teams for a given metric.

    Args:
        team_values: dict of {team_key: metric_value}
        target_team_key: the team to rank
        reverse: True if higher is better (default), False if lower is better

    Returns:
        dict with rank info
    """
    # Sort teams by value
    sorted_teams = sorted(
        team_values.items(),
        key=lambda x: x[1],
        reverse=reverse
    )

    # Find rank (1-indexed)
    rank = None
    for i, (team_key, value) in enumerate(sorted_teams):
        if team_key == target_team_key:
            rank = i + 1
            break

    total_teams = len(team_values)
    percentile = ((total_teams - rank) / total_teams * 100) if rank else 0

    # Calculate league stats
    values = list(team_values.values())
    league_avg = sum(values) / len(values) if values else 0
    target_value = team_values.get(target_team_key, 0)
    gap_to_avg = target_value - league_avg

    return {
        'league_rank': f"{rank}/{total_teams}",
        'league_rank_numeric': rank,
        'percentile': round(percentile, 1),
        'league_average': round(league_avg, 2),
        'your_value': round(target_value, 2),
        'gap_to_average': round(gap_to_avg, 2)
    }


def calculate_playoff_comparison(team_values, target_team_key, playoff_team_keys):
    """
    Compare target team's metric to playoff teams average.

    Args:
        team_values: dict of {team_key: metric_value}
        target_team_key: the team to compare
        playoff_team_keys: list of team keys that made playoffs

    Returns:
        dict with playoff comparison
    """
    playoff_values = [team_values[tk] for tk in playoff_team_keys if tk in team_values]
    playoff_avg = sum(playoff_values) / len(playoff_values) if playoff_values else 0

    target_value = team_values.get(target_team_key, 0)
    gap_to_playoff_avg = target_value - playoff_avg

    return {
        'playoff_teams_average': round(playoff_avg, 2),
        'gap_to_playoff_avg': round(gap_to_playoff_avg, 2)
    }


def get_grade_from_percentile(percentile):
    """Convert percentile to letter grade"""
    if percentile >= 95:
        return "A+"
    elif percentile >= 90:
        return "A"
    elif percentile >= 85:
        return "A-"
    elif percentile >= 80:
        return "B+"
    elif percentile >= 75:
        return "B"
    elif percentile >= 70:
        return "B-"
    elif percentile >= 65:
        return "C+"
    elif percentile >= 60:
        return "C"
    elif percentile >= 55:
        return "C-"
    elif percentile >= 50:
        return "D+"
    elif percentile >= 40:
        return "D"
    elif percentile >= 30:
        return "D-"
    else:
        return "F"


def get_category_from_percentile(percentile, metric_name="performance"):
    """Get descriptive category based on percentile"""
    if percentile >= 90:
        return f"Elite {metric_name}"
    elif percentile >= 75:
        return f"Strong {metric_name}"
    elif percentile >= 60:
        return f"Above Average {metric_name}"
    elif percentile >= 40:
        return f"Average {metric_name}"
    elif percentile >= 25:
        return f"Below Average {metric_name}"
    else:
        return f"Poor {metric_name}"


def calculate_top_teams_stats(team_values, top_n=3):
    """Get stats for top N teams"""
    sorted_teams = sorted(team_values.items(), key=lambda x: x[1], reverse=True)
    top_teams = sorted_teams[:top_n]

    return {
        'top_teams': [
            {'team_key': tk, 'value': round(val, 2)}
            for tk, val in top_teams
        ],
        'top_avg': round(sum(val for _, val in top_teams) / len(top_teams), 2) if top_teams else 0
    }


def calculate_bottom_teams_stats(team_values, bottom_n=3):
    """Get stats for bottom N teams"""
    sorted_teams = sorted(team_values.items(), key=lambda x: x[1])
    bottom_teams = sorted_teams[:bottom_n]

    return {
        'bottom_teams': [
            {'team_key': tk, 'value': round(val, 2)}
            for tk, val in bottom_teams
        ],
        'bottom_avg': round(sum(val for _, val in bottom_teams) / len(bottom_teams), 2) if bottom_teams else 0
    }


def get_playoff_teams(calc):
    """
    Get list of team keys that made playoffs (top 6 by wins).
    Uses calculated stats from weekly data for accuracy.

    Args:
        calc: FantasyCalculator instance

    Returns:
        list of team_keys for playoff teams
    """
    team_records = []
    for team_key in calc.teams.keys():
        # Calculate stats from weekly data (not stale team summary)
        stats = calc.calculate_team_stats_from_weekly_data(team_key)
        wins = stats['wins']
        points_for = stats['points_for']
        team_records.append((team_key, wins, points_for))

    # Sort by wins (desc), then points_for as tiebreaker (desc)
    team_records.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Top 6 teams make playoffs
    playoff_teams = [team_key for team_key, _, _ in team_records[:6]]

    return playoff_teams


def format_league_context(ranking_info, playoff_info=None):
    """
    Format league context for card output.

    Args:
        ranking_info: dict from calculate_league_ranking()
        playoff_info: dict from calculate_playoff_comparison() (optional)

    Returns:
        formatted dict for card output
    """
    context = {
        'league_rank': ranking_info['league_rank'],
        'league_rank_numeric': ranking_info['league_rank_numeric'],
        'percentile': ranking_info['percentile'],
        'league_average': ranking_info['league_average'],
        'gap_to_average': ranking_info['gap_to_average']
    }

    if playoff_info:
        context['playoff_teams_average'] = playoff_info['playoff_teams_average']
        context['gap_to_playoff_avg'] = playoff_info['gap_to_playoff_avg']

    return context
