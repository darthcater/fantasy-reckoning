# Fantasy Wrapped - Data Availability Report
**League:** LOGE (908221)
**Season:** 2025
**API:** Yahoo Fantasy Sports API v2
**Generated:** 2025-12-08

---

## ✅ CONFIRMED AVAILABLE DATA

### **1. Weekly Scores & Matchups**
- ✅ Actual points scored (by team, by week)
- ✅ Projected points (by team, by week)
- ✅ Opponent scores
- ✅ Win/Loss results
- ✅ League average scores
- **Status:** FULLY AVAILABLE

### **2. Roster Data**
- ✅ Weekly roster composition (starters + bench)
- ✅ Player positions (selected_position field)
- ✅ Eligible positions for each player
- ✅ **Injury status (Q/D/O/IR) in roster data**
- **Status:** FULLY AVAILABLE

### **3. Player Statistics**
- ✅ Individual player points by week
- ✅ Player stats breakdown (Pass Yds, Rush Yds, TD, etc.)
- ✅ Can calculate bench points per player
- **Status:** FULLY AVAILABLE (requires separate API call per player)

### **4. Transaction History**
- ✅ All adds, drops, and trades
- ✅ **FAAB bid amounts** (for waiver claims)
- ✅ **Full timestamps** (date + time, not just date)
- ✅ Player names and team destinations
- ✅ Source type (waivers vs free agents)
- **Count:** 293 transactions found in your league
- **Status:** FULLY AVAILABLE

### **5. Draft Data**
- ✅ Complete draft order
- ✅ Player names and positions
- ✅ Team that drafted each player
- **Status:** FULLY AVAILABLE

### **6. Standings & Records**
- ✅ Win/Loss records
- ✅ Points for / Points against
- ✅ Final standings
- ✅ Playoff clinch status
- **Status:** FULLY AVAILABLE

---

## ⚠️ DATA THAT NEEDS WORKAROUNDS

### **Bench Points (Individual Players)**
- **Available:** Yes, but requires extra API calls
- **Workaround:** For each week, for each team:
  1. Get roster (already doing this)
  2. Make ONE API call with all player IDs to get stats
  3. Filter to bench players only
- **Performance:** ~14 teams × 14 weeks × 1 call = 196 API calls
- **With rate limiting:** ~2 minutes total
- **Status:** DOABLE

### **Lineup Change Timestamps**
- **Available:** Only via transaction history
- **Limitation:** Transactions track adds/drops with timestamps, but NOT in-roster moves (e.g., moving a player from bench to starting lineup)
- **Workaround:**
  - We CAN track when players were added (with timestamp)
  - We CANNOT track when existing players were moved in/out of starting lineup
- **Impact on Cards:**
  - **Card 3 (Tinkerer):** Can only measure transaction volume, not lineup tinkering
  - **Fallback:** Track "adds within 24hrs of game time" as proxy for panic moves
- **Status:** PARTIAL

---

## ❌ DATA NOT AVAILABLE

### **Failed Waiver Bids (Bids You Lost)**
- **Not Available:** Only successful transactions are in API
- **Cannot Get:**
  - FAAB bids you placed but lost
  - How much the winning bid was (if you didn't win)
  - Who else bid on a player
- **Impact on Cards:**
  - **Card 5 (Butterfly Effect):** Cannot show "the player you almost got"
  - **Fallback:** Focus on worst drop or worst bench decision instead
- **Status:** NOT AVAILABLE

---

## 📊 CARD-BY-CARD FEASIBILITY

### **CARD 1: The Identity (Manager Archetype)**
**Status:** ✅ **FULLY FEASIBLE**
- ✅ Total transactions (293 found)
- ✅ Transaction timestamps (full date + time)
- ⚠️ Lineup changes: Only via add/drop transactions
- ✅ Win/loss record
- ✅ League averages
- **Adjustment:** Focus on "Transaction Tempo" instead of pure lineup tinkering

---

### **CARD 2: The Parallel Universe**
**Status:** ✅ **FULLY FEASIBLE**
- ✅ Weekly actual scores
- ✅ Weekly bench scores (via player stats API)
- ✅ Weekly roster composition
- ✅ **Injury designations available!** (Q/D/O/IR)
- ✅ Can calculate optimal lineup with injury filtering
- **No adjustments needed!**

---

### **CARD 3: The Tinkerer's Report**
**Status:** ⚠️ **PARTIALLY FEASIBLE**
- ✅ Transaction timestamps available
- ❌ Cannot track in-roster lineup changes (bench ↔ starter swaps)
- **Adjustment:**
  - Track "adds within 24 hours of Sunday 1pm EST"
  - Call it "Sunday Panic Adds" instead of "lineup tinkering"
  - Compare win rate on weeks with Sunday adds vs. no Sunday adds
  - Still captures the essence of last-minute panic

---

### **CARD 4: The Luck Tax**
**Status:** ✅ **FULLY FEASIBLE**
- ✅ Weekly scores
- ✅ Opponent scores
- ✅ League averages
- ✅ Final standings
- ✅ Strength of schedule calculations possible
- **No adjustments needed!**

---

### **CARD 5: The Butterfly Effect**
**Status:** ❌ **NOT FEASIBLE (as designed)**
- ❌ Cannot see failed waiver bids
- ❌ Cannot see other managers' bid amounts
- ❌ Cannot identify "the one that got away"
- **Alternative Butterfly Effects:**
  1. **Worst Drop:** Player you dropped who went on to score the most ROS points
  2. **Worst Bench Decision:** Week where your bench outscored your starters by the most
  3. **Injury Cascade:** Your highest-drafted player who got injured, showing alternate reality without injury
  4. **Trade Regret:** If any trades exist in transaction history
- **Recommendation:** Pivot to "The One You Let Go" (worst drop analysis)

---

### **CARD 6: The Heat Map (Season Journey)**
**Status:** ✅ **FULLY FEASIBLE**
- ✅ Weekly scores (weeks 1-14)
- ✅ Win/loss record by week
- ✅ Opponent scores
- ✅ League average scores
- ✅ Projected scores
- ✅ Can calculate volatility metrics
- **No adjustments needed!**

---

## 🎯 FINAL RECOMMENDATIONS

### **Cards Ready to Build (No Changes Needed):**
1. ✅ Card 1: The Identity
2. ✅ Card 2: The Parallel Universe (injury data available!)
3. ✅ Card 4: The Luck Tax
4. ✅ Card 6: The Heat Map

### **Cards Needing Adjustments:**
3. ⚠️ **Card 3:** Change from "Tinkerer" to "Sunday Panic Adds"
   - Focus on adds/drops within 24hrs of game time
   - Still shows impulsive decision-making

5. ❌ **Card 5:** Replace with "The One You Let Go"
   - Show worst drop (most ROS points scored after you dropped them)
   - Show worst bench decision (biggest starter/bench point differential)
   - Show injury butterfly (best player's injury impact)

---

## 🚀 NEXT STEPS

### **Immediate Actions:**
1. Update `data_puller.py` to:
   - ✅ Fix transactions() method to get all 293 transactions
   - ✅ Add player stats API calls for bench points
   - ✅ Include injury status in roster data
   - ✅ Calculate optimal lineups with injury filtering

2. Validate data quality:
   - Spot-check bench points calculations
   - Verify injury status accuracy
   - Confirm transaction timestamps are correct

3. Build metrics calculator:
   - Calculate all metrics from available data
   - Generate JSON output for each card

### **Data Collection Estimates:**
- **Current:** League metadata + standings (DONE)
- **Add:** Player stats for bench points (~2 minutes)
- **Add:** Transaction parsing (~30 seconds)
- **Total runtime:** ~5-7 minutes for complete data pull

---

## ✅ GO/NO-GO: **🟢 GO FOR LAUNCH**

**All critical data is available.** Minor adjustments needed for Cards 3 & 5, but the core insights remain intact and compelling.
