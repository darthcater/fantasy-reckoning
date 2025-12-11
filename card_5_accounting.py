"""
Card 5: The Final Ledger
Win/loss attribution and improvement plan
"""

def calculate_card_5_accounting(calc, team_key: str, other_cards: dict) -> dict:
    """
    Calculate Card 5: The Final Ledger

    Args:
        calc: FantasyWrappedCalculator instance
        team_key: Team key
        other_cards: Dict containing Cards 1-4 data

    Returns:
        Dict with final accounting and improvement plan
    """
    team = calc.teams[team_key]
    current_week = calc.league['current_week']

    # Get data from other cards
    card_1 = other_cards.get('card_1_draft', calc.calculate_card_1(team_key))
    card_2 = other_cards.get('card_2_identity', calc.calculate_card_2(team_key))
    card_3 = other_cards.get('card_3_inflection', calc.calculate_card_3(team_key))
    card_4 = other_cards.get('card_4_ecosystem', calc.calculate_card_4(team_key))

    # STEP 1: Win Attribution Analysis
    # Calculate how each factor contributed to wins/losses

    actual_record = card_2['timelines']['actual']
    actual_wins = actual_record['wins']
    actual_losses = actual_record['losses']

    optimal_lineup_record = card_2['timelines']['optimal_lineup']
    optimal_lineup_wins = optimal_lineup_record['wins']

    # Draft impact
    draft_grade = card_1['grade']
    draft_rank = card_1['rank']
    draft_impact_wins = 0

    # Grade-based draft impact estimate
    if draft_grade == 'A':
        draft_impact_wins = 2
    elif draft_grade == 'B':
        draft_impact_wins = 1
    elif draft_grade == 'C':
        draft_impact_wins = 0
    elif draft_grade == 'D':
        draft_impact_wins = -1
    else:  # F
        draft_impact_wins = -2

    # Lineup efficiency impact
    lineup_wins_difference = optimal_lineup_wins - actual_wins
    lineup_impact_wins = -lineup_wins_difference  # Negative because it's wins lost

    # Waiver wire impact
    waiver_grade = card_2['skill_grades']['waivers']
    waiver_impact_wins = 0

    if waiver_grade == 'A':
        waiver_impact_wins = 2
    elif waiver_grade == 'B':
        waiver_impact_wins = 1
    elif waiver_grade == 'C':
        waiver_impact_wins = 0
    elif waiver_grade == 'D':
        waiver_impact_wins = -1
    else:  # F
        waiver_impact_wins = -2

    # Luck impact
    luck_grade = card_2['skill_grades']['luck']
    luck_impact_wins = 0

    if luck_grade == 'A':
        luck_impact_wins = 2  # Very lucky
    elif luck_grade == 'B':
        luck_impact_wins = 1
    elif luck_grade == 'C':
        luck_impact_wins = 0
    elif luck_grade == 'D':
        luck_impact_wins = -1
    else:  # F
        luck_impact_wins = -2  # Very unlucky

    # Injury impact (estimate based on roster)
    # This is a placeholder - would need injury data analysis
    injury_impact_wins = 0

    # STEP 2: Identify "The One Thing" to fix
    # What had the biggest negative impact?

    impact_factors = [
        {'factor': 'Draft', 'impact': draft_impact_wins, 'grade': draft_grade},
        {'factor': 'Lineups', 'impact': lineup_impact_wins, 'grade': card_2['skill_grades']['lineups']},
        {'factor': 'Waivers', 'impact': waiver_impact_wins, 'grade': waiver_grade},
        {'factor': 'Luck', 'impact': luck_impact_wins, 'grade': luck_grade},
        {'factor': 'Injuries', 'impact': injury_impact_wins, 'grade': 'N/A'}
    ]

    # Sort by impact (most negative first)
    impact_factors_sorted = sorted(impact_factors, key=lambda x: x['impact'])

    the_one_thing = impact_factors_sorted[0]['factor']

    # STEP 3: Generate improvement checklist

    improvement_checklist = []

    # Add items based on weaknesses
    if draft_grade in ['D', 'F']:
        improvement_checklist.append({
            'category': 'Draft',
            'priority': 'High',
            'action': 'Study player values and avoid reaching on stars',
            'expected_impact': '+2 wins'
        })

    if card_2['skill_grades']['lineups'] in ['D', 'F']:
        improvement_checklist.append({
            'category': 'Lineups',
            'priority': 'High',
            'action': f"Set optimal lineups - you left {card_2['efficiency']['total_bench_points_left']} points on bench",
            'expected_impact': f"+{lineup_wins_difference} wins"
        })

    if waiver_grade in ['D', 'F']:
        improvement_checklist.append({
            'category': 'Waivers',
            'priority': 'Medium',
            'action': 'Target high-upside free agents earlier in the season',
            'expected_impact': '+1-2 wins'
        })

    if card_2['archetype']['type'] == 'Believer':
        improvement_checklist.append({
            'category': 'Activity',
            'priority': 'Low',
            'action': 'Be more active on waivers - you only made {0} transactions/week'.format(card_2['archetype']['transactions_per_week']),
            'expected_impact': '+1 win'
        })

    if card_2['archetype']['type'] == 'Tinkerer':
        improvement_checklist.append({
            'category': 'Activity',
            'priority': 'Low',
            'action': 'Trust your roster more - you made {0} transactions/week'.format(card_2['archetype']['transactions_per_week']),
            'expected_impact': '+0 wins (save time)'
        })

    # Add inflection point lessons
    if card_3['insights']['preventable_losses'] > 0:
        improvement_checklist.append({
            'category': 'Inflection Points',
            'priority': 'High',
            'action': f"Avoid {card_3['insights']['preventable_losses']} preventable lineup mistakes",
            'expected_impact': f"+{card_3['insights']['preventable_losses']} wins"
        })

    # STEP 4: Project next season record

    # Start with actual wins
    projected_wins = actual_wins

    # Add impact from improvements
    for item in improvement_checklist:
        if 'expected_impact' in item:
            impact_str = item['expected_impact']
            # Parse "+X wins" format
            if '+' in impact_str and 'win' in impact_str:
                try:
                    # Extract number from strings like "+2 wins" or "+1-2 wins"
                    impact_num = impact_str.split('+')[1].split(' ')[0].split('-')[0]
                    projected_wins += int(impact_num)
                except:
                    pass

    # Cap at 14 wins (max possible in 14-game season)
    projected_wins = min(projected_wins, current_week)

    projected_record = f"{projected_wins}-{current_week - projected_wins}"

    # STEP 5: Calculate playoff teams efficiency benchmark

    # Get all teams with their wins and lineup efficiency
    all_teams_efficiency = []
    for tk in calc.teams.keys():
        team_card_2 = calc.calculate_card_2(tk)
        team_wins = team_card_2['timelines']['actual']['wins']
        team_efficiency = team_card_2['efficiency']['lineup_efficiency_pct']
        all_teams_efficiency.append({
            'team_key': tk,
            'wins': team_wins,
            'efficiency': team_efficiency
        })

    # Sort by wins to identify playoff teams (top 6)
    all_teams_efficiency.sort(key=lambda x: x['wins'], reverse=True)
    playoff_teams = all_teams_efficiency[:6]

    # Calculate playoff teams average efficiency
    playoff_avg_efficiency = sum(t['efficiency'] for t in playoff_teams) / len(playoff_teams) if playoff_teams else 0

    # Get this manager's efficiency
    manager_efficiency = card_2['efficiency']['lineup_efficiency_pct']
    efficiency_gap = playoff_avg_efficiency - manager_efficiency

    # STEP 6: Final summary

    total_attributed_wins = sum(f['impact'] for f in impact_factors)

    return {
        'manager_name': team['manager_name'],
        'actual_record': {
            'wins': actual_wins,
            'losses': actual_losses,
            'record': actual_record['record']
        },
        'win_attribution': {
            'factors': impact_factors,
            'draft_impact': draft_impact_wins,
            'lineup_impact': lineup_impact_wins,
            'waiver_impact': waiver_impact_wins,
            'luck_impact': luck_impact_wins,
            'injury_impact': injury_impact_wins,
            'total_attributed': total_attributed_wins
        },
        'the_one_thing': {
            'factor': the_one_thing,
            'current_grade': impact_factors_sorted[0]['grade'],
            'impact': impact_factors_sorted[0]['impact'],
            'diagnosis': f"Your {the_one_thing.lower()} was the biggest drag on your season"
        },
        'improvement_checklist': improvement_checklist,
        'projected_2026_record': {
            'record': projected_record,
            'wins': projected_wins,
            'improvement': projected_wins - actual_wins,
            'note': 'If you address the items in the improvement checklist'
        },
        'insights': {
            'biggest_opportunity': improvement_checklist[0] if improvement_checklist else None,
            'total_checklist_items': len(improvement_checklist),
            'high_priority_items': len([i for i in improvement_checklist if i['priority'] == 'High'])
        },
        'playoff_benchmark': {
            'playoff_teams_avg_efficiency': round(playoff_avg_efficiency, 1),
            'your_efficiency': round(manager_efficiency, 1),
            'efficiency_gap': round(efficiency_gap, 1),
            'note': 'Playoff teams (top 6) averaged this lineup efficiency'
        }
    }
