#!/usr/bin/env python3
"""
Fantasy Reckoning - League Compatibility Validator
Checks if a Yahoo Fantasy Football league is compatible BEFORE customer pays
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class LeagueValidator:
    """Validates league compatibility with Fantasy Reckoning"""

    def __init__(self, league_file: str):
        """
        Initialize validator with league data

        Args:
            league_file: Path to league_*.json file
        """
        print(f"Loading league data from {league_file}...")
        with open(league_file, 'r') as f:
            self.data = json.load(f)

        self.league = self.data.get('league', {})
        self.teams = self.data.get('teams', [])
        self.draft = self.data.get('draft', [])
        self.weekly_data = self.data.get('weekly_data', {})
        self.transactions = self.data.get('transactions', [])

        # Results
        self.checks = []
        self.warnings = []
        self.errors = []
        self.card_availability = {
            'card_1_draft': True,
            'card_2_identity': True,
            'card_3_inflection': True,
            'card_4_ecosystem': True,
            'card_5_accounting': True
        }

    def validate(self) -> Dict:
        """
        Run all validation checks

        Returns:
            Dict with validation results
        """
        print("\nRunning compatibility checks...\n")

        # Run checks
        self._check_league_basics()
        self._check_draft_data()
        self._check_roster_config()
        self._check_weekly_data()
        self._check_scoring_type()
        self._check_transactions()
        self._check_special_formats()

        # Determine overall compatibility
        overall = self._determine_compatibility()

        return {
            'compatible': overall['compatible'],
            'confidence': overall['confidence'],
            'checks': self.checks,
            'warnings': self.warnings,
            'errors': self.errors,
            'card_availability': self.card_availability,
            'league_info': {
                'name': self.league.get('name', 'Unknown'),
                'num_teams': self.league.get('num_teams', 0),
                'season': self.league.get('season', 0),
                'current_week': self.league.get('current_week', 0)
            }
        }

    def _check_league_basics(self):
        """Check basic league configuration"""
        num_teams = self.league.get('num_teams', 0)
        season = self.league.get('season', 0)
        current_week = self.league.get('current_week', 0)

        # Check team count
        if 8 <= num_teams <= 16:
            self.checks.append(f"✓ League size: {num_teams} teams (supported)")
        elif num_teams < 8:
            self.warnings.append(f"⚠️  Small league: {num_teams} teams (may affect draft analysis)")
        elif num_teams > 16:
            self.warnings.append(f"⚠️  Large league: {num_teams} teams (uncommon, but should work)")
        else:
            self.errors.append(f"❌ Invalid team count: {num_teams}")

        # Check season
        if season >= 2024:
            self.checks.append(f"✓ Season: {season}")
        else:
            self.warnings.append(f"⚠️  Old season: {season} (data may be incomplete)")

        # Check current week
        if 1 <= current_week <= 18:
            self.checks.append(f"✓ Current week: {current_week}")
        else:
            self.warnings.append(f"⚠️  Unusual week: {current_week}")

    def _check_draft_data(self):
        """Check draft data availability and type"""
        if not self.draft or len(self.draft) == 0:
            self.errors.append("❌ No draft data found (offline draft or keeper league)")
            self.warnings.append("   → Card 1 (Draft Analysis) will be unavailable")
            self.card_availability['card_1_draft'] = False
            return

        # Detect draft type
        has_costs = any(pick.get('cost', 0) > 1 for pick in self.draft)
        has_rounds = any(pick.get('round', 0) > 0 for pick in self.draft)

        if has_costs:
            draft_type = "Auction"
            self.checks.append(f"✓ Draft type: {draft_type} (supported)")
        elif has_rounds:
            draft_type = "Snake"
            self.checks.append(f"✓ Draft type: {draft_type} (supported)")
        else:
            draft_type = "Unknown"
            self.warnings.append(f"⚠️  Draft type unclear - will attempt to analyze")

        # Check draft completeness
        num_teams = self.league.get('num_teams', 0)
        expected_picks = num_teams * 13  # Rough estimate (13 roster spots)
        actual_picks = len(self.draft)

        if actual_picks >= expected_picks * 0.8:  # Allow 20% margin
            self.checks.append(f"✓ Draft data: {actual_picks} picks (complete)")
        else:
            self.warnings.append(f"⚠️  Draft data: {actual_picks} picks (expected ~{expected_picks})")

    def _check_roster_config(self):
        """Check roster configuration"""
        if not self.weekly_data:
            self.errors.append("❌ No weekly roster data found")
            return

        # Sample first team's first week
        first_team_key = list(self.weekly_data.keys())[0]
        first_week_key = list(self.weekly_data[first_team_key].keys())[0]
        sample_week = self.weekly_data[first_team_key][first_week_key]

        roster = sample_week.get('roster', {})
        starters = roster.get('starters', [])
        bench = roster.get('bench', [])

        # Count positions
        positions = {}
        for player in starters:
            pos = player.get('selected_position', 'UNKNOWN')
            positions[pos] = positions.get(pos, 0) + 1

        num_starters = len(starters)
        num_bench = len(bench)

        self.checks.append(f"✓ Roster: {num_starters} starters, {num_bench} bench")

        # Check for standard positions
        standard_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
        found_positions = [pos for pos in positions.keys() if pos in standard_positions]

        if len(found_positions) >= 5:
            self.checks.append(f"✓ Positions: Standard format detected")
        else:
            self.warnings.append(f"⚠️  Non-standard positions: {list(positions.keys())}")

        # Check for superflex (QB-eligible flex that's NOT standard Q/W/R/T)
        flex_positions = [pos for pos in positions.keys() if '/' in pos]
        has_qb_flex = any('Q' in pos for pos in flex_positions)
        has_dedicated_qb = 'QB' in positions

        # True superflex: QB in flex AND either no dedicated QB slot OR multiple QB-eligible slots
        is_true_superflex = has_qb_flex and (not has_dedicated_qb or len([p for p in flex_positions if 'Q' in p]) > 1)

        if is_true_superflex:
            self.warnings.append("⚠️  Superflex/2QB detected - QB values may be approximate")
        elif has_qb_flex and 'Q/W/R/T' in positions:
            # Standard flex that includes QB option - most people don't use QB here
            pass  # No warning needed for standard flex

        # Check for IDP
        idp_positions = [pos for pos in positions.keys() if pos in ['DL', 'LB', 'DB']]
        if idp_positions:
            self.warnings.append(f"⚠️  IDP positions detected: {idp_positions} (not fully supported)")

        # Check for no kicker
        if 'K' not in positions:
            self.warnings.append("⚠️  No kicker position (some metrics unavailable)")

    def _check_weekly_data(self):
        """Check weekly matchup data"""
        if not self.weekly_data:
            self.errors.append("❌ No weekly data found")
            self.card_availability['card_2_identity'] = False
            self.card_availability['card_3_inflection'] = False
            self.card_availability['card_5_accounting'] = False
            return

        num_teams = len(self.weekly_data)
        first_team = list(self.weekly_data.keys())[0]
        num_weeks = len(self.weekly_data[first_team])

        self.checks.append(f"✓ Weekly data: {num_weeks} weeks for {num_teams} teams")

        # Check for opponent data
        sample_week = self.weekly_data[first_team][list(self.weekly_data[first_team].keys())[0]]
        has_opponent = 'opponent_id' in sample_week

        if has_opponent:
            self.checks.append("✓ Matchup data: Opponent tracking available")
        else:
            self.warnings.append("⚠️  No opponent data (Card 3 inflection points may be limited)")

    def _check_scoring_type(self):
        """Check scoring configuration"""
        scoring_type = self.league.get('scoring_type', 'unknown')

        if scoring_type in ['head', 'head2head', 'h2h']:
            self.checks.append("✓ Scoring: Head-to-head (supported)")
        elif scoring_type in ['points', 'point']:
            self.checks.append("✓ Scoring: Points-based (supported)")
        else:
            self.warnings.append(f"⚠️  Unknown scoring type: {scoring_type}")

    def _check_transactions(self):
        """Check transaction data"""
        if not self.transactions:
            self.warnings.append("⚠️  No transaction data (Card 4 ecosystem analysis limited)")
            return

        num_transactions = len(self.transactions)
        self.checks.append(f"✓ Transactions: {num_transactions} recorded")

        # Check transaction types
        trans_types = {}
        for trans in self.transactions:
            ttype = trans.get('type', 'unknown')
            trans_types[ttype] = trans_types.get(ttype, 0) + 1

        # Note: Yahoo transaction API has quirks with drop data
        if trans_types.get('drop', 0) > 0 or trans_types.get('add/drop', 0) > 0:
            self.warnings.append("   Note: Drop analysis is experimental (Yahoo API limitations)")

    def _check_special_formats(self):
        """Check for special league formats"""
        league_name = self.league.get('name', '').lower()

        # Check for special keywords
        special_formats = {
            'guillotine': 'Guillotine format (not yet supported)',
            'best ball': 'Best Ball format (not yet supported)',
            'empire': 'Empire format (not yet supported)',
            'dynasty': 'Dynasty format (keeper analysis unavailable)',
            'keeper': 'Keeper format (keeper analysis unavailable)'
        }

        for keyword, warning in special_formats.items():
            if keyword in league_name:
                self.warnings.append(f"⚠️  {warning}")

    def _determine_compatibility(self) -> Dict:
        """Determine overall compatibility level"""
        has_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0

        available_cards = sum(1 for v in self.card_availability.values() if v)
        total_cards = len(self.card_availability)

        if has_errors:
            if available_cards >= 4:
                confidence = 'partial'
                compatible = True
            elif available_cards >= 3:
                confidence = 'limited'
                compatible = True
            else:
                confidence = 'unsupported'
                compatible = False
        elif has_warnings and len(self.warnings) > 3:
            confidence = 'partial'
            compatible = True
        else:
            confidence = 'full'
            compatible = True

        return {
            'compatible': compatible,
            'confidence': confidence,
            'available_cards': available_cards,
            'total_cards': total_cards
        }


def print_validation_report(results: Dict):
    """Print formatted validation report"""
    print("\n" + "="*70)
    print("FANTASY RECKONING - LEAGUE COMPATIBILITY REPORT")
    print("="*70)

    # League info
    info = results['league_info']
    print(f"\n📊 League: {info['name']}")
    print(f"   Teams: {info['num_teams']} | Season: {info['season']} | Week: {info['current_week']}")

    # Overall compatibility
    print("\n" + "="*70)
    confidence = results['confidence'].upper()

    if results['compatible']:
        if confidence == 'FULL':
            print("✅ FULLY SUPPORTED")
            print("   All 5 cards will generate perfectly!")
        elif confidence == 'PARTIAL':
            print("⚠️  PARTIALLY SUPPORTED")
            print("   Most cards will work with minor limitations")
        elif confidence == 'LIMITED':
            print("⚠️  LIMITED SUPPORT")
            print("   Some cards unavailable due to missing data")
    else:
        print("❌ NOT SUPPORTED")
        print("   Too many compatibility issues - not recommended")

    # Card availability
    print("\n📋 Card Availability:")
    card_names = {
        'card_1_draft': 'Card 1: The Draft',
        'card_2_identity': 'Card 2: The Identity',
        'card_3_inflection': 'Card 3: Inflection Points',
        'card_4_ecosystem': 'Card 4: The Ecosystem',
        'card_5_accounting': 'Card 5: The Accounting'
    }

    for card_id, available in results['card_availability'].items():
        card_name = card_names.get(card_id, card_id)
        status = "✓" if available else "✗"
        print(f"   {status} {card_name}")

    # Checks passed
    if results['checks']:
        print("\n✓ Compatibility Checks Passed:")
        for check in results['checks']:
            print(f"   {check}")

    # Warnings
    if results['warnings']:
        print("\n⚠️  Warnings:")
        for warning in results['warnings']:
            print(f"   {warning}")

    # Errors
    if results['errors']:
        print("\n❌ Errors:")
        for error in results['errors']:
            print(f"   {error}")

    # Recommendation
    print("\n" + "="*70)
    print("💡 RECOMMENDATION")
    print("="*70)

    available = sum(1 for v in results['card_availability'].values() if v)

    if results['compatible']:
        if confidence == 'FULL':
            print("\n✅ READY FOR PURCHASE")
            print(f"   This league is fully supported - all 5 cards will work great!")
            print(f"\n   Next step: Send $10 via Venmo with league ID {info.get('league_id', 'XXXXX')}")
        elif confidence == 'PARTIAL':
            print("\n⚠️  ACCEPTABLE WITH LIMITATIONS")
            print(f"   {available}/5 cards available - some features limited by data.")
            print(f"   Customer should review warnings before purchasing.")
        elif confidence == 'LIMITED':
            print("\n⚠️  LIMITED COMPATIBILITY")
            print(f"   Only {available}/5 cards available.")
            print(f"   Recommend waiting for V2 with better support.")
    else:
        print("\n❌ NOT RECOMMENDED")
        print(f"   League has too many compatibility issues.")
        print(f"   Recommend waiting for expanded format support.")

    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Validate Yahoo Fantasy Football league compatibility with Fantasy Reckoning'
    )
    parser.add_argument(
        'league_file',
        help='Path to league JSON file (e.g., league_908221_2025.json)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation info'
    )

    args = parser.parse_args()

    # Check file exists
    if not Path(args.league_file).exists():
        print(f"❌ Error: File not found: {args.league_file}")
        print("\nUsage: python validate_league.py league_XXXXX_2025.json")
        sys.exit(1)

    # Run validation
    validator = LeagueValidator(args.league_file)
    results = validator.validate()

    # Print report
    print_validation_report(results)

    # Exit code based on compatibility
    if results['compatible']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
