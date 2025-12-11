# Universal League Support Plan
**Making Fantasy Wrapped work for ANY Yahoo Fantasy Football league**

---

## Current State Analysis

### Your League (LOGE - #908221)
- **Draft Type:** Auction ($200 budget)
- **Scoring:** Head-to-Head
- **Teams:** 14
- **Team Names:** Available (e.g., "RELEASE THE GOLDSTEIN FILES", "Dobb's Decision")
- **Manager Names:** Available (e.g., "Jake", "Tom Evans")

### Current Limitations
1. ❌ Hardcoded league data file: `league_908221_2025.json`
2. ❌ Uses `team_key` (Yahoo's internal ID) instead of team names
3. ❌ No snake draft support or analytics
4. ❌ Hardcoded roster assumptions (10 starters)
5. ❌ No league settings validation
6. ❌ No user-friendly way to input league ID
7. ❌ Doesn't adapt to different scoring systems

---

## Yahoo Fantasy League Variations

### Draft Types
1. **Auction Draft**
   - Each team has a budget (typically $200)
   - Players are "bought" via auction
   - Analytics: ROI ($/point), value picks, busts
   - Your league: ✅ AUCTION

2. **Snake Draft**
   - Teams draft in rounds with reversing order
   - Pick order: 1-14, then 14-1, then 1-14, etc.
   - Analytics: Draft position value (e.g., "60th pick returned 1st round value")
   - Your league: ❌ NOT SNAKE

### Scoring Types
1. **Head-to-Head (H2H)** - Your league ✅
   - Weekly matchups, W/L records
   - Playoff brackets

2. **Points-only**
   - Total points determines winner
   - No matchups

3. **Scoring Formats**
   - Standard (no PPR)
   - PPR (Points Per Reception)
   - 0.5 PPR (Half PPR)
   - Custom scoring rules

### Roster Configurations
- **Starter spots:** Varies (8-12 typical)
- **Position requirements:**
  - QB: 1-2
  - RB: 2-3
  - WR: 2-4
  - TE: 1-2
  - FLEX: 0-3
  - K: 0-1
  - DEF: 0-1
  - IDP (Individual Defensive Players): Optional

### League Sizes
- 8, 10, 12, 14, 16+ teams
- Affects draft strategy, waiver wire depth

---

## Implementation Plan

### Phase 1: Core Flexibility (HIGH PRIORITY)

#### 1.1 Dynamic Data File Input
**Current:**
```python
def __init__(self, data_file='league_908221_2025.json'):
```

**Target:**
```python
def __init__(self, data_file=None):
    if data_file is None:
        # Auto-detect most recent league file
        data_file = self._find_latest_league_file()
```

**Files to modify:**
- `fantasy_wrapped_calculator.py` (line 20)

---

#### 1.2 Team Identification via Team Names
**Current:** Uses `team_key` (e.g., "461.l.908221.t.5")
**Target:** Use `team_name` as primary identifier

**Benefits:**
- User-friendly filenames: `fantasy_wrapped_Jake.json` → `fantasy_wrapped_release_the_goldstein_files.json`
- Consistent across seasons
- More recognizable for users

**Changes needed:**
- Update output file naming (line 273)
- Add team name normalization function
- Maintain backward compatibility with team_key

---

#### 1.3 Draft Type Detection
**Logic:**
```python
def detect_draft_type(self) -> str:
    """
    Detect if league used auction or snake draft

    Returns:
        'auction' or 'snake'
    """
    # Check if any draft pick has cost > $1
    if any(pick.get('cost', 1) > 1 for pick in self.draft):
        return 'auction'

    # Check for auction budget in team data
    if any(team.get('auction_budget_total', 0) > 0 for team in self.teams.values()):
        return 'auction'

    return 'snake'
```

**Files to modify:**
- `fantasy_wrapped_calculator.py` (new method in `__init__`)
- `card_1_draft.py` (add snake draft logic)

---

#### 1.4 Snake Draft Analytics (NEW FEATURE)
For snake drafts, Card 1 should show:

**Instead of:** ROI ($/point)
**Show:**
- Draft position value analysis
- "You drafted Player X at pick 60 (5th round)"
- "He returned top-10 value (should've been picked in round 1)"
- "Your best steal: Pick 100 → Ranked #5 overall"
- "Your biggest reach: Pick 12 (1st round) → Ranked #45 overall"

**Implementation:**
```python
def calculate_snake_draft_value(self, team_key):
    """
    Calculate draft value for snake drafts

    Returns:
        {
            'draft_position': 1-14,  # Where they picked in round 1
            'steals': [  # Players drafted later than their value
                {
                    'player': 'Player Name',
                    'draft_pick': 60,
                    'draft_round': 5,
                    'actual_rank': 8,  # Based on total points
                    'value_difference': 52  # Picked 52 spots later than rank
                }
            ],
            'reaches': [...]  # Players drafted earlier than value
        }
    ```

**Files to create/modify:**
- `card_1_draft.py` (add `calculate_snake_draft_analysis()`)

---

### Phase 2: League Settings Detection (MEDIUM PRIORITY)

#### 2.1 Roster Configuration Detection
**Current:** Hardcoded 10 starters (line 152 in `fantasy_wrapped_calculator.py`)

**Target:** Detect from league data
```python
def detect_roster_settings(self):
    """
    Detect league's roster configuration from actual roster data

    Returns:
        {
            'num_starters': 10,
            'positions': {
                'QB': 1,
                'RB': 2,
                'WR': 3,
                'TE': 1,
                'FLEX': 2,
                'K': 1,
                'DEF': 1
            }
        }
    """
    # Sample first week of first team to get roster structure
    sample_week = list(self.weekly_data.values())[0]['week_1']
    starters = sample_week.get('roster', {}).get('starters', [])

    num_starters = len(starters)

    # Count positions
    positions = {}
    for player in starters:
        pos = player.get('selected_position', 'FLEX')
        positions[pos] = positions.get(pos, 0) + 1

    return {
        'num_starters': num_starters,
        'positions': positions
    }
```

**Files to modify:**
- `fantasy_wrapped_calculator.py` (add method, use in optimal lineup calc)

---

#### 2.2 Scoring Type Handling
**Detected from:** `league['scoring_type']`
- `"head"` = Head-to-Head
- `"points"` = Points-only

**Impact:**
- Head-to-Head: Focus on W/L, matchup analysis
- Points-only: Focus on total points, no opponent analysis

**Files to modify:**
- `card_3_inflection.py` (skip inflection analysis for points-only leagues)
- `card_5_accounting.py` (adjust win attribution logic)

---

### Phase 3: User Experience (HIGH PRIORITY)

#### 3.1 Command-Line Arguments
**Add CLI support for easier usage:**

```bash
# Option 1: Specify league ID (runs data puller + calculator)
python main.py --league 908221 --season 2025

# Option 2: Use existing data file
python fantasy_wrapped_calculator.py --data league_908221_2025.json

# Option 3: Auto-detect latest file
python fantasy_wrapped_calculator.py
```

**Implementation:**
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='Fantasy Wrapped Calculator')
    parser.add_argument('--data', help='Path to league data JSON file')
    parser.add_argument('--league', help='Yahoo league ID')
    parser.add_argument('--season', type=int, help='Season year')
    args = parser.parse_args()

    if args.league and args.season:
        # Run data puller first
        run_data_puller(args.league, args.season)
        data_file = f'league_{args.league}_{args.season}.json'
    elif args.data:
        data_file = args.data
    else:
        # Auto-detect
        data_file = find_latest_league_file()

    calc = FantasyWrappedCalculator(data_file)
    calc.generate_all_cards()
```

**Files to modify:**
- `fantasy_wrapped_calculator.py` (update `main()`)

---

#### 3.2 League Validation & Error Messages
**Add helpful error messages for unsupported configurations:**

```python
def validate_league_compatibility(self):
    """
    Check if league is compatible with Fantasy Wrapped

    Raises:
        ValueError: If league has unsupported settings
    """
    errors = []
    warnings = []

    # Check required data
    if not self.draft:
        errors.append("No draft data found. Fantasy Wrapped requires draft results.")

    if self.league.get('num_teams', 0) < 4:
        errors.append(f"League has only {self.league['num_teams']} teams. Minimum 4 required.")

    # Check for warnings
    if self.league.get('scoring_type') == 'points':
        warnings.append("Points-only league detected. Some matchup analysis will be skipped.")

    if not self.transactions:
        warnings.append("No transaction data found. Waiver analysis will be limited.")

    if errors:
        raise ValueError("League compatibility issues:\n" + "\n".join(f"  ❌ {e}" for e in errors))

    if warnings:
        print("⚠️  Warnings:")
        for w in warnings:
            print(f"  {w}")
```

**Files to modify:**
- `fantasy_wrapped_calculator.py` (add method, call in `__init__`)

---

### Phase 4: Advanced Features (NICE TO HAVE)

#### 4.1 Position-Specific Draft Analysis
- Best QB pick, RB pick, etc.
- Position scarcity analysis

#### 4.2 Scoring Format Adjustment
- Detect PPR vs Standard
- Adjust value calculations accordingly

#### 4.3 Player Name Resolution
**Current:** Uses player IDs (e.g., "Player 33393")
**Target:** Fetch player names from Yahoo API

```python
def resolve_player_names(self):
    """Fetch player names for all player IDs in dataset"""
    # Batch API call to get player details
    pass
```

#### 4.4 Multi-Season Support
- Compare year-over-year performance
- Track improvement trends

---

## Testing Strategy

### Test Leagues Needed
1. ✅ **Auction, H2H, 14-team** (Your current league)
2. ⬜ **Snake, H2H, 12-team**
3. ⬜ **Snake, H2H, 10-team**
4. ⬜ **Auction, Points-only, 12-team**
5. ⬜ **Different roster sizes** (8, 16 starters, etc.)

### Testing Checklist
- [ ] Calculator accepts any league file path
- [ ] Auto-detects draft type correctly
- [ ] Snake draft analytics work properly
- [ ] Roster size detection works
- [ ] Team names used in output files
- [ ] Error messages are helpful
- [ ] Works with different scoring types
- [ ] Handles edge cases (no transactions, partial season, etc.)

---

## File Changes Summary

### High Priority Files
1. ✏️ **`fantasy_wrapped_calculator.py`**
   - Remove hardcoded data file
   - Add draft type detection
   - Add roster settings detection
   - Add league validation
   - Add CLI argument support
   - Fix team name usage

2. ✏️ **`card_1_draft.py`**
   - Add snake draft analytics
   - Conditional logic for auction vs snake

3. ✏️ **`data_puller.py`**
   - Make league ID a parameter (already done via .env)

4. 📝 **`main.py`** (NEW FILE)
   - Unified entry point
   - Handles both data pulling and calculation
   - Better user experience

### Medium Priority Files
5. ✏️ **`card_3_inflection.py`**
   - Handle points-only leagues (no matchups)

6. ✏️ **`card_5_accounting.py`**
   - Adjust logic for different league types

### Documentation Files
7. ✏️ **`README.md`**
   - Update with universal league support
   - Add examples for different league types

---

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Works with auction drafts (already done)
- ⬜ Works with snake drafts
- ⬜ Accepts any league data file
- ⬜ Auto-detects league settings
- ⬜ Uses team names properly
- ⬜ Helpful error messages

### Full Feature Set
- ⬜ Snake draft value analysis ("pick 60 = round 1 value")
- ⬜ Position-specific analysis
- ⬜ Scoring format detection (PPR vs Standard)
- ⬜ CLI with arguments
- ⬜ Comprehensive testing with 5+ different league types

---

## Implementation Timeline

### Week 1: Core Flexibility
- Remove hardcoded assumptions
- Add draft type detection
- Dynamic roster configuration

### Week 2: Snake Draft Support
- Implement snake draft analytics
- Test with snake draft league

### Week 3: User Experience
- CLI arguments
- League validation
- Better error messages

### Week 4: Testing & Polish
- Test with multiple league configurations
- Documentation updates
- Edge case handling

---

## Next Steps

**Immediate actions:**
1. Update `fantasy_wrapped_calculator.py` to accept any data file
2. Add draft type detection
3. Implement snake draft analytics in `card_1_draft.py`
4. Test with your league to ensure backward compatibility
5. Find/create a test snake draft league

**Long-term:**
- Build a web interface for non-technical users
- Add player name resolution
- Create visualizations (charts, graphs)
- Support other sports (basketball, baseball)

---

**Questions to Answer:**
1. Should we prioritize snake draft support or other features first?
2. Do you have access to a snake draft league for testing?
3. What's the most important feature for making this shareable with other leagues?
4. Should team names or manager names be used for output files?

---

**Last Updated:** 2025-12-09
