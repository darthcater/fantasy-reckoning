# Fantasy Reckoning - Product Specification

## Overview
Fantasy Reckoning generates 4 personalized Instagram Story-sized cards for every manager in a fantasy football league, analyzing their entire season.

## Deliverable Format
- **Card Size:** 1080×1920px (Instagram Story 9:16 aspect ratio)
- **File Type:** PNG images
- **Quantity:** 4 cards per manager
- **Card Names:**
  1. The Leader - How you played and stacked up against your rivals
  2. The Ledger - Where your points came from (and where they went)
  3. The Lineup - How you deployed your roster in battle
  4. The Legend - The story of your season, where fate and folly intertwined

## User Flow

### 1. Generation (Commissioner/League Member)
**Input:**
- User visits Fantasy Reckoning website
- Enters Yahoo Fantasy Football league ID
- Clicks "Generate Cards"

**Processing:**
- System pulls league data from Yahoo API
- Generates cards for ALL managers in league (single computation)
- Creates shareable league preview page

**Output:**
- User receives shareable link: `fantasyreckoning.com/league/{league_id}_{season}`

### 2. Distribution (Commissioner → League)
- Commissioner shares link with league via:
  - League group chat
  - Text message
  - Email
  - Social media

### 3. Individual Access (Each Manager)
**Landing Page:**
- Manager clicks link → lands on league preview page
- Sees manager selector: dropdown or grid of all managers
- Clicks their name → navigates to their personal card view

**Personal Card View:**
- Manager sees web preview of their 4 cards
- Cards displayed in Instagram Story format (9:16 ratio)
- Swipe/scroll through all 4 cards

**Download:**
- "Download All Cards" button → downloads 4 PNG images (1080×1920 each)
- Files named: `{manager_name}_1_leader.png`, `{manager_name}_2_ledger.png`, etc.
- Ready to share on Instagram Stories, Twitter, group chats

## Technical Architecture

### Current State
✅ **Data Layer:** Python calculator generates JSON with all metrics
✅ **4-Card System:** Leader, Ledger, Lineup, Legend
✅ **10 Archetype System:** Max 3 per archetype per league
✅ **4-Metric Scoring:** Draft, Lineups, Bye Week, Waivers (25% each)

### To Build
🔲 **Card Renderer:** Convert JSON → 1080×1920 PNG images
🔲 **Web Preview:** League page with manager selector
🔲 **Hosting:** Static site or web app for league pages
🔲 **Download System:** Generate and serve PNG files

## Design Specifications

### Card Dimensions
- **Resolution:** 1080×1920px (Instagram Story size)
- **Aspect Ratio:** 9:16
- **Format:** PNG with transparency support
- **Color Scheme:** Medieval/parchment theme (current website colors)

### Card Layout
- **Header:** Card name (The Leader, The Ledger, etc.)
- **Body:** Metrics, stats, visualizations
- **Footer:** Manager name, season, league
- **Branding:** Small Fantasy Reckoning logo

### Typography
- **Headings:** Playfair Display (serif, medieval feel)
- **Body:** System fonts (readability)
- **Accent:** Old English/blackletter for card titles

## Distribution Model

### One Computation Per League
- Commissioner generates once for entire league
- All managers access same generation
- Prevents redundant API calls and processing

### Shareable Link Model
- Persistent URLs for each league season
- Example: `fantasyreckoning.com/league/LOGE_2025`
- Enables async access (managers view when convenient)
- No account/login required

### Individual Downloads
- Each manager downloads only their 4 cards
- No ZIP files or bulk downloads
- Mobile-friendly (save directly to Photos)
- Social media ready

## Success Metrics

### Engagement
- % of league members who click the shared link
- % who download their cards
- % who share on social media

### Viral Growth
- Leagues generated per week
- Instagram Story shares (trackable via hashtag)
- Twitter shares with #FantasyReckoning

### User Experience
- Time from link click to download
- Mobile vs desktop usage
- Repeat usage (same league, different seasons)

## Future Enhancements

### Phase 2
- Email delivery option (automated to all managers)
- Twitter/Instagram direct sharing (API integration)
- Custom branding (league logos, colors)

### Phase 3
- Multi-season comparison cards
- League-wide leaderboard card
- Animated/video cards for stories

### Phase 4
- ESPN and Sleeper platform support
- Dynasty league tracking
- Historical archives

## Open Questions

1. **Hosting:** Static site (Netlify/Vercel) or dynamic app (requires backend)?
2. **Data Persistence:** Store generated cards or regenerate on demand?
3. **Rate Limiting:** How many leagues can generate per day?
4. **Cost:** Free forever or freemium model?
5. **Privacy:** How long do we keep league data/cards?

## Next Steps

### Immediate (MVP)
1. Build card renderer (JSON → PNG)
2. Design 4 card templates (1080×1920)
3. Create league preview web page
4. Implement download functionality
5. Test with LOGE league data

### Short Term
1. Yahoo API integration (automated data pull)
2. Production hosting
3. Analytics tracking
4. Email capture integration

### Long Term
1. Visual card improvements
2. Additional platforms (ESPN, Sleeper)
3. Advanced features (animations, videos)
4. Monetization strategy

---

**Last Updated:** 2025-12-22
**Status:** Product Definition Complete → Ready for Development
