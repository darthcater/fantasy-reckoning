# Value Over Replacement (VOR) Analysis for Fantasy Reckoning

## Executive Summary

**Current State**: Cards use round-based draft value and flat thresholds (5 PPG for waiver efficiency)

**VOR Enhancement**: League-specific replacement levels calculated from actual roster settings

**Recommendation**: HIGH priority for Card 1, MEDIUM for Card 2, LOW for Cards 4/5

---

## What VOR Adds

### Core Concept
Instead of judging players by draft position alone, VOR measures value against the **next available player** at that position based on your league's actual settings.

**Why it matters:**
- TE12 vs replacement TE (TE18) = HUGE gap in shallow leagues
- WR12 vs replacement WR (WR42) = smaller gap (more depth)
- Captures **positional scarcity** automatically

**Formula from your data:**
```
band_start_P = (teams × starters_P + flex_alloc_P) + 1
replacement_P = mean(points[band_start_P : band_start_P + band_size_P])
VOR = player_points - replacement_P
```

---

## Impact Analysis by Card

### 🔥 Card 1: The Draft Tribunal (HIGH VALUE)

#### Current Method
- Compares draft position to finish position
- "Round-based value": Drafted Rd 3, finished as RB8 → good value
- Problem: Doesn't account for positional scarcity

#### With VOR Enhancement
**What changes:**
- Calculate VOR for every player drafted
- Grade draft by **total VOR acquired** vs league average
- Identify steals/busts by VOR, not just round differential

**Example Reckoning Statement:**
> **Current**: "You drafted Travis Kelce in Round 2. He finished as TE3. Decent value."
>
> **With VOR**: "You drafted Travis Kelce in Round 2 (pick 18). He delivered 78 VOR points—the value of a Round 1 pick. Your best steal."

**Specific improvements:**
1. **Better steal/bust identification**
   - Current: "2+ round difference"
   - VOR: "VOR in top/bottom quartile for draft position"

2. **League-specific accuracy**
   - Superflex leagues: QB VOR automatically higher
   - TE Premium: TE VOR automatically higher
   - Deep benches: Replacement level drops, VOR gaps widen

3. **Draft efficiency score**
   - Current: Weighted round value
   - VOR: Total VOR / Expected VOR for draft position
   - More meaningful grade

**Implementation complexity:** MEDIUM
- Need to parse league settings (starters, flex allocation)
- Calculate replacement bands per position
- Integrate into existing draft analysis

**Value add:** ⭐⭐⭐⭐⭐ (Transforms draft analysis accuracy)

---

### 💡 Card 2: The Three Fates (MEDIUM VALUE)

#### Current Method
- Optimal lineup = highest-scoring starters
- Bench points = raw points left on bench
- Problem: Leaving WR1 on bench ≠ leaving WR3 on bench

#### With VOR Enhancement
**What changes:**
- Weight bench points by VOR, not raw points
- "Costly benching" = high-VOR player left on bench
- More accurate opportunity cost

**Example Reckoning Statement:**
> **Current**: "Week 7: You left 18 points on the bench."
>
> **With VOR**: "Week 7: You benched Amon-Ra St. Brown (28 VOR points above replacement). That error cost you the week."

**Specific improvements:**
1. **Weighted bench regret**
   - Not all bench points equal
   - Benching elite players >> benching WR3/RB3

2. **Position-aware optimization**
   - Starting weak TE when elite WR on bench = bigger mistake in standard
   - VOR quantifies this automatically

**Implementation complexity:** LOW-MEDIUM
- Already calculating optimal lineups
- Just need to add VOR weighting to bench analysis

**Value add:** ⭐⭐⭐ (More accurate lineup regret)

---

### 🤔 Card 4: The Forsaken (LOW-MEDIUM VALUE)

#### Current Method
- Waiver efficiency: Added player started + scored ≥5 PPG
- Flat threshold across all positions
- Problem: 5 PPG is more valuable for TE than WR

#### With VOR Enhancement
**What changes:**
- Position-specific replacement thresholds
- "Productive add" = player scored above replacement for position
- More accurate efficiency metric

**Example:**
> **Current threshold**: 5 PPG flat
> - QB scoring 15 PPG = productive ✓
> - TE scoring 6 PPG = productive ✓
>
> **VOR threshold**: Position-specific
> - QB scoring 15 PPG = below QB replacement (18 PPG) ✗
> - TE scoring 6 PPG = above TE replacement (4 PPG) ✓

**Specific improvements:**
1. **Fairer efficiency measurement**
   - Account for positional depth differences
   - Streaming QB vs streaming TE valued appropriately

**Implementation complexity:** LOW
- Replace flat 5 PPG with `replacement_P` lookup
- Minimal code change

**Value add:** ⭐⭐ (More accurate, but marginal improvement for user experience)

---

### 📊 Card 5: The Final Ledger (LOW VALUE)

#### Current Method
- Win attribution by category (draft, lineups, waivers, luck)
- Efficiency metrics compared to league

#### With VOR Enhancement
**What changes:**
- Could add "positional VOR advantage" analysis
- e.g., "Your RBs delivered +45 VOR vs league average"

**Implementation complexity:** MEDIUM
- Requires league-wide VOR calculations
- Integration with win attribution logic

**Value add:** ⭐ (Interesting but not game-changing)

---

## Recommendation Matrix

| Card | Current Quality | VOR Enhancement Value | Implementation Cost | Priority |
|------|----------------|----------------------|---------------------|----------|
| Card 1 | Good | ⭐⭐⭐⭐⭐ | Medium | **HIGH** |
| Card 2 | Good | ⭐⭐⭐ | Low-Medium | **MEDIUM** |
| Card 4 | Good | ⭐⭐ | Low | **LOW** |
| Card 5 | Good | ⭐ | Medium | **SKIP** |

---

## Implementation Strategy

### Phase 1: Foundation (Required for all VOR features)
**Build VOR calculation engine**

```python
def calculate_replacement_levels(calc, league_settings):
    """
    Calculate position-specific replacement levels

    Returns:
        {
            'QB': 15.2,  # avg PPG of replacement QBs
            'RB': 8.4,
            'WR': 9.1,
            'TE': 4.3
        }
    """
    # Parse league settings
    teams = len(calc.teams)
    starters = parse_starters(league_settings)
    flex_allocation = estimate_flex_usage(calc)  # historical flex usage

    # Calculate bands per position
    for position in ['QB', 'RB', 'WR', 'TE']:
        band_start = (teams * starters[position]) + flex_allocation[position] + 1
        band_size = teams  # or 2× for deeper baseline

        # Get players in replacement band
        players = rank_players_by_position(calc, position)
        replacement_players = players[band_start:band_start + band_size]

        # Average their points
        replacement_levels[position] = mean(p.points for p in replacement_players)

    return replacement_levels
```

**Complexity**: ~100-150 lines
**Dependencies**: League settings parser

---

### Phase 2: Card 1 Integration (HIGH PRIORITY)

**Replace round-based value with VOR-based value:**

```python
# OLD: Round difference
round_diff = pick_round - value_round
weighted_value = round_diff * weight

# NEW: VOR-based value
player_vor = player_points - replacement_levels[position]
expected_vor = get_expected_vor_for_pick(pick_number, position)
vor_value = player_vor - expected_vor  # Positive = steal, negative = bust
```

**Changes:**
1. Calculate replacement levels at start
2. Add VOR to each player's draft analysis
3. Rank steals/busts by VOR surplus/deficit
4. Update draft grade to use total VOR

**Testing approach:**
- Run on sample league
- Compare round-based vs VOR-based steals/busts
- Verify VOR captures TE scarcity, QB depth, etc.

**Complexity**: ~200 lines of changes

---

### Phase 3: Card 2 Integration (MEDIUM PRIORITY)

**Weight bench regret by VOR:**

```python
# OLD: Raw bench points
bench_regret = optimal_points - actual_points

# NEW: VOR-weighted bench regret
for benched_player in high_value_bench:
    player_vor = benched_player.points - replacement_levels[position]
    if player_vor > 20:  # High-VOR player
        weighted_regret += player_vor * 1.5  # Weight heavily
```

**Complexity**: ~50-100 lines

---

## Arguments FOR VOR Implementation

### 1. **Accuracy in non-standard leagues** ⭐⭐⭐
- Superflex/2QB leagues: QB VOR skyrockets
- TE Premium: TE becomes more valuable than WR2/RB2
- Current round-based system doesn't adapt

### 2. **Industry standard metric** ⭐⭐
- Used by FantasyPros, ESPN, Yahoo rankings
- Users may expect it
- Adds credibility

### 3. **Automatic league adaptation** ⭐⭐⭐
- No manual tuning needed
- Works for 8-team, 10-team, 12-team, 14-team leagues
- Handles custom roster configurations

### 4. **Better draft insights** ⭐⭐⭐⭐
- "You got 3 Round 1-value picks in Rounds 4-6" is more meaningful than "3 players finished 2+ rounds better"
- Quantifies positional advantage

### 5. **Defensibility** ⭐⭐
- When a user says "That's not a bust!", you can point to VOR
- More objective than round-based heuristics

---

## Arguments AGAINST VOR Implementation

### 1. **User comprehension** ⭐⭐⭐
- "Value Over Replacement" is jargon
- Users understand "Round 3 pick, finished as RB8"
- May need education/explanation

### 2. **Implementation complexity** ⭐⭐
- Requires league settings parsing
- Edge cases: custom positions, IR slots, taxi squads
- More things that can break

### 3. **Minimal impact on Cards 4/5** ⭐
- 5 PPG threshold is "good enough" for waiver efficiency
- VOR adds precision but not insight

### 4. **Testing burden** ⭐⭐
- Need test cases for: standard, PPR, superflex, TE premium, 8/10/12/14 team leagues
- More edge cases = more bugs

### 5. **Scope creep** ⭐
- Already have 16+ solid insights
- VOR is optimization, not new insight
- Diminishing returns

---

## Final Recommendation

### ✅ DO: Implement VOR for Card 1 (The Draft Tribunal)

**Why:**
- Biggest accuracy improvement
- Draft is most important card for league-specific differences
- Users expect sophisticated draft analysis

**Approach:**
1. Build VOR calculation engine (Phase 1)
2. Add as **supplemental** data in Card 1, not replacement
3. Show both round-based value AND VOR
4. Example output:
   ```json
   {
     "player_name": "Travis Kelce",
     "round_diff": 1,  // Keep existing
     "vor": 78.4,       // NEW
     "vor_grade": "Elite steal",  // NEW
     "note": "Round 2 value, delivered Round 1 VOR"
   }
   ```

**Timeline**: Medium complexity, ~4-6 hours of work

---

### 🤔 MAYBE: Implement VOR for Card 2 (The Three Fates)

**Why:**
- Adds nuance to lineup decisions
- Relatively easy once VOR engine exists

**Wait for:** User feedback on Card 1 VOR
- If users love VOR in Card 1 → add to Card 2
- If users confused → skip

---

### ❌ SKIP: VOR for Cards 4 & 5

**Why:**
- Marginal value add
- Flat thresholds are simpler and "good enough"
- Focus on bigger opportunities

---

## Conclusion

VOR is a **powerful enhancement for Card 1** that would make Fantasy Reckoning's draft analysis best-in-class, especially for non-standard leagues. It's worth implementing as the next major feature.

For other cards, the value is more marginal—wait to see if users demand more sophisticated metrics after seeing VOR in Card 1.

**Estimated total effort:** 6-10 hours
- 2-3 hours: VOR calculation engine
- 3-5 hours: Card 1 integration
- 1-2 hours: Testing & edge cases
