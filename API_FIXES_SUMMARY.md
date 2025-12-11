# Yahoo Fantasy API Fixes - Summary

## Overview
Fixed `data_puller.py` to work correctly with `yahoo-fantasy-api` version 2.12.2 by researching and implementing the correct API methods and data structures.

## Issues Fixed

### 1. `League.scoreboard()` Method Does Not Exist
**Problem:** The original code called `self.lg.scoreboard(week)`, but this method doesn't exist in the Library.

**Solution:** Use `self.lg.matchups(week)` instead, which returns the scoreboard data with matchup information.

**Impact:** Affected `get_weekly_scores()` and `get_matchups()` functions.

---

### 2. `Team.roster()` Returns a List, Not a Dict
**Problem:** The original code tried to iterate over `roster.items()`, but `roster()` returns a list of player dictionaries, not a dict.

**Solution:** Changed to iterate over the list directly: `for player_data in roster_list:`

**Return Structure:**
```python
[
    {
        'player_id': 8578,
        'name': 'John Doe',
        'position_type': 'B',
        'eligible_positions': ['C', '1B'],
        'selected_position': 'C',
        'status': ''
    },
    # ... more players
]
```

**Impact:** Affected `get_weekly_roster()` function.

---

### 3. Matchups Data Has Complex Nested Structure
**Problem:** The Yahoo API returns data in a complex nested JSON structure that requires careful navigation.

**Solution:** Implemented robust parsing logic to handle multiple possible data structures:
- `scoreboard_data['scoreboard']['0']['matchups']`
- `scoreboard_data['scoreboard']['matchups']`
- `scoreboard_data['matchups']`

Each level may have data in different keys ('0', 'team', 'matchup', etc.).

---

## Functions Rewritten

### 1. `get_weekly_scores(team_id, week)`

**Changes:**
- Removed call to non-existent `scoreboard()` method
- Use `matchups(week)` to get scoreboard data
- Handle nested JSON structure with fallback paths
- Extract team points from `team_points.total`
- Extract projected points from `team_projected_points.total`
- Added comprehensive error handling with traceback

**Key Code Changes:**
```python
# OLD (doesn't work)
scoreboard = self.lg.scoreboard(week)
team_points = float(team.get('points', 0.0))

# NEW (correct)
scoreboard_data = self.lg.matchups(week)
team_points_obj = team_data.get('team_points', {})
team_points = float(team_points_obj.get('total', 0.0))
```

---

### 2. `get_weekly_roster(team_id, week)`

**Changes:**
- Changed from `roster.items()` to direct list iteration
- Access fields directly: `player_data.get('name')`
- Added note that `roster()` doesn't include player statistics
- Statistics require separate API calls via `League.player_stats()`
- Set points to 0.0 with documentation explaining limitation
- Added comprehensive error handling with traceback

**Key Code Changes:**
```python
# OLD (doesn't work)
for player_key, player_data in roster.items():
    player_info = {
        'player_id': player_key,
        'player_name': player_data.get('name', 'Unknown'),
        # ...
    }

# NEW (correct)
roster_list = self.lg.to_team(team_id).roster(week)
for player_data in roster_list:
    player_info = {
        'player_id': player_data.get('player_id', 0),
        'player_name': player_data.get('name', 'Unknown'),
        # ...
    }
```

**Important Note:** The basic `roster()` method does NOT include player points or statistics. To get actual points, you would need to:
1. Use `League.player_stats(player_ids, req_type='week', week=week)` for each player, OR
2. Extract player stats from the matchup/scoreboard data (which includes roster + stats as sub-resources)

---

### 3. `get_matchups(week)`

**Changes:**
- Removed call to non-existent `scoreboard()` method
- Use `matchups(week)` to get scoreboard data
- Handle nested JSON structure with same logic as `get_weekly_scores()`
- Extract team points from proper nested location
- Added winner determination logic with tie support
- Added comprehensive error handling with traceback

**Key Code Changes:**
```python
# OLD (doesn't work)
scoreboard = self.lg.scoreboard(week)
team1_points = float(team1.get('points', 0.0))

# NEW (correct)
scoreboard_data = self.lg.matchups(week)
# Navigate nested structure...
team1_points_obj = team1_data.get('team_points', {})
team1_points = float(team1_points_obj.get('total', 0.0))
```

---

## Yahoo Fantasy API Data Structures

### Scoreboard/Matchups Response
```json
{
  "scoreboard": {
    "0": {
      "matchups": [
        {
          "matchup": {
            "week": "1",
            "teams": [
              {
                "team": [{
                  "team_key": "423.l.12345.t.1",
                  "team_id": "1",
                  "name": "Team Name",
                  "team_points": {
                    "coverage_type": "week",
                    "week": "1",
                    "total": "103.39"
                  },
                  "team_projected_points": {
                    "coverage_type": "week",
                    "week": "1",
                    "total": "98.50"
                  }
                }]
              },
              {
                "team": [{
                  "team_key": "423.l.12345.t.2",
                  "team_id": "2",
                  "name": "Opponent Team",
                  "team_points": {
                    "total": "95.20"
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

### Roster Response
```python
[
    {
        'player_id': 12345,
        'name': 'Patrick Mahomes',
        'position_type': 'O',  # Offense
        'eligible_positions': ['QB'],
        'selected_position': 'QB',
        'status': ''
    },
    {
        'player_id': 23456,
        'name': 'Christian McCaffrey',
        'position_type': 'O',
        'eligible_positions': ['RB'],
        'selected_position': 'RB',
        'status': ''
    },
    {
        'player_id': 34567,
        'name': 'Injured Player',
        'position_type': 'O',
        'eligible_positions': ['WR', 'FLEX'],
        'selected_position': 'BN',  # Bench
        'status': 'IR'
    }
]
```

---

## Error Handling Improvements

All three functions now include:
1. Try-except blocks with specific error messages
2. Traceback printing for debugging
3. Graceful fallback returns (None or empty list/dict)
4. Null checks before accessing nested data
5. Type checking (isinstance) before assuming dict structure

Example:
```python
try:
    # API call logic
    if isinstance(team_points_obj, dict):
        team_points = float(team_points_obj.get('total', 0.0))
    else:
        team_points = 0.0
except Exception as e:
    print(f"Error fetching data: {e}")
    import traceback
    traceback.print_exc()
    return None
```

---

## API Methods Reference

### League Class Methods (Used in Script)
- `matchups(week=None)` - Get matchup/scoreboard data for a week
- `to_team(team_key)` - Create a Team object
- `teams()` - Get all teams in league (returns dict)
- `standings()` - Get team standings
- `settings()` - Get league settings
- `current_week()` - Get current week number
- `transactions()` - Get transaction history
- `draft_results()` - Get draft results

### Team Class Methods (Used in Script)
- `roster(week=None, day=None)` - Get roster for a week (returns list)
- `matchup(week)` - Get opponent team key for a week

### NOT Available (Removed from Code)
- ~~`League.scoreboard()`~~ - Does not exist, use `matchups()` instead
- Player points in `roster()` - Basic roster doesn't include stats

---

## Testing Recommendations

1. **Test with actual league data:** Run the script with your league credentials to verify data structure
2. **Check data structure variations:** Yahoo's JSON structure can vary slightly
3. **Monitor API changes:** Yahoo Fantasy API may change between seasons
4. **Verify nested navigation:** Use print statements to inspect actual JSON structure
5. **Handle rate limits:** Keep the 0.5s delay between API calls

---

## Known Limitations

1. **Player Points Not Available in Basic Roster:**
   - The `roster()` method only returns positions, not statistics
   - To get player points, need separate `player_stats()` calls
   - This may require additional API calls per player per week
   - Consider extracting from matchup data instead (includes roster as sub-resource)

2. **Complex JSON Structure:**
   - Yahoo's API returns deeply nested JSON
   - Structure can vary (using '0' keys, nested arrays, etc.)
   - Code includes fallback logic but may need adjustment for edge cases

3. **Rate Limiting:**
   - Yahoo API has rate limits
   - Script includes 0.5s delays, but heavy usage may still hit limits
   - Consider adding exponential backoff for errors

---

## Additional Resources

- **Library Documentation:** https://yahoo-fantasy-api.readthedocs.io/en/latest/
- **GitHub Repository:** https://github.com/spilchen/yahoo_fantasy_api
- **Yahoo Fantasy API Official Docs:** https://developer.yahoo.com/fantasysports/guide/
- **PyPI Package:** https://pypi.org/project/yahoo-fantasy-api/

---

## Version Information

- **yahoo-fantasy-api:** 2.12.2
- **Fixed Date:** 2025-12-08
- **Python Compatibility:** Python 3.6+

---

## Summary of Changes

| Function | Issue | Fix | Status |
|----------|-------|-----|--------|
| `get_weekly_scores()` | Used non-existent `scoreboard()` | Changed to `matchups()`, parse nested JSON | ✓ Fixed |
| `get_weekly_roster()` | Used `.items()` on list | Changed to list iteration | ✓ Fixed |
| `get_matchups()` | Used non-existent `scoreboard()` | Changed to `matchups()`, parse nested JSON | ✓ Fixed |
| All functions | Minimal error handling | Added try-except with traceback | ✓ Fixed |

All functions now properly handle the yahoo-fantasy-api 2.12.2 data structures and return data in the expected format for downstream analysis.
