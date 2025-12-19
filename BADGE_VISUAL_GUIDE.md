# Legacy Badge & Mark Visual Design Guide

## Overview
Card V: The Legacy awards each manager 3 achievements - a mix of **Badges** (honors) and **Marks** (shames) based on their season performance.

## Data Structure
Each manager's JSON has a `legacy_achievements` array with exactly 3 items:

```json
"legacy_achievements": [
  {
    "id": "rock_of_ages",
    "name": "Rock of Ages",
    "description": "Scored with unwavering consistency",
    "type": "badge",
    "category": "consistency",
    "tier": 4,
    "icon": "🗿"
  },
  {
    "id": "steady_hand",
    "name": "Steady Hand",
    "description": "Set lineups with reliable consistency",
    "type": "badge",
    "category": "lineup",
    "tier": 1,
    "icon": "🤲"
  },
  {
    "id": "costly_dropper",
    "name": "The Costly Dropper",
    "description": "Armed thy enemies with dropped talent",
    "type": "mark",
    "category": "waivers",
    "tier": 4,
    "icon": "💀"
  }
]
```

## Visual Design Concepts

### Option 1: Shield/Crest Design (Recommended)
Display 3 shield/crest icons horizontally across Card V:

**Badges (Good):**
- Background: Gold gradient for tier 4, silver for tier 3, bronze for tier 2-1
- Border: Ornate medieval frame, glowing effect
- Icon: Displayed prominently in center
- Accent: Laurel wreaths, stars, light rays

**Marks (Bad):**
- Background: Dark red/crimson gradient, charcoal for lower tiers
- Border: Iron chains, jagged edges, weathered look
- Icon: Displayed with ominous glow
- Accent: Cracked texture, burn marks, shadows

### Option 2: Wax Seal Design
Display as 3 wax seal stamps:

**Badges:**
- Color: Gold, royal blue, or emerald green
- Style: Embossed, raised appearance
- Effect: Metallic sheen, official stamp look

**Marks:**
- Color: Deep red, charcoal black
- Style: Branded/burned into surface
- Effect: Scarlet letter aesthetic, scorched edges

### Option 3: Banner/Ribbon Design
Display as 3 medieval banner ribbons:

**Badges:**
- Color: Rich colors (gold, royal blue, emerald)
- Style: Flowing ribbons with ornate text
- Effect: Pride, honor, celebration

**Marks:**
- Color: Blood red, ash grey, burnt orange
- Style: Tattered, torn ribbons
- Effect: Shame, dishonor, warning

## HTML/CSS Structure Example

```html
<div class="legacy-achievements">
  <!-- Achievement 1: Badge (Tier 4) -->
  <div class="achievement badge tier-4">
    <div class="achievement-icon">🗿</div>
    <div class="achievement-name">Rock of Ages</div>
    <div class="achievement-description">Scored with unwavering consistency</div>
  </div>

  <!-- Achievement 2: Badge (Tier 1) -->
  <div class="achievement badge tier-1">
    <div class="achievement-icon">🤲</div>
    <div class="achievement-name">Steady Hand</div>
    <div class="achievement-description">Set lineups with reliable consistency</div>
  </div>

  <!-- Achievement 3: Mark (Tier 4) -->
  <div class="achievement mark tier-4">
    <div class="achievement-icon">💀</div>
    <div class="achievement-name">The Costly Dropper</div>
    <div class="achievement-description">Armed thy enemies with dropped talent</div>
  </div>
</div>
```

## CSS Styling Suggestions

```css
.legacy-achievements {
  display: flex;
  gap: 1.5rem;
  justify-content: space-between;
  margin: 2rem 0;
}

.achievement {
  flex: 1;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  position: relative;
  border: 2px solid;
}

/* BADGES (Good) */
.achievement.badge {
  background: linear-gradient(135deg, #f4e4c1 0%, #e8d5a0 100%);
  border-color: #c9a961;
  box-shadow: 0 4px 12px rgba(201, 169, 97, 0.3);
}

.achievement.badge.tier-4 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  border-color: #d4af37;
  box-shadow: 0 4px 16px rgba(255, 215, 0, 0.5);
}

.achievement.badge.tier-3 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  border-color: #a8a8a8;
}

.achievement.badge .achievement-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

/* MARKS (Bad) */
.achievement.mark {
  background: linear-gradient(135deg, #4a1a1a 0%, #6b2020 100%);
  border-color: #8b0000;
  color: #ffd4d4;
  box-shadow: 0 4px 12px rgba(139, 0, 0, 0.4);
}

.achievement.mark.tier-4 {
  background: linear-gradient(135deg, #2a0a0a 0%, #4a0a0a 100%);
  border-color: #ff0000;
  box-shadow: 0 4px 16px rgba(255, 0, 0, 0.4);
}

.achievement.mark .achievement-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  filter: drop-shadow(0 2px 6px rgba(255,0,0,0.6));
  animation: ominous-glow 2s ease-in-out infinite;
}

@keyframes ominous-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.achievement-name {
  font-family: 'MedievalFont', serif;
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.achievement-description {
  font-size: 0.85rem;
  opacity: 0.9;
  font-style: italic;
}
```

## Icon Replacements (If Using Custom SVGs)

If you want to replace emoji icons with custom SVG graphics:

### Badge Icons:
- 👑 Crown → Royal crown SVG
- 🏆 Trophy → Trophy SVG
- ⚡ Lightning → Power bolt SVG
- 🎖️ Medal → Military medal SVG
- 🔮 Crystal ball → Mystical orb SVG

### Mark Icons:
- 💀 Skull → Skeleton skull SVG
- ⛓️ Chains → Iron shackles SVG
- 🔥 Fire → Burning flames SVG
- ⚠️ Warning → Danger sign SVG
- 🪑 Chair → Bench SVG (for "Bench Folly")

## Placement on Card V

**Recommended Layout:**
```
┌─────────────────────────────────────┐
│     CARD V: THE LEGACY              │
├─────────────────────────────────────┤
│                                     │
│  [Season Arc Narrative Section]    │
│                                     │
├─────────────────────────────────────┤
│         YOUR LEGACY                 │
│                                     │
│  ┌──────┐   ┌──────┐   ┌──────┐   │
│  │ 🗿   │   │ 🤲   │   │ 💀   │   │
│  │Badge │   │Badge │   │ Mark │   │
│  └──────┘   └──────┘   └──────┘   │
│                                     │
├─────────────────────────────────────┤
│  [Archetype & Final Reflection]    │
└─────────────────────────────────────┘
```

## Achievement Categories Breakdown

| Category | Tracks | Example Badges | Example Marks |
|----------|--------|----------------|---------------|
| **Trading** | Trade activity & success | Trade Emperor, Trade Baron | The Eternally Swindled, Brand of Ruin |
| **Waivers** | Waiver wire performance | Lord of the Wire, Waiver Predator | The Costly Dropper, Mark of Missed Chances |
| **Draft** | Draft quality | Master of Draft Table, Draft Savant | The Ruinous Draft, Brand of Wasted Coin |
| **Lineup** | Lineup efficiency | The Perfect Seer, Lineup Sage | The Perpetually Wrong, Brand of Bench Folly |
| **Performance** | Season results | Champion Eternal, Playoff Warrior | The Forsaken, Brand of Last Place |
| **Consistency** | Scoring variance | Rock of Ages, Reliable Pillar | Mark of Chaos, The Unpredictable |
| **Special** | Unique situations | The Iron Throne, The Glass Cannon | The Schedule-Cursed, Mark of Stolen Valor |

## Tier System

- **Tier 4** (Legendary): Rarest, most impactful - top tier visual treatment
- **Tier 3** (Epic): Significant achievement - enhanced visual effects
- **Tier 2** (Rare): Notable performance - moderate visual distinction
- **Tier 1** (Common): Base level - standard visual treatment

## How to Implement

1. **Read the data**: Each manager's JSON has `card_5_legacy.legacy_achievements` array
2. **Loop through 3 achievements**: Display each with appropriate styling based on `type` and `tier`
3. **Apply conditional styling**: Use `type === 'badge'` for gold/silver, `type === 'mark'` for red/dark
4. **Scale by tier**: Higher tier = more dramatic visual effects (shadows, glows, borders)
5. **Use the icon**: Display the emoji/SVG icon prominently in each achievement card

## Notes

- System automatically awards exactly 3 achievements per manager
- Mix is determined by performance (great seasons = mostly badges, poor = mostly marks)
- Each achievement is unique to avoid duplicate categories when possible
- Descriptions use medieval/dramatic language to match theme
