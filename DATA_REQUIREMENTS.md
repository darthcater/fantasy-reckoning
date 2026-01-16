# Fantasy Reckoning - Data Requirements Specification

This document defines the exact data requirements for each metric across all four cards. Use this as a checklist when implementing new platform integrations (Sleeper, ESPN, etc.) or debugging missing/incorrect data.

---

## Overview: Root Causes of Missing Data

When cards show incomplete data, the root cause is typically one of:

1. **Insufficient weeks fetched** - Calculator needs full regular season (14-17 weeks depending on league)
2. **Missing transaction linkage** - Trades/drops need source AND destination team keys
3. **Missing player point data** - Weekly points must be attached to player objects in matchups
4. **Missing roster context** - Need to know who was started vs benched each week
5. **Missing bye week data** - Need NFL bye week schedule mapped to players
6. **Incorrect current_week** - Calculator uses this to determine how many weeks to process

---

## Card 1: The Leader

*"Your management style measured"*

### Metrics Required

| Metric | Data Requirements | How Calculated |
|--------|-------------------|----------------|
| **Manager Archetype** | All 4 dimension percentiles | Weighted scoring across dimensions, max 3 teams per archetype |
| **Draft Performance %** | Draft picks, player points scored, draft cost/round | Compare total drafted player points to league average |
| **Lineup Efficiency %** | Weekly: started roster, bench roster, all player points | % of optimal points actually scored |
| **Bye Week Management %** | Bye week schedule, lineup decisions during bye weeks | Did manager start players on bye? Empty slots? |
| **Waiver Activity %** | All add/drop transactions with timestamps | Transaction volume and timing relative to league |
| **League Percentile** | All 4 dimensions | Average of the 4 percentiles |

### Data Structure Requirements

```python
# For Draft Performance
draft = {
    "picks": [
        {
            "player_name": str,
            "player_id": str,
            "team_key": str,          # Who drafted this player
            "round": int,             # For snake drafts
            "pick": int,              # Overall pick number
            "cost": int,              # For auction drafts (dollars spent)
        }
    ],
    "type": "snake" | "auction"
}

# For Lineup Efficiency - CRITICAL: Need BOTH started AND bench players
weekly_data[week]["matchups"][team_key] = {
    "roster": {
        "starters": [
            {
                "player_name": str,
                "player_id": str,
                "position": str,          # NFL position (QB, RB, etc.)
                "selected_position": str, # Lineup slot (QB, RB1, FLEX, etc.)
                "points": float,          # Actual points scored this week
            }
        ],
        "bench": [
            {
                "player_name": str,
                "player_id": str,
                "position": str,
                "selected_position": "BN",
                "points": float,          # Points scored (even though benched)
            }
        ]
    }
}

# For Bye Week Management
# Need to know each player's bye week - either from:
# 1. Player metadata (bye_week field)
# 2. NFL schedule lookup
# 3. Detecting 0-point weeks for non-injured players

# For Waiver Activity
transactions = [
    {
        "type": "add" | "drop" | "trade",
        "timestamp": int,             # Unix timestamp
        "players": [...],
        # ... details below in Card 2 section
    }
]
```

### Validation Checklist

- [ ] Draft data includes all picks with player_id, team_key, round/cost
- [ ] Weekly matchup data includes BOTH starters AND bench for each team
- [ ] All players have `points` field populated for each week they played
- [ ] current_week reflects actual weeks of data (not NFL API current week)
- [ ] Bye week information is available (either in player data or derivable)

---

## Card 2: The Ledger

*"Points earned, and points forsaken"*

### Metrics Required

| Metric | Data Requirements | How Calculated |
|--------|-------------------|----------------|
| **Draft Points** | Draft picks + points scored by those players when started | Sum of points from drafted players (started only) |
| **Waivers Points** | Waiver add transactions + points scored | Sum of points from waiver pickups (started only) |
| **Trades Points** | Trade transactions + points scored | Net points from players acquired vs sent in trades |
| **Costly Drops Points** | Drop transactions + opponent usage | Points scored by dropped players when started AGAINST dropper |
| **Best Value** | Draft data + points, cost/round | Highest pts/$ (auction) or pts vs round avg (snake) |
| **Biggest Bust** | Draft data + points, cost/round | Lowest pts/$ or most negative vs round avg |
| **Best Waiver** | Waiver adds + points started | Highest points from a waiver pickup |
| **Trade Win/Loss** | Trade transactions + net impact | Best/worst trade by started points differential |
| **Costly Drop** | Drops + opponent starts | Most damaging drop (points scored against you) |

### Data Structure Requirements

```python
# Transaction structure - CRITICAL for trades
transactions = [
    {
        "transaction_id": str,
        "type": "add" | "drop" | "trade",
        "timestamp": int,
        "status": "complete",
        "faab_bid": int | None,       # For FAAB leagues
        "players": [
            {
                "player_name": str,
                "player_id": str,
                "position": str,
                "type": "add" | "drop",

                # FOR TRADES - These are CRITICAL and were missing:
                "source_type": "team" | "waivers" | "freeagents",
                "source_team_key": str | None,      # Who sent the player
                "source_team_name": str | None,
                "destination_team_key": str | None, # Who received the player
                "destination_team_name": str | None,
            }
        ]
    }
]

# For trade impact calculation, need to track:
# 1. Which players were traded
# 2. Points those players scored AFTER the trade
# 3. Whether those points were started or benched
# 4. The matchup context (were they started against the trade partner?)
```

### Why Trades Were Missing (Root Cause Analysis)

The original Sleeper integration showed "N/A" for trades because:

1. **Trades existed** (2 trades in the league)
2. **But source_team_key was None** for all "add" type players in trades
3. The trade parsing set `source_type: "freeagents"` instead of `"team"`
4. Without source_team_key, the calculator couldn't determine who sent the player
5. Trade impact calculation requires knowing: Team A sent Player X, received Player Y

**Fix applied**: Match each "add" in a trade with its corresponding "drop" to determine source team.

### Validation Checklist

- [ ] All transactions have valid type (add/drop/trade)
- [ ] Trade transactions have source_team_key populated for adds (not None)
- [ ] Trade transactions have destination_team_key populated for drops
- [ ] FAAB bids captured for waiver transactions (if FAAB league)
- [ ] Timestamps are valid Unix timestamps (not milliseconds)
- [ ] Can trace each player's journey: drafted by → dropped by → picked up by → traded to

---

## Card 3: The Lineup

*"How you played your pieces on the board"*

### Metrics Required

| Metric | Data Requirements | How Calculated |
|--------|-------------------|----------------|
| **Lineup Efficiency %** | Started vs optimal lineup each week | Actual points / Optimal points |
| **Actual Record** | Win/loss each week | Count of wins and losses |
| **Perfect Lineups Record** | Optimal lineup points vs opponent | What-if record with perfect hindsight |
| **Strongest Unit** | Points by position group | Which position contributed most vs league avg |
| **Weakest Unit** | Points by position group | Which position underperformed most |
| **The Blunder** | Lineup decisions + game outcomes | Wrong start that cost a winnable game |
| **The Clutch Call** | Lineup decisions + game outcomes | Right start that won a close game |

### Data Structure Requirements

```python
# For each week, need complete roster information
weekly_data[week] = {
    "matchups": {
        team_key: {
            "team_key": str,
            "opponent_key": str,
            "points": float,              # Total points scored
            "opponent_points": float,     # Opponent's total points
            "result": "win" | "loss" | "tie",
            "roster": {
                "starters": [...],        # See Card 1 structure
                "bench": [...]            # MUST include bench with points
            }
        }
    }
}

# For Blunder/Clutch detection, need:
# 1. Close games (margin < X points)
# 2. Bench player who outscored a starter at same position
# 3. The difference would have changed the outcome
```

### Why Blunders Were Showing N/A

Possible reasons:
1. **Insufficient weeks**: Only 2 weeks means fewer close games to analyze
2. **No bench data**: Can't calculate "should have started X" without bench points
3. **No close games**: All games were blowouts (unlikely over full season)
4. **Position mismatch**: Bench player couldn't have replaced starter (different positions)

### Validation Checklist

- [ ] All 14-17 regular season weeks are present
- [ ] Each week has matchups for all teams
- [ ] Each matchup has opponent_key and opponent_points
- [ ] Bench players have points populated (not null/0 when they scored)
- [ ] Player positions allow for flex substitution logic

---

## Card 4: The Legend

*"How fate and folly intertwined"*

### Metrics Required

| Metric | Data Requirements | How Calculated |
|--------|-------------------|----------------|
| **The Reckoning (True Record)** | All matchups, all-play calculation | Record vs every team every week |
| **Schedule Luck** | Actual schedule vs average | Compare opponent strength to league average |
| **Injury Toll** | Injury status, points impact | Games lost due to injured starters |
| **Opponent Blunders** | Opponent lineup mistakes | Wins gifted by opponent's bad starts |
| **Agent of Chaos** | Player variance, game impact | High-variance player who swung outcomes |

### Data Structure Requirements

```python
# For all-play / true record
# Need all team scores for each week to calculate "would have beaten X teams"

# For injury tracking
player = {
    "injury_status": str | None,  # "O", "IR", "Q", "D", etc.
    "points": float,              # 0 or low when injured
}

# For opponent blunder detection
# Need opponent's bench data to see their mistakes

# For agent of chaos
# Need player-level points across all weeks to calculate variance
```

### Validation Checklist

- [ ] Can access all team scores for each week (for all-play)
- [ ] Injury status is captured in player data
- [ ] Opponent roster data includes their bench (for opponent blunders)
- [ ] Historical player points available for variance calculation

---

## Integration Testing Protocol

When adding a new platform integration, run these tests:

### Test 1: Week Coverage
```python
# Verify all regular season weeks are fetched
assert len(weekly_data) >= 14, f"Only {len(weekly_data)} weeks fetched"
assert league['current_week'] >= 14, f"current_week is {league['current_week']}"
```

### Test 2: Roster Completeness
```python
# Verify bench data exists
for week in weekly_data:
    for team_key, matchup in week['matchups'].items():
        assert 'bench' in matchup['roster'], f"No bench data for {team_key} week {week}"
        assert len(matchup['roster']['bench']) > 0, f"Empty bench for {team_key}"
```

### Test 3: Transaction Integrity
```python
# Verify trade source/destination
trades = [t for t in transactions if t['type'] == 'trade']
for trade in trades:
    for player in trade['players']:
        if player['type'] == 'add':
            assert player['source_team_key'] is not None, f"Trade add missing source"
        if player['type'] == 'drop':
            assert player['destination_team_key'] is not None, f"Trade drop missing dest"
```

### Test 4: Points Population
```python
# Verify player points are populated
for week in weekly_data:
    for team_key, matchup in week['matchups'].items():
        for player in matchup['roster']['starters'] + matchup['roster']['bench']:
            # Points should be a number (can be 0 for bye/injury)
            assert isinstance(player.get('points'), (int, float)), f"Missing points"
```

### Test 5: Draft Data
```python
# Verify draft has required fields
if draft['type'] == 'snake':
    for pick in draft['picks']:
        assert 'round' in pick, "Snake draft missing round"
elif draft['type'] == 'auction':
    for pick in draft['picks']:
        assert 'cost' in pick, "Auction draft missing cost"
```

---

## Sleeper-Specific Issues Found

| Issue | Symptom | Root Cause | Fix |
|-------|---------|------------|-----|
| Only 2 weeks | Cards show minimal data | NFL state API returns postseason week | Check season_type for 'post'/'off' |
| Trades N/A | No trade data on Card 2 | source_team_key was None | Match adds with drops in trade |
| Bye Week 0% | Card 1 shows 0% | Insufficient weeks OR bye data missing | Fetch full season, verify bye weeks |
| Waiver 0% | Card 1 shows 0% | Either no waivers OR timestamps wrong | Verify transaction timestamps |
| roster_positions error | Calculator crash | Sleeper uses list, Yahoo uses dict | Convert list to dict format |

---

## Data Flow Diagram

```
Platform API (Yahoo/Sleeper/ESPN)
         │
         ▼
    Data Puller
    - Fetch league metadata
    - Fetch all teams
    - Fetch ALL regular season weeks (14-17)
    - Fetch ALL transactions
    - Fetch draft results
    - Normalize to Yahoo-compatible format
         │
         ▼
    JSON Data File
    - league: metadata + current_week
    - teams: all team info
    - weekly_data: matchups with full rosters
    - transactions: adds/drops/trades with linkage
    - draft: picks with cost/round
         │
         ▼
    Calculator
    - Validates data completeness
    - Generates Card 1-4 metrics
    - Outputs per-team JSON files
         │
         ▼
    HTML Generator
    - Renders cards with data
    - Shows N/A when data missing
```

---

## Checklist Before Shipping Integration

- [ ] Full regular season weeks fetched (14-17 weeks)
- [ ] current_week reflects actual data, not API state
- [ ] All matchups have starters AND bench with points
- [ ] Trade source/destination teams properly linked
- [ ] Draft type detected (snake vs auction)
- [ ] Draft picks have round OR cost (based on type)
- [ ] Transactions have valid timestamps
- [ ] Roster positions in correct format (dict)
- [ ] Run all 5 integration tests
- [ ] Generate cards for test league and verify no N/A values
- [ ] Check Card 2 for trade data (if trades occurred)
- [ ] Check Card 3 for blunder/clutch (if close games occurred)
