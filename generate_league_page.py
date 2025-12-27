#!/usr/bin/env python3
"""
Fantasy Reckoning - League Page Generator
End-to-end script that pulls fresh data and generates shareable league page

Usage:
    python generate_league_page.py --league_id 908221 [--season 2025]
"""

import os
import sys
import json
import glob
import argparse
import subprocess
from datetime import datetime


def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"⚡ {description}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        print(result.stderr)
        sys.exit(1)

    if result.stdout:
        print(result.stdout)

    print(f"✓ {description} completed")
    return result


def pull_fresh_data(league_id, season):
    """Step 1: Pull fresh data from Yahoo API"""
    # Update .env file with league ID
    env_path = '.env'

    # Read existing .env or create new one
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

    # Update league ID and season
    env_vars['LEAGUE_ID'] = str(league_id)
    env_vars['SEASON_YEAR'] = str(season)

    # Write back to .env
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    print(f"Updated .env: LEAGUE_ID={league_id}, SEASON_YEAR={season}")

    # Run data puller
    run_command('python3 data_puller.py', 'Pulling fresh data from Yahoo API')

    # Find the generated league file
    league_file = f'league_{league_id}_{season}.json'
    if not os.path.exists(league_file):
        print(f"❌ Error: Expected league file not found: {league_file}")
        sys.exit(1)

    return league_file


def calculate_metrics(league_file):
    """Step 2: Calculate all metrics and generate card JSONs"""
    run_command(
        f'python3 fantasy_wrapped_calculator.py --data "{league_file}"',
        'Calculating metrics and generating cards'
    )

    # Find all generated fantasy_wrapped_*.json files
    card_files = glob.glob('fantasy_wrapped_*.json')

    if not card_files:
        print("❌ Error: No card files generated")
        sys.exit(1)

    print(f"✓ Generated {len(card_files)} manager card files")
    return card_files


def generate_html_page(league_file, output_file='league_page.html'):
    """Step 3: Generate HTML page with all managers' cards"""
    from html_generator import generate_league_html

    # Load league data to get league info and team names
    with open(league_file, 'r') as f:
        league_data = json.load(f)

    league_name = league_data['league']['name']
    league_id = league_data['league']['league_id']
    season = league_data['league']['season']

    # Build team name map: manager_name -> team_name
    team_map = {}
    for team in league_data.get('teams', []):
        manager_name = team.get('manager_name')
        team_name = team.get('team_name')
        if manager_name and team_name:
            team_map[manager_name] = team_name

    # Load all manager card data
    card_files = glob.glob('fantasy_wrapped_*.json')
    managers_data = []

    for card_file in sorted(card_files):
        with open(card_file, 'r') as f:
            data = json.load(f)
            managers_data.append(data)

    # Generate HTML with team names
    html_content = generate_league_html(
        league_name=league_name,
        league_id=league_id,
        season=season,
        managers_data=managers_data,
        team_map=team_map
    )

    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"\n{'='*60}")
    print(f"✓ Generated league page: {output_file}")
    print(f"{'='*60}")

    return output_file


def open_in_browser(html_file):
    """Step 4: Open the generated page in browser"""
    import webbrowser

    file_path = os.path.abspath(html_file)
    file_url = f'file://{file_path}'

    print(f"\n🚀 Opening in browser: {file_url}")
    webbrowser.open(file_url)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Fantasy Reckoning league page with fresh data'
    )
    parser.add_argument(
        '--league_id',
        required=True,
        help='Yahoo Fantasy league ID'
    )
    parser.add_argument(
        '--season',
        type=int,
        default=2025,
        help='Season year (default: 2025)'
    )
    parser.add_argument(
        '--output',
        default='league_page.html',
        help='Output HTML file name (default: league_page.html)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Skip opening in browser'
    )

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  FANTASY RECKONING                           ║
║              League Page Generator v1.0                      ║
╚══════════════════════════════════════════════════════════════╝

League ID: {args.league_id}
Season: {args.season}
Output: {args.output}
""")

    try:
        # Step 1: Pull fresh data
        league_file = pull_fresh_data(args.league_id, args.season)

        # Step 2: Calculate metrics
        calculate_metrics(league_file)

        # Step 3: Generate HTML
        html_file = generate_html_page(league_file, args.output)

        # Step 4: Open in browser
        if not args.no_browser:
            open_in_browser(html_file)

        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    SUCCESS! 🎉                               ║
╚══════════════════════════════════════════════════════════════╝

Your league page is ready: {html_file}

Share this file with your league or upload to a web host.
""")

    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
