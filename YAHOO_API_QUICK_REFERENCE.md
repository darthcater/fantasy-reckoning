# Yahoo Fantasy API 2.12.2 - Quick Reference Guide

## Installation
```bash
pip install yahoo-fantasy-api==2.12.2
```

## Basic Setup
```python
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

# Authenticate
sc = OAuth2(None, None, from_file='oauth2.json')
gm = yfa.Game(sc, 'nfl')
game_id = gm.game_id()

# Get league
full_league_key = f"{game_id}.l.{league_id}"
lg = gm.to_league(full_league_key)
```

---

## League Methods

### Get Matchups/Scoreboard
```python
# Get matchups for a specific week
scoreboard_data = lg.matchups(week=1)

# Returns nested dict structure:
# scoreboard_data['scoreboard']['0']['matchups'] or
# scoreboard_data['matchups']
```

### Get Teams
```python
# Returns dict of teams {team_key: team_data}
teams = lg.teams()

# Example:
# {
#   '423.l.12345.t.1': {
#     'name': 'Team Name',
#     'manager': {'nickname': 'Manager Name'},
#     ...
#   }
# }
```

### Get Standings
```python
# Returns list ordered by rank
standings = lg.standings()

# Example:
# [
#   {
#     'team_key': '423.l.12345.t.1',
#     'rank': 1,
#     'outcome_totals': {'wins': 10, 'losses': 3, 'ties': 0},
#     'points_for': 1234.5,
#     'points_against': 1100.2
#   }
# ]
```

### Get League Settings
```python
settings = lg.settings()

# Returns dict with:
# - name: League name
# - num_teams: Number of teams
# - playoff_start_week: Playoff start week
# - scoring_type: 'head2head' or 'points'
```

### Get Current Week
```python
current_week = lg.current_week()
# Returns: int (e.g., 14)
```

### Get Transactions
```python
transactions = lg.transactions()
# Optional: lg.transactions(tran_types='add,drop,trade')

# Returns list of transaction dicts
```

### Get Draft Results
```python
draft = lg.draft_results()

# Returns list of picks with:
# - round, pick, team_key, player_key, player info
```

### Get Player Stats
```python
# For specific week
stats = lg.player_stats(
    player_ids=[12345, 23456],
    req_type='week',
    week=1
)

# For season
stats = lg.player_stats(
    player_ids=[12345],
    req_type='season'
)
```

---

## Team Methods

### Create Team Object
```python
team = lg.to_team(team_key)
# team_key format: '423.l.12345.t.1'
```

### Get Roster
```python
# Get roster for specific week
roster = team.roster(week=1)

# Returns LIST of player dicts:
# [
#   {
#     'player_id': 12345,
#     'name': 'Patrick Mahomes',
#     'position_type': 'O',
#     'eligible_positions': ['QB'],
#     'selected_position': 'QB',
#     'status': ''
#   },
#   ...
# ]
```

### Get Matchup Opponent
```python
opponent_key = team.matchup(week=1)
# Returns: string team_key of opponent
```

---

## Common Data Structures

### Matchup Data Structure
```python
{
  'scoreboard': {
    '0': {
      'matchups': [
        {
          'matchup': {
            'week': '1',
            'teams': [
              {
                'team': [{
                  'team_key': '423.l.12345.t.1',
                  'team_points': {
                    'total': '103.39'
                  },
                  'team_projected_points': {
                    'total': '98.50'
                  }
                }]
              }
            ]
          }
        }
      ]
    }
  }
}
```

### Navigating Matchup Data
```python
# Get matchups list
if 'scoreboard' in data and '0' in data['scoreboard']:
    matchups = data['scoreboard']['0']['matchups']
elif 'matchups' in data:
    matchups = data['matchups']

# For each matchup
for matchup_obj in matchups:
    matchup = matchup_obj.get('matchup', matchup_obj)
    teams = matchup.get('0', {}).get('teams', matchup.get('teams', []))

    # For each team
    for team_obj in teams:
        if 'team' in team_obj:
            team_data = team_obj['team'][0]
        else:
            team_data = team_obj

        team_key = team_data.get('team_key')
        points = team_data.get('team_points', {}).get('total', 0.0)
```

---

## Common Patterns

### Get All Weekly Scores for a Team
```python
def get_weekly_scores(lg, team_key, week):
    data = lg.matchups(week)
    # Navigate to find team in matchups
    # Extract points from team_points.total
    return points
```

### Get Starters vs Bench
```python
def get_starters_bench(team, week):
    roster = team.roster(week)

    starters = [p for p in roster if p['selected_position'] != 'BN']
    bench = [p for p in roster if p['selected_position'] == 'BN']

    return starters, bench
```

### Get Player Stats for Week
```python
def get_player_week_stats(lg, player_id, week):
    stats = lg.player_stats(
        player_ids=[player_id],
        req_type='week',
        week=week
    )
    return stats
```

---

## Important Notes

### What's Available
- ✓ `lg.matchups(week)` - Scoreboard/matchup data
- ✓ `team.roster(week)` - Returns LIST, not dict
- ✓ `lg.teams()` - Returns dict {team_key: data}
- ✓ `lg.player_stats()` - Get player statistics

### What's NOT Available
- ✗ `lg.scoreboard()` - Does NOT exist, use `matchups()`
- ✗ Points in basic roster - Need `player_stats()` separately
- ✗ `roster.items()` - roster is a LIST, not dict

### Rate Limiting
```python
import time

# Add delay between API calls
time.sleep(0.5)  # 500ms delay
```

### Error Handling
```python
try:
    data = lg.matchups(week)
    # Process data
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

---

## Position Codes

### Common Position Types
- `O` - Offense
- `D` - Defense
- `K` - Kicker

### Common Selected Positions
- `QB` - Quarterback
- `RB` - Running Back
- `WR` - Wide Receiver
- `TE` - Tight End
- `FLEX` - Flex position
- `K` - Kicker
- `DEF` - Defense/Special Teams
- `BN` - Bench

---

## League Key Format

Format: `{game_id}.l.{league_id}`

Examples:
- NFL 2024: `423.l.12345`
- NFL 2025: `449.l.12345`
- MLB 2025: `458.l.12345`

Get current game_id:
```python
game_id = gm.game_id()
```

---

## Useful Debugging

### Print Data Structure
```python
import json

data = lg.matchups(1)
print(json.dumps(data, indent=2))
```

### Check Data Types
```python
print(f"Type: {type(data)}")
print(f"Keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
```

### Inspect Roster
```python
roster = team.roster(1)
print(f"Roster type: {type(roster)}")  # Should be list
print(f"First player: {roster[0] if roster else 'Empty'}")
```

---

## Resources

- **Documentation:** https://yahoo-fantasy-api.readthedocs.io/
- **GitHub:** https://github.com/spilchen/yahoo_fantasy_api
- **Yahoo API Docs:** https://developer.yahoo.com/fantasysports/guide/
- **PyPI:** https://pypi.org/project/yahoo-fantasy-api/

---

## Version
**yahoo-fantasy-api:** 2.12.2
**Last Updated:** 2025-12-08
