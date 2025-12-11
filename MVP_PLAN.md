# Fantasy Reckoning - MVP Launch Plan
**Updated:** December 10, 2024
**Timeline:** 2 weeks (Launch by end of Week 17)
**Goal:** 10 paying leagues at $10 each

---

## 🎯 SCOPE

### What We're Building
- Season recap cards for Yahoo Fantasy Football leagues
- 5 cards per manager with data-driven insights
- Beautiful, shareable PNG images (Instagram Story format)
- Supports both auction AND snake drafts

### What We're NOT Building (Yet)
- ESPN/Sleeper support (Yahoo only for now)
- Automated payment processing (manual Venmo)
- User accounts or dashboards
- Website (just Reddit/Twitter marketing)
- Memes/entertainment layer (clean data cards only)

---

## 💰 BUSINESS MODEL

**Price:** $10 per league (one-time payment)

**Payment:** Venmo/Cash App
- Customer DMs/comments with interest
- You reply with Venmo handle
- They send $10 with league name/ID
- You manually process their order

**Delivery:** Email with Google Drive link
- Generate cards (automated)
- Upload to Google Drive folder
- Send email with download link
- 24-hour turnaround

**Target:** 10 leagues = $100 revenue (validation, not profit)

---

## 🗓️ 2-WEEK TIMELINE

### Week 1: Fix Bugs & Design Cards

**Day 1-2 (Dec 10-11): Fix Critical Bugs**
- [ ] Implement snake draft analysis (currently returns placeholder)
- [ ] Fix opponent lookup bug in Card 3 (shows wrong opponent)
- [ ] Fix transaction timestamp parsing in Card 4 (always Week 1)
- [ ] Add error handling for division by zero edge cases

**Day 3 (Dec 12): Test on Your League**
- [ ] Pull fresh league data
- [ ] Run calculator for all 14 managers
- [ ] Verify all cards are accurate
- [ ] Test both auction and snake draft detection

**Day 4-6 (Dec 13-15): Design in Figma**
- [ ] Create 5 card templates (1080×1920 Instagram Story size)
- [ ] Use clean gradients (purple/blue Spotify Wrapped style)
- [ ] No memes - focus on data and typography
- [ ] Test with your league's actual data
- [ ] Get feedback from friends

**Day 7 (Dec 16): Build Automation**
- [ ] Share Figma designs with Claude
- [ ] Claude translates to HTML/CSS
- [ ] Build Python screenshot generator
- [ ] Test: JSON → HTML → PNG pipeline
- [ ] Generate all 70 cards for your league (14 managers × 5)

### Week 2: Launch & Process Orders

**Day 8 (Dec 17): Soft Launch Prep**
- [ ] Write Reddit post with sample cards
- [ ] Create list of 30 fantasy Twitter accounts to DM
- [ ] Set up Google Drive folder structure
- [ ] Write email template for delivery
- [ ] Create order tracking spreadsheet

**Day 9-10 (Dec 18-19): Launch**
- [ ] Post to r/fantasyfootball (Tuesday morning)
- [ ] DM 30 Twitter accounts offering free/discounted analysis
- [ ] Respond to comments/DMs
- [ ] Process first 2-3 beta leagues for free (social proof)

**Day 11-14 (Dec 20-23): Process Orders**
- [ ] As Venmo payments come in, add to queue
- [ ] Generate cards (2-3 min per league, automated)
- [ ] Upload to Google Drive
- [ ] Email download links
- [ ] Respond to questions/feedback
- [ ] Track what works/breaks

---

## 🐛 CRITICAL BUGS TO FIX

### Must Fix This Week

**1. Snake Draft Not Implemented**
- **File:** `card_1_draft.py` lines 32-50
- **Issue:** Currently returns placeholder "Snake draft analysis coming soon!"
- **Impact:** 50% of leagues can't use the product
- **Fix:** Implement draft position value analysis for snake drafts

**2. Opponent Lookup Broken**
- **File:** `card_3_inflection.py` lines 42-53
- **Issue:** Takes first other team alphabetically, not actual opponent
- **Impact:** All "biggest mistake" analysis is wrong
- **Fix:** Use `week_data.get('opponent_id')` instead of iteration

**3. Transaction Timestamps Wrong**
- **File:** `card_4_ecosystem.py` line 38
- **Issue:** All transactions assigned to Week 1
- **Impact:** "Drops that hurt" calculations completely wrong
- **Fix:** Parse actual timestamp from transaction data

### Should Fix (But Can Document as Known Issues)

**4. Optimal Lineup Ignores Positions**
- Creates illegal lineups (QB in RB slot)
- Can document: "Position constraints coming soon"

**5. Missing Player Names**
- Shows "Player 12345" for some players
- Can document: "Some player names may show IDs"

**6. Playoff Weeks Included**
- Corrupts regular season records
- Can filter to weeks 1-14 for now

---

## 🎨 DESIGN APPROACH

### Figma → HTML/CSS Pipeline

**Your Work:**
1. Design 5 beautiful cards in Figma
   - Card 1: Draft Grade (big letter grade, steals/busts)
   - Card 2: Identity (timeline comparison, efficiency %)
   - Card 3: Inflection Points (biggest mistake highlight)
   - Card 4: Ecosystem (waiver stats, drops analysis)
   - Card 5: Accounting (win attribution breakdown)

2. Use Spotify Wrapped inspiration:
   - Bold gradients (purple, blue, pink)
   - Big typography (let numbers be the hero)
   - Simple shapes and dividers
   - Clean white text on dark background
   - No photos, no memes (yet)

**Claude's Work:**
1. Translate Figma designs to HTML/CSS
2. Build Python script to:
   - Read JSON data
   - Insert into HTML templates
   - Screenshot as PNG (1080×1920)
   - Save organized by manager

**Result:**
- Beautiful cards that match your Figma design
- Fully automated generation (2-3 min per league)
- No manual copy-paste work

---

## 🛠️ TECHNICAL STACK

**Data Collection (Working):**
- `data_puller.py` - Yahoo API integration ✓
- `league_XXX.json` - Raw league data ✓

**Analysis (Mostly Working):**
- `fantasy_wrapped_calculator.py` - Main engine ✓
- `card_1_draft.py` - Draft analysis (needs snake draft)
- `card_2_identity.py` - Efficiency/timeline ✓
- `card_3_inflection.py` - Key moments (needs opponent fix)
- `card_4_ecosystem.py` - Waivers/drops (needs timestamp fix)
- `card_5_accounting.py` - Win attribution ✓

**Export (Working):**
- `export_for_figma.py` - Text file export ✓

**Generation (To Build):**
- HTML/CSS card templates (Claude creates)
- Python screenshot generator using Playwright
- Batch processing script for all managers

**Delivery (Simple):**
- Google Drive for file hosting
- Gmail for email delivery
- Google Sheets for order tracking
- Venmo for payments

---

## 📣 MARKETING STRATEGY

### Target: 10 Leagues

**Channel 1: Reddit (Primary)**

Post to r/fantasyfootball (2M+ members):

**Title:** "I analyzed my fantasy league's entire season and found out why we all lost"

**Strategy:**
- Value-first (share insights, not just selling)
- Humble tone (testing a tool, not pitching a product)
- Include screenshots from your league
- Offer: "First 10 leagues at $10 (normally $20)"
- Call to action: "DM me your Yahoo league ID"

**Timing:** Tuesday morning, Week 16 (playoffs = high engagement)

**Channel 2: Twitter DMs (Secondary)**

Target 30 accounts:
- Fantasy football podcasters (5K-50K followers)
- Twitter analysts who share lineup advice
- Fantasy content creators

**DM Template:**
```
Hey [Name]! Love your fantasy content.

I built a tool that analyzes entire fantasy seasons - draft ROI,
lineup efficiency, biggest mistakes, etc.

Would you want a free analysis of your league? Could make for
interesting content.

Here's what it looks like: [sample card image]

No strings attached - just testing before wider launch.
```

**Expected:** 2-3 influencers take you up on it, share their results

**Channel 3: Word of Mouth**

- Your league mates share their cards
- Group chat FOMO (everyone wants to see their stats)
- Natural viral spread (12-14 people per league see cards)

---

## 📦 DELIVERY PROCESS

### Order Flow

1. **Customer reaches out** (Reddit comment or Twitter DM)

2. **You respond:**
   ```
   Awesome! It's $10 via Venmo @yourhandle

   After you send it, reply with:
   - Your Yahoo league ID (found in URL)
   - Your league name
   - Your email for delivery

   Cards delivered within 24 hours!
   ```

3. **Customer sends Venmo** with note: "League: [Name]"

4. **You add to tracking sheet:**
   | Order Date | Customer | League ID | Email | Status | Delivered |
   |------------|----------|-----------|-------|--------|-----------|
   | Dec 18     | John     | 908221    | john@ | Paid   | Dec 19    |

5. **Generate cards** (automated):
   ```bash
   python generate_cards.py --league_id 908221
   # Creates: league_908221_cards/ folder with 70 PNGs
   ```

6. **Upload to Google Drive:**
   - Create folder: "League_908221_LOGE"
   - Upload all cards
   - Get shareable link (anyone with link can view)

7. **Send email:**
   ```
   Subject: Your Fantasy Reckoning is Ready!

   Hey [Name],

   Your LOGE league's season recap cards are ready!

   Download here: [Google Drive link]
   (Link expires in 30 days)

   Inside you'll find 5 cards for each of your 14 managers.
   Share them in your group chat!

   Questions? Just reply to this email.

   - Max
   ```

8. **Mark as complete** in tracking sheet

**Time per league:** 5-10 minutes once automated

---

## 📊 SUCCESS METRICS

### Week 17 Goals

**Minimum Success:**
- 5 paying leagues ($50)
- All cards generated correctly
- No major bugs discovered
- 2-3 social media posts from customers

**Target Success:**
- 10 paying leagues ($100)
- 1-2 influencer shares
- 5+ Reddit comments saying "this is cool"
- Clear feedback on what to improve

**Stretch Success:**
- 15+ leagues ($150+)
- Influencer with 10K+ followers shares
- Reddit post gets 100+ upvotes
- People asking "when is ESPN support?"

### What This Validates

**If you hit 10 leagues:**
- ✓ People will pay for this
- ✓ The insights are valuable
- ✓ Cards are shareable
- ✓ Yahoo Fantasy market exists

**Then you can decide:**
- Scale it up (fix more bugs, add ESPN, charge $20-30)
- Keep it small (side hustle, 50-100 leagues/year)
- Open source it (build in public)

---

## 🚫 WHAT WE'RE NOT DOING

### Out of Scope for MVP

**Technology:**
- ❌ Payment processors (Stripe, Lemon Squeezy) - use Venmo
- ❌ Webhooks and automation - manual processing is fine
- ❌ Database - use Google Sheets
- ❌ User accounts - one-time generation
- ❌ Website - just Reddit/Twitter

**Features:**
- ❌ ESPN/Sleeper support - Yahoo only
- ❌ Memes/custom images - clean data cards
- ❌ Mid-season analysis - end of season only
- ❌ Print-ready files - digital only
- ❌ Custom branding - standard template

**Business:**
- ❌ Tax compliance - under $600, not an issue
- ❌ LLC/business entity - sole proprietor is fine
- ❌ Refund policy - just refund if issues
- ❌ Terms of service - keep it simple

### Why We're Punting

**For 10 leagues at $10 each:**
- Total revenue: $100
- Not worth complex infrastructure
- Focus on product validation
- Can scale later if it works

**Keep it simple, ship fast, learn quickly.**

---

## 🎯 YOUR NEXT STEPS

### Today (Dec 10)

**1. Find a snake draft league for testing** (30 min)
- Ask friends if they have one
- Or find a public league example
- Need to test snake draft implementation

**2. Fix snake draft bug** (2-4 hours)
- Implement draft pick value analysis
- Test with both auction and snake leagues
- Verify grades make sense

### Tomorrow (Dec 11)

**3. Fix opponent lookup bug** (1-2 hours)
- Use `opponent_id` from weekly data
- Test all matchup analysis is correct

**4. Fix transaction timestamps** (1-2 hours)
- Parse actual week from timestamp
- Verify Card 4 calculations correct

### Thursday-Saturday (Dec 12-14)

**5. Test on your league** (1 hour)
- Fresh data pull
- Generate all 14 managers
- Verify everything accurate

**6. Design cards in Figma** (4-6 hours)
- 5 templates (1080×1920)
- Spotify Wrapped aesthetic
- Test with your data

### Sunday (Dec 15)

**7. Share Figma designs** (1 hour)
- Show Claude your designs
- Get HTML/CSS templates
- Test screenshot generation

### Week 2 (Dec 16-23)

**8. Launch and process orders**
- Post on Reddit
- DM Twitter accounts
- Generate cards as orders come in
- Aim for 10 leagues

---

## 💡 KEY DECISIONS MADE

**Pricing:** $10 per league
- Accessible price point
- Easy impulse purchase
- Low barrier for testing

**Payment:** Venmo (manual)
- No processing fees
- Simple for small volume
- Can upgrade later

**Design:** Figma → HTML/CSS
- Visual design tool (easy)
- Automated generation (scalable)
- Best of both worlds

**Platform:** Yahoo only
- Most complex (auction + snake)
- If Yahoo works, others will be easier
- Focus on doing one thing well

**Marketing:** Organic only
- Reddit post + Twitter DMs
- No paid ads
- Word of mouth

**Timeline:** 2 weeks
- Week 1: Fix + design
- Week 2: Launch + deliver
- Fast validation

---

## 🎉 WHAT SUCCESS LOOKS LIKE

**End of Week 17 (Dec 24):**

You have:
- 10 leagues processed ✓
- $100 in revenue ✓
- 140 happy managers with cards ✓
- Testimonials and feedback ✓
- Clear sense of product-market fit ✓

You learned:
- Do people actually want this? (validation)
- What breaks? (bugs to fix)
- What do they love? (features to enhance)
- Is this worth scaling? (business decision)

You can decide:
- Keep it as side project (manual, 50 leagues/year)
- Scale it up (automate, add platforms, charge more)
- Open source it (community project)
- Sunset it (learned something, move on)

**No pressure, just validation.**

---

## 📞 SUPPORT

For bugs/questions during development:
- Ask Claude to fix specific issues
- Share error messages for debugging
- Test frequently on your league data

For customer support during launch:
- Reply to all DMs/emails within 24 hours
- If cards are wrong, regenerate for free
- If customer unhappy, refund immediately
- Collect feedback for V2

---

**Last Updated:** December 10, 2024
**Status:** Ready to start Week 1 development
**Next Task:** Fix snake draft implementation
