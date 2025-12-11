# League Validation Guide

## How to Use validate_league.py

### Step 1: Get League Data

When a customer inquires, ask them to run the data puller:

```bash
python data_puller.py
# Follow prompts to authenticate and select league
```

This creates: `league_XXXXXX_2025.json`

### Step 2: Run Validation

```bash
python validate_league.py league_XXXXXX_2025.json
```

**Takes 1-2 seconds**, shows:
- ✅ Fully supported / ⚠️ Partial / ❌ Not supported
- Which cards are available (1-5)
- Specific warnings/errors
- Purchase recommendation

---

## Example Outputs

### ✅ Perfect League (90% of cases)
```
✅ FULLY SUPPORTED
   All 5 cards will generate perfectly!

📋 Card Availability:
   ✓ Card 1: The Draft
   ✓ Card 2: The Identity
   ✓ Card 3: Inflection Points
   ✓ Card 4: The Ecosystem
   ✓ Card 5: The Accounting

✅ READY FOR PURCHASE
   Next step: Send $10 via Venmo with league ID XXXXX
```

**Your response to customer:**
> "✅ Your league is fully supported! All 5 cards will work perfectly.
> Send $10 to @venmo-handle with your league ID, cards delivered in 24hrs."

---

### ⚠️ Offline Draft (5% of cases)
```
⚠️  PARTIALLY SUPPORTED
   Most cards will work with minor limitations

📋 Card Availability:
   ✗ Card 1: The Draft
   ✓ Card 2: The Identity
   ✓ Card 3: Inflection Points
   ✓ Card 4: The Ecosystem
   ✓ Card 5: The Accounting

❌ Errors:
   ❌ No draft data found (offline draft or keeper league)
   → Card 1 (Draft Analysis) will be unavailable
```

**Your response to customer:**
> "⚠️ Your league has no draft data (offline draft?), so Card 1 won't be available.
> You'll get Cards 2-5 (4 cards total) for $10. Still interested?"

---

### ⚠️ Superflex League (3% of cases)
```
⚠️  PARTIALLY SUPPORTED
   Most cards will work with minor limitations

⚠️  Warnings:
   ⚠️  Superflex/2QB detected - QB values may be approximate

✅ ACCEPTABLE WITH LIMITATIONS
   5/5 cards available - some features limited by data.
   Customer should review warnings before purchasing.
```

**Your response to customer:**
> "⚠️ Your league is superflex - all 5 cards will generate, but QB draft values
> may be slightly off (not fully optimized for superflex yet). $10 if you're interested."

---

### ❌ Unsupported Format (2% of cases)
```
❌ NOT SUPPORTED
   Too many compatibility issues - not recommended

❌ Errors:
   ❌ Invalid team count: 6
   ❌ No weekly roster data found
   ❌ No draft data found
```

**Your response to customer:**
> "❌ Unfortunately your league format isn't supported yet (missing key data).
> I'm adding more format support soon - I'll reach out when it's ready!"

---

## Customer Flow

### Option A: Customer Has Technical Skills
1. Send them: "Run `python data_puller.py` and share the league JSON file"
2. You run: `python validate_league.py league_XXXXX.json`
3. Share results
4. If ✅, collect payment
5. Generate cards

### Option B: Customer Doesn't Have Python (Most Common)
1. Ask: "What's your Yahoo league ID and season year?"
2. You run: `python data_puller.py` with their credentials (if they authorize)
3. You run: `python validate_league.py`
4. Share results
5. If ✅, collect payment
6. Generate cards

---

## Quick Decision Tree

**Validation shows:**
- **✅ FULLY SUPPORTED** → Accept $10, deliver all 5 cards
- **⚠️ PARTIAL (4-5 cards)** → Explain limitations, accept $10 if they agree
- **⚠️ LIMITED (2-3 cards)** → Offer $5 discount, or decline
- **❌ NOT SUPPORTED** → Politely decline, offer to notify when supported

---

## Time Investment

- Run validation: **1-2 seconds**
- Explain to customer: **1-2 minutes**
- Total pre-sale time: **5 minutes max**

Saves 30-60 minutes of generation + potential refund headache!

---

## Testing Different Formats

To test validation on different league types:

```bash
# Standard league (your league)
python validate_league.py league_908221_2025.json

# If you get test data from friends:
python validate_league.py league_SNAKE_12TEAM.json
python validate_league.py league_SUPERFLEX_10TEAM.json
python validate_league.py league_IDP_14TEAM.json
```

---

## Error Handling

**If validation crashes:**
```bash
python validate_league.py league_XXXXX.json --verbose
```

Shows detailed error output for debugging.

**Common issues:**
- Missing file → Tell customer to re-run data_puller.py
- Corrupt JSON → Have customer pull data again
- Old season → Works fine, just warns about old data

---

## Integration with Order Tracking

**Google Sheets columns:**
| Order Date | Customer | League ID | Status | Validation | Payment | Delivered |
|------------|----------|-----------|--------|------------|---------|-----------|
| Dec 18     | John     | 908221    | ✅ Full | Done       | $10     | Dec 19    |
| Dec 18     | Sarah    | 445123    | ⚠️ Partial | No draft   | $10     | Dec 19    |
| Dec 18     | Mike     | 332145    | ❌ Unsupported | Declined   | -       | -         |

**Status values:**
- ✅ Full → All 5 cards
- ⚠️ Partial → 4 cards (no draft)
- ⚠️ Limited → 2-3 cards
- ❌ Declined → Not compatible

---

## Reddit/Twitter Template Response

**When someone asks "Does my league work?"**

> Hey! To check compatibility, I need your league data. Two options:
>
> **Option 1 (Recommended):** DM me your Yahoo league ID and I'll validate it (takes 2 min)
>
> **Option 2 (DIY):** Clone the repo, run `python data_puller.py` and `python validate_league.py`
>
> Most standard leagues (auction/snake, 8-14 teams) work perfectly!
> Superflex/IDP have partial support. I'll let you know before you pay.

---

## Success Metrics

Track validation results to understand your market:

- **% Fully supported** → Should be 85-90%
- **% Partial** → Should be 5-10%
- **% Declined** → Should be <5%

If >15% are partial/declined, consider hardening priorities for Week 2.
