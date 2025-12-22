# Fantasy Reckoning - Development Roadmap

## Current State ✅
- ✅ Data calculator (Python) generates JSON for all 4 cards
- ✅ 10 archetype system with max 3 per league
- ✅ 4-metric scoring (Draft, Lineups, Bye Week, Waivers)
- ✅ Website with card previews (Instagram 9:16 ratio)
- ✅ Product spec defined
- ✅ User flow clarified

## What Needs to Be Built

### Phase 1: MVP (Core Functionality)

#### 1. Card Renderer 🎨
**Priority: CRITICAL**
**Status:** Not started

Convert JSON data → 1080×1920 PNG images

**Requirements:**
- Input: JSON files (existing output from calculator)
- Output: 4 PNG images per manager (1080×1920px each)
- Design: Medieval/parchment theme matching website
- Cards: The Leader, The Ledger, The Lineup, The Legend

**Technical Options:**
- **Python:** Pillow/PIL for image generation
- **Node.js:** Sharp or Canvas for rendering
- **Web:** HTML Canvas → PNG export
- **Design Tools:** Figma → Export templates → Programmatic fill

**Deliverables:**
- [ ] Card 1: The Leader template (1080×1920)
- [ ] Card 2: The Ledger template (1080×1920)
- [ ] Card 3: The Lineup template (1080×1920)
- [ ] Card 4: The Legend template (1080×1920)
- [ ] Renderer script (JSON → PNG)
- [ ] Test with LOGE league data

---

#### 2. League Preview Web Page 🌐
**Priority: HIGH**
**Status:** Not started

Web interface where users view and download cards

**Requirements:**
- URL format: `fantasyreckoning.com/league/{league_id}_{season}`
- Manager selector (dropdown or grid)
- Card viewer (swipe/scroll through 4 cards)
- Download button (all 4 cards as PNGs)

**Technical Stack Options:**
- **Static:** Next.js/React with pre-generated pages
- **Dynamic:** Node.js/Express serving on-demand
- **Hybrid:** Static site with client-side rendering

**User Flow:**
1. Land on league page → see all manager names
2. Click manager name → navigate to their card view
3. View 4 cards (swipe/scroll)
4. Click "Download Cards" → get 4 PNG files

**Deliverables:**
- [ ] League landing page (manager selector)
- [ ] Individual manager card viewer
- [ ] Download functionality (4 PNGs)
- [ ] Mobile-responsive design
- [ ] Social share buttons (optional)

---

#### 3. Generation Pipeline 🔧
**Priority: HIGH**
**Status:** Not started

Automated flow from league ID → shareable link

**Requirements:**
- User enters Yahoo league ID
- System pulls data from Yahoo API (or JSON upload for MVP)
- Runs calculator → generates JSON
- Runs renderer → generates PNG cards
- Creates league page → returns shareable link

**MVP Approach (Manual):**
1. User uploads `league_{id}_{season}.json` file
2. System processes locally
3. Generates cards
4. Provides shareable link

**Future (Automated):**
1. User enters league ID
2. System calls Yahoo API
3. Processes automatically
4. Generates cards + link

**Deliverables:**
- [ ] File upload interface (MVP)
- [ ] Processing pipeline (JSON → PNGs → link)
- [ ] League page generation
- [ ] Shareable link system

---

### Phase 2: Polish & Optimization

#### 4. Yahoo API Integration 🔌
**Priority: MEDIUM**
**Status:** Not started

Automate data pulling (no manual JSON upload)

**Requirements:**
- OAuth authentication with Yahoo
- League data fetching
- Player stats pulling
- Transaction history

**Deliverables:**
- [ ] Yahoo OAuth flow
- [ ] API data fetcher
- [ ] Data normalization (API → calculator format)

---

#### 5. Hosting & Deployment 🚀
**Priority: MEDIUM**
**Status:** Not started

Production-ready infrastructure

**Options:**
- **Vercel/Netlify:** Static site hosting (free tier)
- **Railway/Render:** Dynamic app hosting
- **AWS/GCP:** Full control, more complex

**Requirements:**
- Fast page loads
- Reliable image serving
- Handle concurrent users
- CDN for images

**Deliverables:**
- [ ] Production hosting setup
- [ ] Domain configuration
- [ ] SSL certificate
- [ ] CDN setup (Cloudflare)

---

#### 6. Analytics & Tracking 📊
**Priority: LOW**
**Status:** Not started

Understand user behavior

**Metrics to Track:**
- Leagues generated per day
- Cards downloaded per league
- Social shares (Instagram, Twitter)
- Bounce rate on league pages

**Tools:**
- Google Analytics
- Plausible (privacy-focused)
- Custom event tracking

**Deliverables:**
- [ ] Analytics integration
- [ ] Event tracking (downloads, shares)
- [ ] Dashboard for metrics

---

### Phase 3: Advanced Features

#### 7. Visual Improvements 🎨
- Card animations (subtle motion graphics)
- Video cards (animated stats)
- Dark mode cards
- Custom color schemes per league

#### 8. Platform Expansion 🏈
- ESPN league support
- Sleeper league support
- NFL.com league support

#### 9. Premium Features 💎
- Multi-season comparison cards
- League-wide leaderboard card
- Custom branding (league logos)
- Historical archives

---

## Recommended Build Order

### Week 1-2: Card Design & Rendering
1. Design 4 card templates in Figma (1080×1920)
2. Build renderer (JSON → PNG)
3. Test with LOGE league data
4. Iterate on design

### Week 3-4: Web Interface
1. Build league preview page
2. Create manager card viewer
3. Implement download functionality
4. Mobile optimization

### Week 5-6: Integration & Launch
1. Connect renderer to web interface
2. Set up hosting
3. Deploy MVP
4. Test with real users (LOGE league)

### Week 7+: Iteration
1. Gather user feedback
2. Add Yahoo API integration
3. Scale infrastructure
4. Add analytics

---

## Open Technical Questions

1. **Storage:** Where do we store generated PNGs?
   - S3/Cloudinary vs. regenerate on-demand?
   - How long do we keep them?

2. **Caching:** How do we handle same league ID requested twice?
   - Cache cards for 24 hours?
   - Allow manual regeneration?

3. **Rate Limiting:** How many leagues per IP per day?
   - Prevent abuse
   - Balance accessibility

4. **Cost:** What's the hosting/storage budget?
   - Free tier feasible for MVP?
   - When do we need paid infrastructure?

---

## Next Immediate Steps

**Right Now:**
1. ✅ Finalize product spec ✅
2. ✅ Update website with user flow ✅
3. 🔲 Design first card template (The Leader) in Figma
4. 🔲 Build proof-of-concept renderer (one card)
5. 🔲 Test rendering with Max's LOGE data

**This Week:**
- Design all 4 card templates
- Build renderer for all 4 cards
- Create simple HTML preview page

**This Month:**
- Complete web interface
- Deploy MVP
- Test with LOGE league

---

**Status:** Ready to start building
**Last Updated:** 2025-12-22
