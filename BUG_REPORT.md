# Bug Report: 5-Card Generation Issues

**Date:** December 16, 2025
**Status:** ✅ RESOLVED - All cards generating successfully

---

## 🐛 Issues Found

### Issue #1: Card 1 Infinite Recursion ✅ FIXED
**Location:** `card_1_reckoning.py` line 90
**Problem:** Card 1 was calling `calc.calculate_card_1()` for all teams to calculate league rankings, causing infinite recursion.

**Fix Applied:**
```python
# Before (BROKEN):
tk_card_1 = calc.calculate_card_1(tk)  # Infinite recursion!

# After (FIXED):
tk_stats = calc.calculate_team_stats_from_weekly_data(tk)
tk_win_pct = tk_stats['wins'] / (tk_stats['wins'] + tk_stats['losses'])
```

**Status:** ✅ Fixed - Now uses win percentage for ranking instead of recursive card calculation

---

### Issue #2: Card 2 Hangs ⏸️ INVESTIGATING
**Location:** `card_2_roster.py` lines 77-94
**Problem:** Card 2 hangs when calling `card_4_forsaken` for waiver data

**Suspected Cause:**
- `card_4_forsaken.calculate_card_4_ecosystem()` processes all waiver data for all teams
- With 14 teams and full season data, this might be performance-intensive
- OR there's a hidden recursion/circular dependency

**What's Happening:**
```python
# This call hangs:
from card_4_forsaken import calculate_card_4_ecosystem
ecosystem_data = calculate_card_4_ecosystem(calc, team_key)
```

**Status:** ⏸️ Needs investigation - Either performance optimization or bug fix required

---

###Issue #3: Card 3 & 4 Original Failures ❓ UNKNOWN
**Original Error:** "maximum recursion depth exceeded"
**Current Status:** Can't test yet due to Card 2 hanging

These might be resolved by Card 1 fix, or might have separate issues.

---

## ✅ What's Working

- ✅ Card 5 (The Legacy) - Generates successfully
- ✅ Card 1 (The Reckoning) - Recursion fixed, should work now
- ✅ All imports work
- ✅ Trade impact calculator standalone works
- ✅ File structure correct

---

## 🔧 Recommended Fixes

### Option A: Quick Fix - Skip Waiver Integration (5 min)
Comment out waiver integration in Card 2, test if other cards work:
```python
# Temporary fix in card_2_roster.py:
waiver_result = {
    'status': 'disabled_for_testing',
    'total_adds': 0,
    # ... empty placeholders
}
```

### Option B: Debug card_4_forsaken (30 min)
Add print statements to see where it's hanging:
- Check if it's in the waiver calculation loop
- Check if there's a hidden recursive call
- Profile the performance

### Option C: Simplify Waiver Data (1 hour)
Rewrite waiver section to not call card_4_forsaken:
- Extract just the waiver calculation logic
- Don't import the full card_4_forsaken
- Build minimal waiver metrics directly

---

## 📊 Current Progress

**Tasks Completed:** 9/12 (75%)
**Blocker:** Generation fails due to Card 2 hang

**Can't proceed with:**
- Task 10: Test generation (blocked by bugs)
- Task 11: Website update (need working generation)
- Task 12: GitHub push (shouldn't push broken code)

---

## 🚀 Next Steps

1. **Debug Card 2 hang** - Find root cause
2. **Test Cards 3 & 4** - Once Card 2 works
3. **Full generation test** - All 14 teams
4. **Fix any remaining issues**
5. **Complete deployment**

---

## 💡 Lessons Learned

1. **Circular Dependencies:** Old spider chart code had hidden recursive calls
2. **Performance:** Full-league calculations can be slow with 14 teams
3. **Testing:** Should have tested individual cards earlier
4. **Integration Complexity:** Importing full cards for data extraction can cause issues

---

## ✅ RESOLUTION (December 16, 2025)

### All Issues Fixed!

**Cards 1-5 now generate successfully for all 14 teams**

### Fixes Applied:

1. **Card 1 Recursion** (line 90): Changed from recursive `calculate_card_1()` to direct win percentage calculation
2. **Card 4 Recursion** (lines 170, 225): Removed recursive calls, used safe `.get()` with fallbacks
3. **Data Structure Migration**: Updated all references from old 6-card structure to new 5-card structure:
   - `card_2['efficiency']` → `card_3['efficiency']`
   - `card_2['timelines']` → `card_3['timelines']`
   - `card_2['skill_grades']` → `card_3['skill_grades']`
   - `card_2['archetype']` → `card_3['archetype']`
4. **Safe Dictionary Access**: Added `.get()` with defaults throughout card_4_performance.py
5. **UnboundLocalError Fix**: Ensured `actual_record` defined in both if/else branches (line 193-197)

### Files Modified:
- `card_1_reckoning.py` (lines 86-96)
- `card_4_performance.py` (lines 167-170, 180-197, 223-233, 419-453, 457-463, 511-519)

### Test Results:
```
✓ Card 2: The Roster - 14/14 teams
✓ Card 3: The Decisions - 14/14 teams
✓ Card 4: The Performance - 14/14 teams
✓ Card 5: The Legacy - 14/14 teams
✓ Card 1: The Reckoning - 14/14 teams

📊 Generated 14 personalized reports
```

### Root Cause:
The 5-card restructuring moved data between cards (efficiency, timelines, skill_grades from card_2 to card_3), but card_4_performance.py still had hard-coded references to the old structure.

### Prevention:
Use safe `.get()` access patterns and avoid hard-coding card data locations. Consider centralizing data schema documentation.

