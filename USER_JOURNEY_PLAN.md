# Fantasy Reckoning User Journey & Onboarding Plan

**Status:** DRAFT - Needs finalization before launch
**Last Updated:** Dec 12, 2025

---

## Critical Questions to Answer

### 1. WHO CAN SIGN UP?
**Options:**
- **A) Commissioner only** - Simplest, but limits reach
- **B) Any league member** - Max reach, but need league validation
- **C) Hybrid** - Prefer commissioner, but allow any member with verification

**Recommendation:** **Option C - Hybrid approach**
- Primary CTA: "Commissioners: Get Reckoning for Your League"
- Secondary: "League Member? We can still help - just need a few extra steps"
- Reduces friction while maintaining data quality

---

### 2. YAHOO PERMISSIONS & AUTHORIZATION

**What we need:**
- Yahoo league ID (public)
- Season year (public)
- League data access (requires Yahoo OAuth if private league)

**Two paths:**

**Path A: Public League (70% of leagues)**
- User provides: League ID + Year
- We fetch data directly (no auth needed)
- ✅ Instant, frictionless

**Path B: Private League (30% of leagues)**
- User must authorize our app via Yahoo OAuth
- They authenticate, grant read access
- We pull data once, then revoke
- ⚠️ Extra step, but secure

**Implementation:**
- Website should detect if league is public/private
- Guide user down appropriate path
- "Most leagues are public - we'll let you know if yours needs authorization"

---

### 3. ENTRY POINTS & CHANNELS

**Where users discover us:**

| Entry Point | User Action | Our Response |
|-------------|-------------|--------------|
| **Website** | Fill email form | → Email: "Thanks! Send us your league ID" |
| **Twitter/X DM** | "I want Reckoning!" | → "Great! Reply with your Yahoo league ID" |
| **Reddit comment** | Tag/mention us | → DM them: "Link to onboarding form" |
| **Email waitlist** | Submit email | → "We're live! Here's your league ID form" |
| **Friend referral** | Hears about it | → Any of the above paths |

**Critical:** ALL paths should funnel to same place: **League submission form**

---

### 4. SIGN-UP PROCESS (Step-by-Step)

### **STEP 1: DISCOVERY**
User finds us via website/Twitter/Reddit/friend

### **STEP 2: INTEREST**
User clicks "FACE YOUR RECKONING" CTA

### **STEP 3: INFORMATION CAPTURE**
Simple form:
```
📋 Get Your League's Reckoning

Your Email: _____________
Yahoo League ID: _________ (Where to find this?)
Season Year: 2024 ▼
League Name (optional): _____________

[VALIDATE MY LEAGUE]
```

### **STEP 4: INSTANT VALIDATION** ⚡
- We run `validate_league.py` in real-time
- Shows result in <3 seconds:
  - ✅ "Your league is fully supported! All 6 cards available."
  - ⚠️ "Your league is partially supported (5/6 cards - no draft data)"
  - ❌ "Sorry, your league format isn't supported yet. We'll notify you when it is."

### **STEP 5: PRICING & COMMITMENT**
If ✅ or ⚠️:
```
✅ YOUR LEAGUE WORKS!

What you get:
- 6 personalized cards for EVERY manager in your league
- Delivered within 24 hours
- Shareable screenshots for maximum trash talk

Price: FREE (optional $5 tip appreciated)

[CONFIRM - GENERATE MY RECKONING] ←
```

### **STEP 6: GENERATION** ⚙️
- User clicks confirm
- We generate all cards for all managers
- Takes 2-5 minutes
- Progress shown: "Generating cards for 12 managers... 5/12 complete"

### **STEP 7: DELIVERY** 📧
Email sent to user with:
```
Subject: ⚔️ Your Fantasy Reckoning Has Arrived

Your league's Reckoning is complete!

🔗 View all cards: [fantasyreckoning.com/league/908221]

Each manager gets:
- Card I: The Draft Tribunal
- Card II: The Three Fates
- Card III: The Fatal Error
- Card IV: The Forsaken
- Card V: The Final Ledger
- Card VI: The Six Faces

📤 Share with your league:
[Copy league link] [Share on Twitter] [Download all cards]

---

💡 TIP: Post these in your league chat for maximum chaos.

Enjoying your Reckoning? [Buy me a coffee ☕]
```

### **STEP 8: VIEWING & SHARING** 📱

**Individual card pages:**
- URL: `fantasyreckoning.com/league/908221/manager/jake`
- Shows all 6 cards in beautiful dark theme
- Mobile-optimized
- Each card has "Share" button:
  - 📸 Screenshot (auto-downloads perfect image)
  - 🐦 Share to Twitter
  - 📋 Copy link

**League overview page:**
- URL: `fantasyreckoning.com/league/908221`
- Shows all managers
- Leaderboard view
- "Share entire league" option

---

## 5. DATA TRACKING & MANAGEMENT

**What we need to track:**

### **Google Sheet: "Reckoning Orders 2025"**

| Submitted | Email | League ID | Status | Validation | Managers | Delivered | Notes |
|-----------|-------|-----------|--------|------------|----------|-----------|-------|
| Dec 15 2pm | john@email.com | 908221 | ✅ Complete | Full (6/6) | 12 | Dec 15 3pm | Tipped $5 |
| Dec 15 3pm | sarah@email.com | 445123 | ⚠️ Partial | 5/6 cards | 10 | Dec 15 4pm | No draft data |
| Dec 15 4pm | mike@email.com | 332145 | ❌ Declined | Failed | - | - | Superflex unsupported |

**Columns explained:**
- **Submitted:** When they submitted form
- **Email:** Contact email
- **League ID:** Yahoo league ID
- **Status:** ✅ Complete / ⚠️ Partial / ❌ Declined / ⏳ Processing
- **Validation:** What cards are available
- **Managers:** How many managers in league
- **Delivered:** When we sent email
- **Notes:** Tips, issues, special requests

**Automation:**
- Form submission → Auto-add row to sheet
- Validation result → Auto-update Status column
- Generation complete → Auto-update Delivered column

---

## 6. VALIDATION PROCESS

**How we verify it works:**

```
User submits League ID
         ↓
Run validate_league.py league_XXXXX.json
         ↓
Result in <3 seconds:
         ↓
    ✅ FULL / ⚠️ PARTIAL / ❌ UNSUPPORTED
         ↓
Show user what cards they'll get
         ↓
User confirms or declines
```

**Validation checks:**
- Draft data exists? (affects Card 1)
- Weekly roster data exists? (affects Cards 2-5)
- Transaction data exists? (affects Card 4)
- Scoring format supported? (all formats work)
- Team count valid? (8-14 teams recommended)

---

## 7. TIMELINE EXPECTATIONS

**Set clear expectations:**

| Stage | Time | User Sees |
|-------|------|-----------|
| Submit form | Instant | "Validating your league..." |
| Validation | 2-3 sec | "✅ Your league works!" |
| Confirm | Instant | "Generating your Reckoning..." |
| Generation | 2-5 min | Progress bar: "5/12 managers complete" |
| Delivery | Instant | "✅ Sent to your email!" |
| **TOTAL** | **~5 minutes** | **From submit to inbox** |

**Messaging:**
- "Most leagues process in under 5 minutes"
- "We'll email you when it's ready (usually 2-5 minutes)"
- "Large leagues (14+ managers) may take up to 10 minutes"

---

## 8. CARD DELIVERY & SHARING

### **Delivery Format:**

**Option A: Web-based (Recommended)**
- Host all cards at fantasyreckoning.com
- Each manager gets unique URL
- Beautiful responsive card viewer
- Built-in share buttons
- SEO benefit (traffic to our site)

**Option B: Email attachments**
- Send 6 image files per manager
- Bloated emails, spam risk
- No analytics
- ❌ NOT RECOMMENDED

**Option C: Hybrid**
- Email with link to web viewer
- Option to download all cards as ZIP
- Best of both worlds

### **Sharing Mechanics:**

**Screenshot button on each card:**
```javascript
[📸 Share This Card]
  ↓
Generates perfect 1080x1920 image
  ↓
Auto-downloads to device
  ↓
User posts to Twitter/Instagram/GroupChat
```

**Tweet template:**
```
My Fantasy Reckoning: [Card Name]

[Auto-generated image]

The tribunal has spoken.

Get your league's Reckoning: fantasyreckoning.com

#FantasyFootball #FantasyReckoning
```

---

## 9. WEBSITE SECTIONS NEEDED

### **A) Hero Section** (existing)
- "Your judgment day has arrived"
- Primary CTA: "FACE YOUR RECKONING"

### **B) How It Works** (NEW - CRITICAL)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ SUBMIT YOUR LEAGUE
   Enter your Yahoo league ID (we'll show you where to find it)

2️⃣ INSTANT VALIDATION
   We verify your league works (takes 3 seconds)

3️⃣ CONFIRM & GENERATE
   We create 6 cards for every manager (free!)

4️⃣ RECEIVE & SHARE
   Get your cards via email in ~5 minutes, share with league

⚡ From submit to delivered: ~5 minutes
🎯 Works with 90%+ of Yahoo fantasy leagues
💰 Completely free (tips appreciated)
```

### **C) FAQ Section** (NEW)
- "Do I need to be the commissioner?"
- "What if my league is private?"
- "How long does it take?"
- "Can I share the cards?"
- "What formats are supported?"

### **D) League ID Helper** (NEW)
```
WHERE TO FIND YOUR LEAGUE ID

1. Go to your Yahoo fantasy league
2. Look at the URL:
   https://football.fantasysports.yahoo.com/f1/12345/...
                                                 ^^^^^
                                            This is your League ID

[Copy this number and paste it in the form above]
```

---

## 10. FRICTION POINTS & SOLUTIONS

### **Friction Point 1: "Where's my league ID?"**
**Solution:**
- Big visual guide with screenshot
- "Click here if you can't find it" → Opens helper modal
- Auto-detect from pasted URL

### **Friction Point 2: "Is my league supported?"**
**Solution:**
- Instant validation (3 seconds)
- Clear ✅/⚠️/❌ messaging
- "90%+ of leagues work - we'll tell you right away"

### **Friction Point 3: "How do I share with my league?"**
**Solution:**
- "Copy league link" button (one click)
- Pre-written message template
- "Post this in your league chat" instructions

### **Friction Point 4: "Payment/signup confusion"**
**Solution:**
- "Completely FREE" in big letters
- "No signup required"
- "Optional tip if you love it"
- Remove all payment friction

### **Friction Point 5: "Private league authorization"**
**Solution:**
- "Your league is private - click here to authorize (one-time, 30 seconds)"
- Clear explanation: "We need read-only access to pull your data"
- "We delete your data after generation"

---

## 11. MULTI-CHANNEL ENTRY STRATEGY

### **Website visitors:**
- Hero CTA → Form → Validation → Delivery

### **Twitter/X users:**
- Tweet about us → Reply with League ID → We generate → DM them link
- Or: "DM us your league ID" → Manual process → Send link

### **Email waitlist:**
- Send blast: "We're live! Submit your league here: [link]"
- Link goes to form

### **Reddit users:**
- Comment: "Check out Fantasy Reckoning: [link]"
- Link goes to form

**All roads lead to: League submission form**

---

## 12. SUCCESS METRICS TO TRACK

- **Conversion rate:** Form views → Submissions
- **Validation success:** % that pass validation
- **Time to delivery:** Avg minutes from submit to email
- **Share rate:** % of users who share cards
- **Viral coefficient:** New users from shares
- **Tip rate:** % who donate

---

## NEXT STEPS

1. **Website Design Agent:** Incorporate "How It Works" section
2. **Build submission form:** Simple, fast, auto-validation
3. **Create card viewer:** Web-based individual card pages
4. **Set up tracking:** Google Sheet + analytics
5. **Write email templates:** Confirmation, delivery, follow-up
6. **Test end-to-end:** Submit test league, verify 5-min delivery

---

## OPEN QUESTIONS FOR USER

1. Do we want to collect any data beyond email + league ID?
2. Should we require email, or allow anonymous submissions?
3. Do we manually approve each league, or auto-generate?
4. What's our capacity? (How many leagues can we process per day?)
5. Do we need a queue system for high volume?

---

**STATUS:** Ready for user review and Website Design agent collaboration
