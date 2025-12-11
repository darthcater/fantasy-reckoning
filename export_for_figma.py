"""
Export Fantasy Reckoning data in Figma-friendly formats
Creates clean text files for easy copy-paste into Figma
"""

import json
import csv
from pathlib import Path


def export_manager_cards_text(json_file: str, output_dir: str = "figma_exports"):
    """
    Export each manager's cards as clean text files for Figma

    Args:
        json_file: Path to fantasy_wrapped_[manager].json
        output_dir: Directory to save exports
    """
    # Load JSON
    with open(json_file, 'r') as f:
        data = json.load(f)

    manager_name = data['manager_name']
    cards = data['cards']

    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    manager_dir = Path(output_dir) / manager_name.replace(' ', '_')
    manager_dir.mkdir(exist_ok=True)

    # Export Card 1: The Draft
    card1 = cards['card_1_draft']
    card1_text = f"""
CARD 1: THE DRAFT
================

{manager_name}

DRAFT GRADE: {card1['grade']}
Rank: {card1['rank']}/14

Draft ROI: ${card1['draft_roi']}/point
League Avg: ${card1['league_avg_roi']}/point

STEALS (Best Value)
-------------------
"""
    for i, steal in enumerate(card1['steals'][:3], 1):
        card1_text += f"{i}. {steal.get('player_name', f\"Player {steal['player_id']}\")}\n"
        card1_text += f"   Cost: ${steal['cost']} → {steal['points']} pts (${steal['per_point']}/pt)\n\n"

    card1_text += "\nBUSTS (Worst Value)\n"
    card1_text += "-------------------\n"
    for i, bust in enumerate(card1['busts'][:3], 1):
        card1_text += f"{i}. {bust.get('player_name', f\"Player {bust['player_id']}\")}\n"
        card1_text += f"   Cost: ${bust['cost']} → {bust['points']} pts (${bust['per_point']}/pt)\n\n"

    with open(manager_dir / "card_1_draft.txt", 'w') as f:
        f.write(card1_text)

    # Export Card 2: The Identity
    card2 = cards['card_2_identity']
    card2_text = f"""
CARD 2: THE IDENTITY
===================

{manager_name}

ARCHETYPE: {card2['archetype']['type']}
"{card2['archetype']['description']}"

THE THREE TIMELINES
-------------------
1. ACTUAL:  {card2['timelines']['actual']['record']} ({card2['timelines']['actual']['total_points']} pts)
2. OPTIMAL: {card2['timelines']['optimal_lineup']['record']} ({card2['timelines']['optimal_lineup']['total_points']} pts)
3. PERFECT: {card2['wins_left_on_table']['perfect_season_record']}

WINS LEFT ON TABLE: {card2['wins_left_on_table']['total_wins_lost']}
- From lineups: {card2['wins_left_on_table']['lineup_wins_lost']} wins
- From waivers: {card2['wins_left_on_table']['waiver_wins_lost']} wins

LINEUP EFFICIENCY
-----------------
Your efficiency: {card2['efficiency']['lineup_efficiency_pct']}%
Bench points left: {card2['efficiency']['total_bench_points_left']} pts
Avg per week: {card2['efficiency']['avg_bench_points_per_week']} pts

SKILL GRADES
------------
Draft:   {card2['skill_grades']['draft']}
Lineups: {card2['skill_grades']['lineups']}
Waivers: {card2['skill_grades']['waivers']}
Luck:    {card2['skill_grades']['luck']}
"""

    with open(manager_dir / "card_2_identity.txt", 'w') as f:
        f.write(card2_text)

    # Export Card 3: Inflection Points
    card3 = cards['card_3_inflection']
    card3_text = f"""
CARD 3: INFLECTION POINTS
=========================

{manager_name}

THE BIGGEST MISTAKE
-------------------
{card3['biggest_mistake']['tagline']}

"""

    if card3['biggest_mistake']['event']:
        event = card3['biggest_mistake']['event']
        card3_text += f"Your Score: {event['details']['actual_score']}\n"
        card3_text += f"Optimal Score: {event['details']['optimal_score']}\n"
        card3_text += f"Opponent: {event['details']['opponent_score']}\n"
        card3_text += f"Bench Points Left: {event['details']['bench_points_left']}\n"
        card3_text += f"Outcome: {event['details']['outcome']}\n\n"

    card3_text += f"\nSUMMARY\n"
    card3_text += f"-------\n"
    card3_text += f"Total Inflection Points: {card3['summary']['total_inflection_points']}\n"
    card3_text += f"Lineup Mistakes: {card3['summary']['lineup_mistakes']}\n"
    card3_text += f"Close Losses: {card3['summary']['close_losses']}\n"
    card3_text += f"Boom/Bust Weeks: {card3['summary']['boom_bust_weeks']}\n"
    card3_text += f"\nPreventable Losses: {card3['insights']['preventable_losses']}\n"
    card3_text += f"Total Win Impact: +{card3['insights']['total_preventable_win_impact']} wins\n"

    with open(manager_dir / "card_3_inflection.txt", 'w') as f:
        f.write(card3_text)

    # Export Card 4: The Ecosystem
    card4 = cards['card_4_ecosystem']
    card4_text = f"""
CARD 4: THE ECOSYSTEM
=====================

{manager_name}

WAIVER WIRE IMPACT
------------------
Actual waiver points: {card4['optimal_fa_analysis']['actual_waiver_points']}
Optimal available: {card4['optimal_fa_analysis']['optimal_waiver_points']}
Opportunity cost: {card4['optimal_fa_analysis']['opportunity_cost']} pts

Efficiency: {card4['optimal_fa_analysis']['efficiency_pct']}%

DROPS THAT HURT
---------------
Total drops: {card4['drops_analysis']['total_drops']}
Drops that hurt: {card4['drops_analysis']['drops_that_hurt']}
Points given away: {card4['drops_analysis']['total_ros_points_given_away']}

ECOSYSTEM IMPACT
----------------
Players given to rivals: {card4['ecosystem_impact']['players_given_to_rivals']}
Points given to rivals: {card4['ecosystem_impact']['points_given_to_rivals']}
"""

    with open(manager_dir / "card_4_ecosystem.txt", 'w') as f:
        f.write(card4_text)

    # Export Card 5: The Accounting
    card5 = cards['card_5_accounting']
    card5_text = f"""
CARD 5: THE ACCOUNTING
======================

{manager_name}

ACTUAL RECORD: {card5['actual_record']['record']}

WIN ATTRIBUTION
---------------
"""

    for factor in card5['win_attribution']['factors']:
        card5_text += f"{factor['factor']}: {factor['impact']:+d} wins (Grade: {factor['grade']})\n"

    card5_text += f"\nTHE ONE THING TO FIX\n"
    card5_text += f"--------------------\n"
    card5_text += f"{card5['the_one_thing']['factor']}\n"
    card5_text += f"Current Grade: {card5['the_one_thing']['current_grade']}\n"
    card5_text += f"Impact: {card5['the_one_thing']['impact']} wins\n"
    card5_text += f"\n{card5['the_one_thing']['diagnosis']}\n"

    card5_text += f"\nPLAYOFF BENCHMARK\n"
    card5_text += f"-----------------\n"
    card5_text += f"Playoff teams avg efficiency: {card5['playoff_benchmark']['playoff_teams_avg_efficiency']}%\n"
    card5_text += f"Your efficiency: {card5['playoff_benchmark']['your_efficiency']}%\n"
    card5_text += f"Gap to close: {card5['playoff_benchmark']['efficiency_gap']}%\n"

    card5_text += f"\nIMPROVEMENT CHECKLIST\n"
    card5_text += f"---------------------\n"
    for i, item in enumerate(card5['improvement_checklist'], 1):
        card5_text += f"{i}. [{item['priority']}] {item['category']}\n"
        card5_text += f"   Action: {item['action']}\n"
        card5_text += f"   Impact: {item['expected_impact']}\n\n"

    card5_text += f"\nPROJECTED 2026 RECORD\n"
    card5_text += f"---------------------\n"
    card5_text += f"{card5['projected_2026_record']['record']}\n"
    card5_text += f"Improvement: +{card5['projected_2026_record']['improvement']} wins\n"
    card5_text += f"{card5['projected_2026_record']['note']}\n"

    with open(manager_dir / "card_5_accounting.txt", 'w') as f:
        f.write(card5_text)

    print(f"✅ Exported {manager_name}'s cards to {manager_dir}/")


def export_all_managers(output_dir: str = "figma_exports"):
    """Export all fantasy_wrapped_*.json files"""
    import glob

    json_files = glob.glob("fantasy_wrapped_*.json")

    if not json_files:
        print("❌ No fantasy_wrapped_*.json files found")
        return

    print(f"Found {len(json_files)} managers")

    for json_file in json_files:
        try:
            export_manager_cards_text(json_file, output_dir)
        except Exception as e:
            print(f"❌ Error exporting {json_file}: {e}")

    print(f"\n✅ All exports complete! Check {output_dir}/ directory")


def export_league_summary_csv(output_file: str = "league_summary.csv"):
    """Export a CSV with key metrics for all managers"""
    import glob

    json_files = glob.glob("fantasy_wrapped_*.json")

    if not json_files:
        print("❌ No fantasy_wrapped_*.json files found")
        return

    rows = []

    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)

        manager = data['manager_name']
        cards = data['cards']

        row = {
            'Manager': manager,
            'Record': cards['card_2_identity']['timelines']['actual']['record'],
            'Total Points': cards['card_2_identity']['timelines']['actual']['total_points'],
            'Draft Grade': cards['card_1_draft']['grade'],
            'Draft Rank': f"{cards['card_1_draft']['rank']}/14",
            'Lineup Efficiency': f"{cards['card_2_identity']['efficiency']['lineup_efficiency_pct']}%",
            'Bench Points Left': cards['card_2_identity']['efficiency']['total_bench_points_left'],
            'Wins Left on Table': cards['card_2_identity']['wins_left_on_table']['total_wins_lost'],
            'Preventable Losses': cards['card_3_inflection']['insights']['preventable_losses'],
            'Optimal Record': cards['card_2_identity']['timelines']['optimal_lineup']['record'],
            'The One Thing': cards['card_5_accounting']['the_one_thing']['factor'],
            'Projected 2026 Wins': cards['card_5_accounting']['projected_2026_record']['wins']
        }

        rows.append(row)

    # Sort by total points
    rows.sort(key=lambda x: x['Total Points'], reverse=True)

    # Write CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ League summary exported to {output_file}")


if __name__ == "__main__":
    print("Fantasy Reckoning - Figma Export Tool")
    print("=" * 50)
    print()
    print("Options:")
    print("1. Export all managers' cards as text files")
    print("2. Export league summary as CSV")
    print("3. Both")
    print()

    choice = input("Choose (1/2/3): ").strip()

    if choice in ['1', '3']:
        export_all_managers()

    if choice in ['2', '3']:
        export_league_summary_csv()
