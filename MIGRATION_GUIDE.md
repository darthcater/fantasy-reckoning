# Migration Guide: Fixing Yahoo Fantasy API Issues

## Quick Fix Checklist

If you're experiencing errors with `yahoo-fantasy-api 2.12.2`, check these:

- [ ] Replace `lg.scoreboard(week)` with `lg.matchups(week)`
- [ ] Change `roster.items()` to direct list iteration
- [ ] Update point extraction to use nested `team_points.total`
- [ ] Add proper error handling with traceback
- [ ] Handle nested JSON structure variations

---

## Common Error Messages and Fixes

### Error 1: AttributeError: 'League' object has no attribute 'scoreboard'

**Error:**
```
AttributeError: 'League' object has no attribute 'scoreboard'
```

**Fix:**
```python
# WRONG
scoreboard = self.lg.scoreboard(week)

# CORRECT
scoreboard_data = self.lg.matchups(week)
```

**Why:** The `League` class doesn't have a `scoreboard()` method. Use `matchups()` instead, which returns the same scoreboard data.

---

### Error 2: AttributeError: 'list' object has no attribute 'items'

**Error:**
```
AttributeError: 'list' object has no attribute 'items'
```

**Fix:**
```python
# WRONG
roster = team.roster(week)
for player_key, player_data in roster.items():
    # ...

# CORRECT
roster_list = team.roster(week)
for player_data in roster_list:
    player_id = player_data.get('player_id')
    name = player_data.get('name')
    # ...
```

**Why:** The `roster()` method returns a list of player dictionaries, not a dictionary.

---

### Error 3: KeyError or Missing Points Data

**Error:**
```
KeyError: 'points'
# or
TypeError: float() argument must be a string or a number, not 'dict'
```

**Fix:**
```python
# WRONG
team_points = float(team.get('points', 0.0))

# CORRECT
team_points_obj = team_data.get('team_points', {})
if isinstance(team_points_obj, dict):
    team_points = float(team_points_obj.get('total', 0.0))
else:
    team_points = 0.0
```

**Why:** Points are nested in a dict: `team_points.total`, not directly accessible as `points`.

---

## Step-by-Step Migration

### 1. Update get_weekly_scores()

**Before:**
```python
def get_weekly_scores(self, team_id, week):
    scoreboard = self.lg.scoreboard(week)  # ERROR: scoreboard() doesn't exist

    for matchup_data in scoreboard.get('matchups', []):
        teams = matchup_data.get('teams', [])
        for team in teams:
            if team.get('team_key') == team_id:
                team_points = float(team.get('points', 0.0))  # ERROR: Wrong structure
```

**After:**
```python
def get_weekly_scores(self, team_id, week):
    try:
        # Use matchups() instead of scoreboard()
        scoreboard_data = self.lg.matchups(week)

        # Navigate nested structure
        matchups_list = None
        if 'scoreboard' in scoreboard_data and '0' in scoreboard_data['scoreboard']:
            matchups_list = scoreboard_data['scoreboard']['0'].get('matchups', [])
        elif 'matchups' in scoreboard_data:
            matchups_list = scoreboard_data['matchups']

        for matchup_obj in matchups_list:
            matchup_data = matchup_obj.get('matchup', matchup_obj)
            teams_in_matchup = matchup_data.get('teams', [])

            # Extract team data (handle nested structure)
            team_list = []
            for team_obj in teams_in_matchup:
                if 'team' in team_obj:
                    team_list.append(team_obj['team'][0])
                else:
                    team_list.append(team_obj)

            for team_data in team_list:
                if team_data.get('team_key') == team_id:
                    # Extract points correctly
                    team_points_obj = team_data.get('team_points', {})
                    team_points = float(team_points_obj.get('total', 0.0))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
```

---

### 2. Update get_weekly_roster()

**Before:**
```python
def get_weekly_roster(self, team_id, week):
    roster = self.lg.to_team(team_id).roster(week)

    for player_key, player_data in roster.items():  # ERROR: roster is a list
        player_info = {
            'player_id': player_key,
            'player_name': player_data.get('name'),
            'actual_points': float(player_data.get('points', 0.0)),  # Points not available
        }
```

**After:**
```python
def get_weekly_roster(self, team_id, week):
    try:
        # roster() returns a list, not a dict
        roster_list = self.lg.to_team(team_id).roster(week)

        for player_data in roster_list:  # Iterate directly over list
            player_info = {
                'player_id': player_data.get('player_id', 0),  # From dict key
                'player_name': player_data.get('name', 'Unknown'),
                'position': player_data.get('position_type', 'Unknown'),
                'selected_position': player_data.get('selected_position', 'BN'),
                'eligible_positions': player_data.get('eligible_positions', []),
                'status': player_data.get('status', ''),
                # Note: basic roster() doesn't include points
                'actual_points': 0.0,  # Need separate player_stats() call
                'projected_points': 0.0,
            }

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {'starters': [], 'bench': []}
```

---

### 3. Update get_matchups()

**Before:**
```python
def get_matchups(self, week):
    scoreboard = self.lg.scoreboard(week)  # ERROR: scoreboard() doesn't exist

    for matchup_data in scoreboard.get('matchups', []):
        teams = matchup_data.get('teams', [])
        team1_points = float(teams[0].get('points', 0.0))  # ERROR: Wrong structure
```

**After:**
```python
def get_matchups(self, week):
    try:
        # Use matchups() instead of scoreboard()
        scoreboard_data = self.lg.matchups(week)

        # Navigate nested structure (same as get_weekly_scores)
        matchups_list = None
        if 'scoreboard' in scoreboard_data and '0' in scoreboard_data['scoreboard']:
            matchups_list = scoreboard_data['scoreboard']['0'].get('matchups', [])
        elif 'matchups' in scoreboard_data:
            matchups_list = scoreboard_data['matchups']

        for matchup_obj in matchups_list:
            matchup_data = matchup_obj.get('matchup', matchup_obj)
            teams_in_matchup = matchup_data.get('teams', [])

            # Parse team data
            team_list = []
            for team_obj in teams_in_matchup:
                if 'team' in team_obj:
                    team_list.append(team_obj['team'][0])
                else:
                    team_list.append(team_obj)

            # Extract points correctly
            team1_data = team_list[0]
            team1_points_obj = team1_data.get('team_points', {})
            team1_points = float(team1_points_obj.get('total', 0.0))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []
```

---

## Testing Your Fixes

### 1. Test Basic Functionality
```python
# Test authentication
puller = FantasyWrappedDataPuller(league_id, season)
puller.authenticate()

# Test league metadata
metadata = puller.get_league_metadata()
print(f"League: {metadata['name']}")

# Test teams
teams = puller.get_all_teams()
print(f"Found {len(teams)} teams")
```

### 2. Test Matchups/Scores
```python
# Test matchups for week 1
week = 1
matchups = puller.get_matchups(week)
print(f"Week {week} matchups: {len(matchups)}")

# Test scores for first team
team_id = teams[0]['team_key']
scores = puller.get_weekly_scores(team_id, week)
print(f"Team points: {scores['actual_points']}")
```

### 3. Test Roster
```python
# Test roster for first team, week 1
roster = puller.get_weekly_roster(team_id, 1)
print(f"Starters: {len(roster['starters'])}")
print(f"Bench: {len(roster['bench'])}")
print(f"First player: {roster['starters'][0]['player_name']}")
```

### 4. Debug Data Structure
```python
# If you're seeing errors, inspect the actual data structure
import json

data = puller.lg.matchups(1)
print(json.dumps(data, indent=2))

# Check what keys are present
print(f"Top-level keys: {data.keys()}")
if 'scoreboard' in data:
    print(f"Scoreboard keys: {data['scoreboard'].keys()}")
```

---

## Common Pitfalls

### 1. Assuming Points Are in Roster Data
**Problem:** The basic `roster()` method doesn't include player statistics.

**Solution:**
- Use `League.player_stats()` for individual player points, OR
- Extract from matchup/scoreboard data (includes roster as sub-resource)

### 2. Not Handling Nested JSON Structure
**Problem:** Yahoo's API returns deeply nested JSON with numeric string keys ('0').

**Solution:**
- Check for multiple possible paths to data
- Use `get()` with defaults instead of direct key access
- Add isinstance() checks before assuming dict structure

### 3. Missing Error Handling
**Problem:** API calls can fail, data structure can vary.

**Solution:**
```python
try:
    # API call
    data = self.lg.matchups(week)

    # Check data exists
    if not data or 'scoreboard' not in data:
        print(f"No data found for week {week}")
        return None

    # Safe access with defaults
    matchups = data.get('scoreboard', {}).get('0', {}).get('matchups', [])

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    return None
```

---

## Verification Checklist

After making changes, verify:

- [ ] No `AttributeError` for `scoreboard()`
- [ ] No `AttributeError` for `.items()` on roster
- [ ] Points are correctly extracted (not 0.0 for all teams)
- [ ] All functions return data in expected format
- [ ] Error handling catches and logs issues
- [ ] Script completes without crashes
- [ ] Data is saved to JSON file
- [ ] JSON file contains expected structure

---

## Getting Help

If you're still having issues:

1. **Check the data structure:**
   ```python
   import json
   print(json.dumps(lg.matchups(1), indent=2))
   ```

2. **Enable detailed logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Check library version:**
   ```bash
   pip show yahoo-fantasy-api
   ```

4. **Consult documentation:**
   - Library: https://yahoo-fantasy-api.readthedocs.io/
   - Yahoo API: https://developer.yahoo.com/fantasysports/guide/

5. **Review example code:**
   - GitHub: https://github.com/spilchen/yahoo_fantasy_api
   - Examples folder in repository

---

## Summary

The main changes needed:
1. Replace `scoreboard()` → `matchups()`
2. Handle `roster()` as a list, not dict
3. Extract points from nested `team_points.total`
4. Add comprehensive error handling
5. Handle Yahoo's complex nested JSON structure

All functions should now work correctly with yahoo-fantasy-api 2.12.2!
