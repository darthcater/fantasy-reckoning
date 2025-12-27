# Fantasy Reckoning Production Checklist

**Purpose**: Comprehensive QA checklist for verifying all calculations, data handling, and edge cases before launch.

**Last Updated**: 2025

---

## Pre-Flight Checks

### Data Validation
- [ ] League file auto-detection works (`_find_latest_league_file()`)
- [ ] League file loads successfully (valid JSON structure)
- [ ] All required data keys present: `league`, `teams`, `weekly_data`, `transactions`, `draft`
- [ ] Team count ≥ 4 (minimum league size validation)
- [ ] Current week value is valid (1-18)
- [ ] Playoff start week is valid (typically 15)

### League Compatibility
- [ ] Draft type detection works (`auction` vs `snake` vs `unknown`)
- [ ] Roster configuration detected correctly (`num_starters`, `positions`)
- [ ] Scoring type identified (`head` vs `points`)
- [ ] Superflex detection works (QB in flex positions)
- [ ] IDP league detection (DL, LB, DB positions)
- [ ] Special format detection (guillotine, best ball, empire - should error)

### Feature Flags Set Correctly
- [ ] `has_draft_data` = True if draft picks exist
- [ ] `has_roster_positions` = True if league config present
- [ ] `has_scoring_settings` = True if stat modifiers present
- [ ] `supports_superflex` flagged correctly
- [ ] `supports_idp` flagged correctly
- [ ] `has_waiver_data` = True if transactions exist

---

## Card 1: The Leader

### Manager Archetype & Skill Percentiles

#### Archetype Assignment (League-Level)
- [ ] All teams processed in Pass 1 (Cards 2-4 generated first)
- [ ] Archetype scoring uses correct data from Cards 2-4
- [ ] League-level assignment enforces MAX 3 teams per archetype
- [ ] All 10 archetypes available: Tinkerer, Loyalist, Dealer, Hermit, Gambler, Conservative, Optimizer, Erratic, Rock, Rollercoaster
- [ ] Capacity constraints enforced (no archetype assigned >3 times)
- [ ] Archetype distribution logged and verified
- [ ] Fallback archetype ('rock') used only when necessary

#### Draft Percentile Calculation
- [ ] Draft rank retrieved from Card 2 (not Card 1 - circular dependency check)
- [ ] Draft rank defaults to 7 if unavailable
- [ ] Percentile formula: `((num_teams - rank + 1) / num_teams) * 100`
- [ ] Percentile rounded to 1 decimal place
- [ ] Grade mapping from percentile correct (A+ to F)

#### Lineup Percentile Calculation
- [ ] Lineup efficiency percentile from Card 3
- [ ] Defaults to 50 if Card 3 unavailable
- [ ] Percentile range: 0-100
- [ ] Efficiency based on actual vs optimal lineup comparison

#### Bye Week Percentile Calculation
- [ ] `calculate_league_bye_week_percentile()` called correctly
- [ ] Bye weeks identified by 2+ starters scoring 0 pts
- [ ] Replacement player performance tracked
- [ ] League-wide comparison done correctly
- [ ] Percentile calculation: `(teams_below / (num_teams - 1)) * 100`

#### Waiver Percentile Calculation
- [ ] Waiver scores cached (`_waiver_scores_cache`) to avoid recalculation
- [ ] Waiver score = total_points_started - costly_drops_value
- [ ] All teams scored for comparison
- [ ] Percentile: `(teams_below / (num_teams - 1)) * 100`
- [ ] Defaults to 50 if no waiver data

#### Excellence Score
- [ ] Four dimensions weighted equally (25% each): Draft, Lineups, Bye Weeks, Waivers
- [ ] Formula: `draft_pct * 0.25 + lineup_pct * 0.25 + bye_pct * 0.25 + waiver_pct * 0.25`
- [ ] Score range: 0-100
- [ ] Rounded to 1 decimal place

#### Overall Rank
- [ ] Ranked by win percentage (not recursive card generation)
- [ ] Uses `calculate_team_stats_from_weekly_data()` for accurate wins
- [ ] Rank format: "X/Y" where Y = num_teams
- [ ] Percentile calculated from rank

#### Dimension Breakdown
- [ ] All 4 dimensions present: draft, lineups, bye_weeks, waivers
- [ ] Each dimension has: percentile, grade, weight (0.25), contribution, label
- [ ] Grades map correctly to percentiles (A+ ≥95, A ≥90, etc.)
- [ ] Contribution = percentile * weight

#### Manager Profile
- [ ] Strongest dimension identified (highest percentile)
- [ ] Weakest dimension identified (lowest percentile)
- [ ] Weakness label generated correctly
- [ ] Manager summary categorizes performance (well-rounded, one-dimensional, etc.)

#### Improvement Potential
- [ ] Biggest opportunity = weakest dimension
- [ ] Target percentile = 70
- [ ] Potential gain calculated: `max(0, 70 - current_percentile)`
- [ ] Ceiling score = current + (gain * weight)
- [ ] Ceiling rank estimated from all team scores
- [ ] Message formatted with current → target improvement

### Edge Cases
- [ ] No draft data: Card 1 shows "N/A" for draft metrics
- [ ] Offline/keeper draft: Handled gracefully with warnings
- [ ] First week of season: Handle minimal data
- [ ] Ties in records: Tiebreaker logic works
- [ ] Single-digit leagues: Percentiles still meaningful
- [ ] All dimensions at 50th percentile: No div-by-zero errors

### Data Quality
- [ ] No null/undefined values in percentiles
- [ ] All percentiles in range [0, 100]
- [ ] Grades valid (A+ through F)
- [ ] Archetype name and description present
- [ ] No circular dependencies (Card 1 depends on 2-4, not vice versa)

---

## Card 2: The Ledger

### Draft Analysis

#### Snake Draft
- [ ] Draft type detection: `draft_type == 'snake'`
- [ ] All drafted players collected with positions
- [ ] Position detection uses `_get_player_position()` from weekly roster data
- [ ] Replacement levels calculated for all positions (QB, RB, WR, TE, K, DEF)
- [ ] VOR calculation: `ppg - replacement_ppg`
- [ ] VOR grades assigned correctly (Elite ≥8, Strong ≥5, Solid ≥2, Replacement ≥0, Below <0)

**Positional Rankings**:
- [ ] Draft rank assigned by overall pick order
- [ ] Finish rank assigned by total points within position
- [ ] Expected round calculated using `_calculate_expected_round()`
- [ ] Round difference = draft_round - value_round
- [ ] Weighted value: early rounds (≤3) get 3x weight, mid (4-6) get 2x, late get 1x

**Steals & Busts**:
- [ ] Steals: round_diff ≥ +2 (drafted 2+ rounds later than deserved)
- [ ] Busts: round_diff ≤ -2 (drafted 2+ rounds earlier than deserved)
- [ ] Top 3 steals and top 3 busts identified
- [ ] VOR-based steals: VOR ≥5 AND drafted round 4+
- [ ] VOR-based busts: VOR <0 AND drafted rounds 1-8

**Walked Past Gold**:
- [ ] Top 20% performers identified
- [ ] Passed opportunities counted (available at manager's pick but taken later)
- [ ] Threshold: passed 2+ times
- [ ] Sorted by `times_passed * total_points`
- [ ] Top 3 missed opportunities shown

**League Comparison**:
- [ ] All teams' draft value scores calculated
- [ ] Manager ranked by weighted value (higher = better)
- [ ] Grade assigned by percentile (A ≥80%, B ≥60%, C ≥40%, D ≥20%, F <20%)
- [ ] VOR surplus = total_vor - expected_vor

#### Auction Draft
- [ ] Draft type detection: `draft_type == 'auction'`
- [ ] Cost tracking for all picks
- [ ] Position-specific replacement levels calculated
- [ ] VOR calculated for all picks
- [ ] ROI metric: `cost / total_points` (lower = better)

**Positional Spending Analysis**:
- [ ] Budget percentage calculated for each position
- [ ] League average spending by position calculated
- [ ] Spending difference: `pos_spent - league_avg_spent`
- [ ] Points difference: `pos_points - league_avg_points`
- [ ] Verdict assigned: GOOD VALUE, OVERPAID, WEAK, FAIR VALUE, BARGAIN

**Steals with Context**:
- [ ] Minimum 50 total points to qualify
- [ ] Top 5 by cost efficiency ($/point)
- [ ] Contextual explanation generated (cost saved vs avg, points surplus, VOR)
- [ ] Performance tier assigned based on VOR
- [ ] Value summary formatted

**Busts with Context**:
- [ ] Minimum $20 cost to qualify
- [ ] Top 5 by inefficiency (highest $/point)
- [ ] Cost tier determined (elite, mid-tier, starter)
- [ ] Expected points from tier calculated
- [ ] Points shortfall = expected - actual
- [ ] Production tier assigned (below replacement, replacement, below average, average)
- [ ] Estimated win impact: `shortfall / 30`
- [ ] Only added if shortfall > 0 (actual underperformance)

**The Verdict**:
- [ ] Total spent, total points, ROI calculated
- [ ] League average ROI calculated
- [ ] Ranked by ROI (lower = better)
- [ ] Grade percentile calculated
- [ ] Problems identified (3+ busts, weak positions, poor ROI)
- [ ] Verdict tone set (elite, mediocre, poor)

**The Sentence**:
- [ ] Crime identified (biggest bust, neglected position, or mediocrity)
- [ ] Evidence presented with specific numbers
- [ ] Damage quantified (wins lost)
- [ ] Punishment assigned
- [ ] Path to redemption outlined
- [ ] Expected improvement projected

### Waiver Analysis
- [ ] All waiver adds identified from transactions (`type == 'add'` or `'add/drop'`)
- [ ] Player type filtered to `'add'` (not drops)
- [ ] Week calculated from timestamp
- [ ] Points started tracked (not bench points)
- [ ] Weeks started counted for each pickup
- [ ] Total points started summed
- [ ] Productive adds: ≥10 points started
- [ ] Efficiency rate: `(productive_adds / total_adds) * 100`
- [ ] Best adds: top 5 by points started

### Trade Analysis
- [ ] Trade transactions filtered (`type == 'trade'`)
- [ ] Team involvement checked (any player with destination = team_key)
- [ ] Acquired vs gave_away players separated correctly
- [ ] ROS points calculated from trade week forward
- [ ] Started vs benched points tracked separately
- [ ] Utilization percentage: `(started / total) * 100`
- [ ] Net total impact: `acquired_total - gave_away_total`
- [ ] Net started impact: `acquired_started - gave_away_started`
- [ ] Trade verdict: BIG WIN (>10), MINOR WIN (>0), WASH (±1), MINOR LOSS (<0), BIG LOSS (<-10)
- [ ] Overall verdict based on total started impact

### Costly Drops Analysis
- [ ] Drops inferred from weekly roster changes (player in week N, not in N+1)
- [ ] Trades excluded (player has destination_team_key in trade transaction)
- [ ] Dropped player tracking includes: player_id, name, position, drop_week
- [ ] Pickup detection across all other teams starting from drop week
- [ ] ROS points for new team calculated
- [ ] Started points threshold: ≥5 points
- [ ] Total value given away summed (started points only)
- [ ] Costly drops sorted by started points (highest first)
- [ ] Most costly drop identified
- [ ] Verdict assigned (No drops, Minor <20, Questionable 20-50, Poor 50-100, Massive >100)

### Points Story Summary
- [ ] Draft points total calculated
- [ ] Waiver points started total
- [ ] Trade net impact (started)
- [ ] Costly drops total
- [ ] All four acquisition channels tracked

### Edge Cases
- [ ] No draft data: error message with explanation
- [ ] No transactions: waiver/trade sections show "No data"
- [ ] No drops: "No drops made" verdict
- [ ] Player not found in weekly data: skip gracefully
- [ ] Trade with multiple players: all players processed
- [ ] Same player traded multiple times: each trade tracked separately
- [ ] Auction without costs: detection falls back to snake
- [ ] Division by zero in ROI calculations: check for total_points > 0
- [ ] Timestamp parsing errors: fall back to week 1
- [ ] Missing player names: use "Player {player_id}"

### Data Precision
- [ ] All point totals rounded to 1 decimal place
- [ ] Percentages rounded to 1 decimal place
- [ ] Efficiency rates in range [0, 100]
- [ ] ROI values rounded to 2-3 decimal places
- [ ] VOR values rounded to 1 decimal place

### Validation
- [ ] Draft grade present (A-F or N/A)
- [ ] Draft rank is integer 1 to num_teams
- [ ] Waiver efficiency 0-100%
- [ ] Trade verdict is valid enum
- [ ] All player IDs converted to strings for comparison
- [ ] No negative point totals (unless legitimately negative)

---

## Card 3: The Lineup

### Optimal Lineup Calculation

#### Core Algorithm
- [ ] All players collected: starters + bench
- [ ] IR players excluded from optimization
- [ ] Injured players filtered if `filter_injured=True` (Q, D, O, IR status)
- [ ] Required positions extracted from actual starters
- [ ] Players sorted by points (highest first)
- [ ] Greedy algorithm fills each position with best eligible player
- [ ] Position eligibility checked: `position in player.eligible_positions`
- [ ] Used players tracked (no double-assignment)
- [ ] Optimal points summed from optimal lineup
- [ ] Actual points summed from non-IR starters

#### Metrics
- [ ] Optimal points calculated correctly
- [ ] Actual points calculated correctly (excluding IR)
- [ ] Points left on bench = optimal - actual
- [ ] Efficiency percentage: `(actual / optimal) * 100`
- [ ] Handles optimal_points = 0 (div by zero protection)

### Archetype Determination

#### League-Relative Activity
- [ ] All team transaction rates calculated
- [ ] Transaction rate = `num_transactions / current_week`
- [ ] Sorted for percentile calculation
- [ ] Activity percentile: `(rank / total_teams) * 100`

#### Effectiveness Calculation
- [ ] Total points added via transactions calculated
- [ ] ROS points tracked from acquisition week forward
- [ ] Effective adds: ≥20 ROS points
- [ ] Efficiency rate: `(effective_adds / total_adds) * 100`
- [ ] ROI per transaction: `total_points_added / num_transactions`

#### Archetype Assignment (2D Matrix)
- [ ] Activity levels: Low (<33%), Medium (33-66%), High (>66%)
- [ ] Effectiveness levels: Low (<40%), High (≥40%)
- [ ] 6 archetypes correctly assigned:
  - [ ] The Idle Genius (Low activity, High efficiency)
  - [ ] The Passive Loser (Low activity, Low efficiency)
  - [ ] The Active Optimizer (High activity, High efficiency)
  - [ ] The Busy Fool (High activity, Low efficiency)
  - [ ] The Balanced Strategist (Medium activity, High efficiency)
  - [ ] The Cautious Tinkerer (Medium activity, Low efficiency)

#### Archetype Impact Analysis
- [ ] Activity rank calculated: `sum(1 for rate if rate < avg) + 1`
- [ ] Strategy description includes league context (rank/total)
- [ ] Effectiveness description includes hit rate percentage
- [ ] Context includes transaction count and ROS points
- [ ] Verdict tailored to archetype (positive for good, negative for bad)
- [ ] Draft rank cross-referenced for Idle Genius and Passive Loser

### Timeline Calculations

#### Actual Record
- [ ] Wins counted from weekly results
- [ ] Losses counted from weekly results
- [ ] Ties counted from weekly results
- [ ] Total points summed across all weeks
- [ ] Result field used: 'W', 'L', or 'T'

#### Optimal Lineup Record
- [ ] Optimal lineup calculated for each week
- [ ] Optimal points compared to opponent points
- [ ] Wins counted: optimal > opponent
- [ ] Losses counted: optimal < opponent
- [ ] Ties counted: optimal == opponent
- [ ] Total optimal points summed

#### Wins Left on Table
- [ ] Lineup wins lost = optimal_wins - actual_wins
- [ ] Waiver wins lost estimated (placeholder for full simulation)
- [ ] Total wins lost = max of both calculations

### Efficiency Metrics

#### League Benchmarking
- [ ] All teams' efficiency calculated
- [ ] League average efficiency computed
- [ ] Playoff teams identified (top 6 by wins)
- [ ] Playoff average efficiency calculated
- [ ] Efficiency gap to playoffs: `playoff_avg - manager_efficiency`

#### League Ranking
- [ ] Efficiency dictionary built for all teams
- [ ] `calculate_league_ranking()` called with `reverse=True` (higher is better)
- [ ] Rank, percentile, gap_to_average returned
- [ ] Grade assigned from percentile

### Bye Week Management

#### Detection & Tracking
- [ ] Weeks with 2+ starters on bye identified
- [ ] Starters on bye: scored 0 but had points in other weeks
- [ ] Weekly bye details collected: week, players_on_bye, total_points, bye_count
- [ ] Replacement performances tracked (week totals)
- [ ] Average replacement points calculated

#### League Comparison
- [ ] All teams' bye week performance calculated
- [ ] League average bye performance computed
- [ ] Performance vs league calculated: `manager_avg - league_avg`
- [ ] Preventable bye losses identified (scored below avg AND lost by that margin)

#### Summary Generation
- [ ] Bye week count reported
- [ ] Average replacement points shown
- [ ] League average shown for context
- [ ] Verdict: positive if ≥ league avg, negative if below
- [ ] Preventable losses counted

### Pivotal Moments Analysis

#### Fatal Error Detection
- [ ] Lost close game (result == 'L')
- [ ] Margin ≤ 20 points
- [ ] Bench left ≥ 15 points
- [ ] Impact score = `bench_left / margin`
- [ ] Sorted by impact (highest first)

#### Clutch Call Detection
- [ ] Won close game (result == 'W')
- [ ] Margin ≤ 20 points
- [ ] Bench left ≤ 10 points
- [ ] Impact score = `(20 - bench_left) / margin`
- [ ] Sorted by impact (highest first)

#### Moment Selection
- [ ] Best fatal error identified
- [ ] Best clutch call identified
- [ ] Most impactful moment selected (compare impact scores)
- [ ] Fallback logic: worst loss OR best win if no qualifying moments

#### Player-Specific Analysis
- [ ] Worst swap identified (position-eligible only!)
- [ ] Started player vs benched player comparison
- [ ] Respect position eligibility: `selected_position in bench_player.eligible_positions`
- [ ] IR players excluded from swaps
- [ ] Point gain calculated
- [ ] Decision gap reported

### Which Fate Awaits You

#### Path of Repetition
- [ ] Projected record = actual record
- [ ] Outlook: stagnation message
- [ ] Probability: "Likely if you do not heed the warnings"

#### Path of Discipline
- [ ] Projected wins = actual + lineup_wins_gap
- [ ] Capped at 14 wins
- [ ] Improvement message includes lineup efficiency target
- [ ] Requirement: "Study projections, set lineups early, trust data"
- [ ] Probability: "Achievable with focus"
- [ ] If lineup_wins_gap < 2: "Minimal gains available"

#### Path of Perfection
- [ ] Projected wins = optimal_adds_wins
- [ ] Improvement = total gains from all decisions
- [ ] Requirement: optimal adds analysis
- [ ] Probability: "Nearly impossible"
- [ ] Note: "Requires clairvoyance"

#### Recommended Path
- [ ] 'discipline' if lineup_wins_gap ≥ 2
- [ ] 'repetition' otherwise
- [ ] The choice message: "Three paths lie before you"

### Edge Cases
- [ ] No opponent data: use league average as proxy
- [ ] Missing weekly data: skip week gracefully
- [ ] All players on IR: optimal lineup = 0 points
- [ ] No valid swaps (all positions filled optimally): show generic message
- [ ] Ties in games: handle separately from wins/losses
- [ ] Week 1 only: handle minimal data for averages
- [ ] No transactions: archetype defaults appropriately
- [ ] Zero total points: div by zero protection in efficiency calc

### Data Precision
- [ ] All point totals rounded to 1 decimal
- [ ] Efficiency percentages rounded to 1 decimal
- [ ] Transactions per week rounded to 2 decimals
- [ ] Activity percentile rounded to 1 decimal
- [ ] Efficiency rate rounded to 1 decimal
- [ ] ROI per transaction rounded to 1 decimal

### Validation
- [ ] Archetype type is valid string
- [ ] All timeline records have wins, losses, ties fields
- [ ] Efficiency percentage in range [0, 100]
- [ ] Bye week count ≥ 0
- [ ] Preventable losses ≤ total losses
- [ ] Pivotal moment type is 'fatal_error', 'clutch_call', or None
- [ ] Activity percentile in [0, 100]
- [ ] No null values in archetype impact fields

---

## Card 4: The Legend

### All-Play Record Calculation

#### Core Calculation
- [ ] Every week processed for regular season only
- [ ] Manager score compared to ALL other teams (not just matchup opponent)
- [ ] All-play wins: count teams beaten each week
- [ ] All-play losses: count teams who beat manager each week
- [ ] Ties ignored (rare, not counted)
- [ ] Total games = all_play_wins + all_play_losses

#### Win Percentage
- [ ] All-play win % = `(wins / total_games) * 100`
- [ ] Division by zero protection (total_games > 0)
- [ ] Rounded to 1 decimal place

#### Expected vs Actual
- [ ] Expected actual wins = `(all_play_win_pct / 100) * weeks_played`
- [ ] Actual wins from `calculate_team_stats_from_weekly_data()`
- [ ] Schedule luck = actual_wins - expected_wins
- [ ] Luck categories:
  - [ ] Very Lucky: ≥ +2 wins
  - [ ] Slightly Lucky: ≥ +1 win
  - [ ] Neutral: -1 to +1
  - [ ] Slightly Unlucky: ≤ -1 win
  - [ ] Very Unlucky: ≤ -2 wins

#### League Ranking
- [ ] All teams' all-play % calculated
- [ ] `calculate_league_ranking()` called with `reverse=True`
- [ ] Rank, percentile, league avg, gap returned
- [ ] Grade assigned from percentile

### Win Attribution Analysis

#### Baseline
- [ ] Total games counted
- [ ] Baseline wins = `total_games / 2` (50% win rate, i.e., 7-7 in 14 games)

#### Skill Factors (Repeatable)

**Draft Impact**:
- [ ] Draft rank from Card 2 (Card 1 not yet generated - avoid circular dependency)
- [ ] Median rank = `(num_teams + 1) / 2`
- [ ] Draft impact = `(median_rank - draft_rank) * 0.15` wins per rank
- [ ] Defaults to median if rank unavailable

**Lineup Impact**:
- [ ] Manager efficiency from Card 2 (`lineup_efficiency_pct`)
- [ ] Baseline efficiency = 50%
- [ ] Lineup impact = `(manager_eff - 50) * 0.08` wins per 1% efficiency
- [ ] Alternative: use preventable losses from Card 3
- [ ] Use minimum of both approaches (conservative)

**Waiver Impact**:
- [ ] Waiver points added from Card 4 (if available)
- [ ] League average waiver points estimated: `avg_transactions * 10`
- [ ] Waiver impact = `(points_diff / 100) * 0.5` wins per 100 points
- [ ] Defaults to 0 if Card 4 data unavailable

**Total Skill Impact**:
- [ ] Sum of draft + lineup + waiver impacts
- [ ] Can be positive or negative

#### Luck Factors (Won't Repeat)

**Schedule Luck**:
- [ ] Expected wins calculated per week (teams beaten / (total - 1))
- [ ] Schedule luck = actual_wins - expected_wins
- [ ] Rounded to nearest 0.5
- [ ] Tough opponent weeks tracked (opponent in top 3 scorers)
- [ ] Weak opponent weeks tracked (opponent in bottom 3 scorers)
- [ ] Narrative generated from details

**Opponent Mistakes**:
- [ ] Each win checked for opponent lineup errors
- [ ] Opponent's optimal lineup calculated
- [ ] Lucky win if opponent_optimal > manager_score
- [ ] Win margin = manager_score - opponent_score
- [ ] Details tracked: week, scores, bench left, margin
- [ ] Rounded to nearest 0.5
- [ ] Top 2 examples shown in narrative

**Random Luck**:
- [ ] Explained wins = baseline + skill + schedule + opponent_mistakes
- [ ] Random luck = actual_wins - explained_wins
- [ ] Captures injury timing, boom/bust weeks, etc.
- [ ] Rounded to nearest 0.5

**Total Luck Impact**:
- [ ] Sum of schedule + opponent_mistakes + random
- [ ] Can be positive or negative

#### Attribution Breakdown
- [ ] All factors present in breakdown
- [ ] Skill factors: draft, lineups, waivers (with category='skill')
- [ ] Luck factors: schedule_luck, opponent_mistakes, random_luck (with category='luck')
- [ ] Each factor has impact value, note, details, narrative
- [ ] True skill record calculated: `baseline + total_skill_impact`
- [ ] Explanation formula: "X-Y = baseline + skill + luck"

### The One Thing

#### Identification
- [ ] Skill factors sorted by impact (most negative first)
- [ ] Worst skill factor = The One Thing
- [ ] Impact value extracted
- [ ] NOT based on luck (can't fix luck!)

#### ROI Analysis
- [ ] Potential improvement = abs(min(0, factor_impact))
- [ ] Use potential_gains from lineups if available
- [ ] Effort scores assigned: Draft=8, Lineups=4, Waivers=7 (1-10 scale)
- [ ] ROI = `potential_improvement / effort`
- [ ] Sorted by ROI (highest = best bang for buck)
- [ ] Best ROI factor identified

### Improvement Checklist

#### Draft Improvements
- [ ] If draft grade D or F: add high priority item
- [ ] Expected impact: +2 wins
- [ ] Action: "Study player values and avoid reaching on stars"

#### Lineup Improvements
- [ ] If lineup grade D or F: add high priority item
- [ ] Expected impact: +N wins (from optimal_wins - actual_wins)
- [ ] Action includes bench points left

#### Waiver Improvements
- [ ] If waiver efficiency < 40%: add medium priority item
- [ ] Expected impact: +1-2 wins
- [ ] Action: "Target high-upside free agents earlier"

#### Activity Improvements
- [ ] If archetype is 'Believer' (low activity): add low priority
- [ ] Action: increase waiver activity
- [ ] If archetype is 'Tinkerer' (high activity, low efficiency): add low priority
- [ ] Action: reduce churning

#### Inflection Point Improvements
- [ ] If preventable_losses > 0: add high priority
- [ ] Expected impact: +N wins (from preventable losses)
- [ ] Action: avoid specific lineup mistakes

### 2026 Projections (WITH LUCK REGRESSION)

#### True Skill Baseline
- [ ] True skill wins = baseline + total_skill_impact
- [ ] Luck regresses to 0 (mean)

#### Scenario 1: No Change
- [ ] Projected wins = true_skill_wins (baseline + skill, luck → 0)
- [ ] Record formatted as "X-Y"
- [ ] Note: "If you change nothing (luck regresses to mean)"

#### Scenario 2: Fix One Thing
- [ ] Biggest weakness gain calculated
- [ ] Use preventable_losses if The One Thing is Lineups
- [ ] Projected wins = no_change_wins + biggest_weakness_gain
- [ ] Record formatted
- [ ] Note: "If you fix {factor} (recommended)"

#### Scenario 3: Fix All Weaknesses
- [ ] Total skill improvements summed across all factors
- [ ] Projected wins = no_change_wins + total_improvements
- [ ] Record formatted
- [ ] Note: "If you fix all skill weaknesses (optimistic)"

#### Validation
- [ ] All scenarios capped at total_games (max wins)
- [ ] All scenarios ≥ 0 (min wins)
- [ ] Records rounded to integers
- [ ] Improvement = projected_wins - actual_wins
- [ ] Wins needed to maintain calculated if luck > 0

#### Reality Check
- [ ] If total_luck_impact > 1: show warning
- [ ] Message: "You were +X lucky wins. That won't repeat. Need +Y skill improvement."
- [ ] Otherwise: "Your record reflects your skill level."

### Playoff Benchmark
- [ ] All teams' efficiency and wins collected
- [ ] Top 6 teams by wins identified (playoff teams)
- [ ] Playoff average efficiency calculated
- [ ] Manager's efficiency compared
- [ ] Efficiency gap calculated: `playoff_avg - manager_eff`
- [ ] Note explains what this means

### Memorable Weeks

#### Killer Weeks
- [ ] Manager scored #1 in league that week
- [ ] Second place score tracked
- [ ] Margin calculated
- [ ] All killer weeks collected

#### Buzzsaw Weeks
- [ ] Manager scored top 3 but still lost
- [ ] Opponent rank identified
- [ ] Opponent name retrieved
- [ ] Margin calculated (opponent - manager)
- [ ] Only true buzzsaws counted (not just any loss)

### Edge Cases
- [ ] No Card 2/3 data: use defaults for skill factors
- [ ] No trades: waiver impact = 0
- [ ] No lineup data: lineup impact = 0
- [ ] Zero games played: baseline = 0, percentages protected
- [ ] Negative luck: formulas still work
- [ ] All wins or all losses: attribution still calculated
- [ ] Missing opponent IDs: skip opponent mistake analysis for that week
- [ ] Circular dependency avoided: uses Card 2 for draft grade, not Card 1
- [ ] Infinite recursion avoided: doesn't call calculate_card_4 for all teams

### Data Precision
- [ ] All win impacts rounded to 1 decimal
- [ ] Luck factors rounded to nearest 0.5
- [ ] Percentages rounded to 1 decimal
- [ ] Point totals rounded to 1 decimal
- [ ] Projected wins rounded to integers

### Validation
- [ ] Actual record has wins, losses, record fields
- [ ] All-play record calculated correctly
- [ ] Skill factors have impact, grade, category, potential_gains
- [ ] Luck factors have impact, category, note, details, narrative
- [ ] The One Thing is from skill factors, not luck
- [ ] ROI factors have roi, effort_score, potential_improvement
- [ ] Improvement checklist items have category, priority, action, expected_impact
- [ ] All 3 projection scenarios present
- [ ] Playoff benchmark fields populated
- [ ] Memorable weeks have correct structure

---

## Cross-Cutting Concerns

### Data Integrity

#### Player ID Consistency
- [ ] All player IDs converted to strings for comparison: `str(player_id)`
- [ ] Player ID lookups use consistent format
- [ ] Player names fallback to "Player {id}" if missing

#### Week Key Format
- [ ] Week keys formatted as `f'week_{week}'`
- [ ] Week numbers are integers (1-18)
- [ ] Regular season weeks calculated correctly: `range(1, playoff_start)`

#### Point Calculations
- [ ] `actual_points` field used for scoring
- [ ] Float conversion: `float(player.get('actual_points', 0))`
- [ ] Sum operations handle empty lists gracefully
- [ ] Zero point games handled (bye weeks, injuries)

### Calculation Dependencies

#### Card Generation Order
- [ ] Pass 1: Cards 2, 3, 4 generated for all teams
- [ ] Pass 2: Archetypes assigned at league level
- [ ] Pass 3: Card 1 generated with assigned archetypes
- [ ] No circular dependencies (Card 1 doesn't call Cards 2-4, they're passed in)

#### Cross-Card Data Flow
- [ ] Card 1 receives other_cards dict with Cards 2-4 data
- [ ] Card 1 uses Card 2 for draft grade (not Card 1 - would be circular)
- [ ] Card 1 uses Card 3 for efficiency and archetype
- [ ] Card 4 receives other_cards dict but doesn't recursively call itself
- [ ] Card 4 uses Card 2 for draft grade, Card 3 for efficiency

#### Caching
- [ ] Waiver scores cached in `_waiver_scores_cache` (Card 1)
- [ ] No redundant calculations across multiple calls
- [ ] Cache invalidation not needed (single execution per team)

### League Compatibility

#### League Size
- [ ] Works with 8-team leagues
- [ ] Works with 10-team leagues
- [ ] Works with 12-team leagues
- [ ] Works with 14+ team leagues
- [ ] Percentile calculations work with small leagues (n=4 minimum)

#### Scoring Systems
- [ ] Head-to-head leagues fully supported
- [ ] Points-only leagues: some metrics unavailable (noted in warnings)
- [ ] PPR scoring: works
- [ ] Standard scoring: works
- [ ] Half-PPR scoring: works

#### Draft Types
- [ ] Snake drafts: full VOR analysis with positional rankings
- [ ] Auction drafts: ROI analysis with cost tiers
- [ ] Offline drafts: graceful degradation (Card 2 unavailable)
- [ ] Keeper leagues: partial draft data handled

#### Roster Configurations
- [ ] Standard (1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 K, 1 DEF): works
- [ ] 2 QB leagues: detected and supported
- [ ] Superflex (QB/RB/WR/TE): detected, warned
- [ ] IDP leagues (DL, LB, DB): detected, warned (limited support)
- [ ] Variable bench sizes: handled dynamically

### Missing Data Scenarios

#### No Draft Data
- [ ] Card 1: Draft percentile defaults to 50
- [ ] Card 2: Shows error message "No draft data available"
- [ ] Card 2: Draft grade = "N/A"
- [ ] Card 2: Empty steals/busts arrays
- [ ] Other cards proceed normally

#### No Transaction Data
- [ ] Card 2: Waivers section shows 0 adds
- [ ] Card 2: Trades section shows "No trades made"
- [ ] Card 2: Costly drops shows "No drops made"
- [ ] Card 3: Archetype defaults based on available data
- [ ] Card 4: Waiver impact = 0

#### Incomplete Weekly Data
- [ ] Missing weeks skipped in calculations
- [ ] Averages calculated over available weeks only
- [ ] No division by zero (check weeks_played > 0)
- [ ] Extrapolation avoided (don't assume missing = 0)

#### Missing Opponent Data
- [ ] All-play record still calculated (compares to all teams)
- [ ] Schedule luck uses league average if opponent missing
- [ ] Opponent mistakes skipped for weeks without opponent data

### Rounding & Precision

#### Point Totals
- [ ] All point sums rounded to 1 decimal: `round(total, 1)`
- [ ] Displayed with 1 decimal place in output

#### Percentages
- [ ] All percentages calculated as floats first
- [ ] Rounded to 1 decimal: `round(pct, 1)`
- [ ] Range validated: [0, 100]

#### Win Projections
- [ ] Win counts are integers: `int(round(wins))`
- [ ] Never negative: `max(0, wins)`
- [ ] Never exceed total games: `min(total_games, wins)`

#### Impact Values
- [ ] Win impacts rounded to 1 decimal
- [ ] Luck factors rounded to nearest 0.5
- [ ] ROI values rounded to 2-3 decimals

### Error Handling

#### Graceful Degradation
- [ ] Missing data returns default values (not errors)
- [ ] Empty arrays handled in sum/average operations
- [ ] None values handled in comparisons
- [ ] Invalid data types caught and logged

#### Division by Zero Protection
- [ ] Check denominator > 0 before division
- [ ] Use ternary operators: `x / y if y > 0 else 0`
- [ ] Average calculations check len(list) > 0

#### Type Safety
- [ ] Player IDs always converted to strings
- [ ] Week numbers always integers
- [ ] Point values always floats
- [ ] Boolean flags properly typed

### Performance

#### Calculation Efficiency
- [ ] No nested loops over all teams × all weeks × all players (O(n³))
- [ ] Caching used where appropriate
- [ ] Early exits in search loops (use `break`)
- [ ] Efficient data structures (dicts for lookups, not lists)

#### Memory Usage
- [ ] No duplicate data storage
- [ ] Large datasets not copied unnecessarily
- [ ] Generator expressions used where appropriate

### Output Validation

#### Required Fields
- [ ] Every card has `manager_name` field
- [ ] Every card has `card_name` field (except Card 1 uses archetype)
- [ ] Numeric fields are numbers (not strings)
- [ ] Array fields are arrays (not None)

#### Data Completeness
- [ ] No missing required fields
- [ ] No null/undefined in critical paths
- [ ] Empty states handled explicitly (show "N/A" or "No data")

#### Formatting
- [ ] Records formatted as "X-Y" or "X-Y-Z" (with ties)
- [ ] Ranks formatted as "X/Y"
- [ ] Percentiles shown with 1 decimal
- [ ] Point totals shown with 1 decimal

---

## Pre-Launch Validation Tests

### Integration Tests

#### Single Team Test
- [ ] Generate all 4 cards for one team
- [ ] Verify no errors
- [ ] Verify all required fields present
- [ ] Verify calculations match manual verification

#### Full League Test
- [ ] Generate all 4 cards for all teams
- [ ] Verify archetype distribution (max 3 per archetype)
- [ ] Verify percentile distributions look normal
- [ ] Verify all rankings sum correctly

#### Edge Case League Tests
- [ ] 8-team league
- [ ] 14-team league
- [ ] Points-only league (no head-to-head)
- [ ] Auction draft league
- [ ] League with no transactions
- [ ] League with incomplete data (mid-season)

### Data Quality Checks

#### Percentile Sanity
- [ ] All percentiles in [0, 100]
- [ ] League averages near 50th percentile
- [ ] Top team near 100th percentile
- [ ] Bottom team near 0th percentile

#### Attribution Accuracy
- [ ] Skill + luck ≈ actual wins (within ±1 win)
- [ ] True skill record makes sense
- [ ] Luck factors sum correctly

#### Consistency Checks
- [ ] Draft rank in Card 1 matches Card 2
- [ ] Efficiency in Card 1 matches Card 3
- [ ] Waiver data in Card 1 matches Card 2
- [ ] All-play record in Card 4 makes sense vs actual record

### Regression Tests

#### Known Good Data
- [ ] Test league with verified calculations
- [ ] Compare output to expected results
- [ ] All key metrics match (within rounding)

#### Historical Data
- [ ] Prior season data still processes correctly
- [ ] No breaking changes in calculations

### User Acceptance Tests

#### Readability
- [ ] Narratives make grammatical sense
- [ ] Numbers formatted consistently
- [ ] Verdicts match the underlying data
- [ ] No confusing or contradictory messages

#### Actionability
- [ ] Improvement suggestions are specific
- [ ] ROI analysis provides clear guidance
- [ ] Projections are realistic
- [ ] Checklist items are actionable

---

## Launch Readiness Checklist

### Code Quality
- [ ] No TODO comments in production code
- [ ] No debug print statements
- [ ] All functions have docstrings
- [ ] Complex logic has inline comments

### Documentation
- [ ] README.md updated with usage instructions
- [ ] Card structure documented
- [ ] Data requirements documented
- [ ] Known limitations documented

### Testing
- [ ] All integration tests pass
- [ ] All edge cases handled
- [ ] Manual spot checks completed
- [ ] Beta testers have validated output

### Performance
- [ ] Full league generation completes in <30 seconds
- [ ] Memory usage reasonable (<1GB)
- [ ] No infinite loops or recursion errors

### User Experience
- [ ] Progress messages clear during generation
- [ ] Error messages helpful and actionable
- [ ] Output files named clearly
- [ ] JSON structure clean and navigable

### Final Verification
- [ ] Generate cards for 3 different leagues
- [ ] Manually verify 10% of calculations
- [ ] No errors or warnings in production run
- [ ] Output validated by domain expert

---

## Post-Launch Monitoring

### Error Tracking
- [ ] Monitor for uncaught exceptions
- [ ] Track leagues that fail to process
- [ ] Collect edge cases that weren't anticipated

### Data Quality
- [ ] Spot check random teams weekly
- [ ] Verify key metrics (win attribution, efficiency)
- [ ] Check for outliers or anomalies

### User Feedback
- [ ] Collect feedback on accuracy
- [ ] Track confusion points
- [ ] Document feature requests

### Calculation Refinement
- [ ] Validate correlation coefficients (draft, lineup, waiver impacts)
- [ ] Adjust weights if real-world data shows different patterns
- [ ] Improve projections based on actual next-season results

---

## Version History

**v1.0** - Initial production release
- All 4 cards implemented
- League-level archetype assignment
- VOR-based draft analysis
- Win attribution system
- All-play record as true strength measure

---

**END OF CHECKLIST**

This checklist should be used before each production deployment. Any item that cannot be checked should be investigated and resolved before launch.
