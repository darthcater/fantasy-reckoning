# Fantasy Reckoning - Project Context

## Overview
Fantasy football season review card generator. Pulls data from Yahoo Fantasy API and generates shareable cards for each manager.

## Typography Standards

| Element | Font | Size | Style |
|---------|------|------|-------|
| Section headers | League Gothic | 0.9rem | uppercase, letter-spacing: 0.05em |
| Row labels | League Gothic | 1.0rem | uppercase, color: #e8d5b5 |
| Hero values (archetype, record) | League Gothic | 2.0rem | uppercase, color: #b8864f |
| Player names | EB Garamond | 0.95rem | font-weight: 600, color: #b8864f |
| Stats/values | EB Garamond | 0.95rem | colored by context |
| Descriptions | EB Garamond | 0.85rem | italic for footnotes |
| Logo/wordmark | Pirata One | - | Fantasy Reckoning brand only |

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Gold | #b8864f | Player names, hero values, positive highlights |
| Cream | #e8d5b5 | Labels, neutral text, zero values |
| Green | #6fa86f | Positive values (gains, wins) |
| Red | #c96c6c | Negative values (losses, busts, drops) |
| Background | #252a34 | Card background |

**Important**: Zero values get neutral color (#e8d5b5) with no +/- sign.

## Card Structure

### Card 1: The Leader
- Manager archetype (name + description)
- Skill percentiles vs league (Draft, Lineups, Bye Week, Waivers)
- Overall percentile

### Card 2: The Ledger
- **Your Balance**: Draft, Waivers, Trades, Costly Drops (with ranks)
- **Key Moves** (5 items in grid layout):
  - Best Value (draft pick, pts/$)
  - Biggest Bust (draft pick, pts/$)
  - Best Add (waiver pickup, pts)
  - Trade Win/Loss (dynamic label based on impact)
  - Costly Drop (pts to opponent)
- Footnote: "Points = started in lineup (opponent for drops)"

### Card 3: The Lineup
- Deployment stats (efficiency, records, bench waste)
- Pivotal moment (Fatal Error or Clutch Call)

### Card 4: The Legend
- The Reckoning (true skill record)
- Fortune's Hand (Schedule Luck, Opponent Blunders)
- Agent of Chaos (high-variance player)

## Layout Standards

- Card dimensions: 1080x1920px (Instagram Story, 9:16 ratio)
- Tables use CSS grid: `grid-template-columns: auto 1fr auto`
  - Column 1: Labels (left-aligned)
  - Column 2: Player names (center-aligned)
  - Column 3: Values (right-aligned)
- Mobile preview: `max-width: 400px` with `aspect-ratio: 9/16`

## Key Files

| File | Purpose |
|------|---------|
| `html_generator.py` | Generates league pages with all managers' cards |
| `generate_homepage.py` | Generates homepage preview cards |
| `website/index.html` | Homepage (marketing + preview) |
| `archetypes.py` | Manager archetype definitions and scoring |
| `fantasy_wrapped_calculator.py` | Core calculations from Yahoo data |

## PNG Download

Using `html-to-image` library for client-side PNG capture:
- Clone card element, apply 1080x1920 styles, capture, remove clone
- `fontEmbedCSS` option handles Google Fonts embedding
- Wait for `document.fonts.ready` before capture

## Brand Voice

The **Reckoning Scribe** style:
- Dark, ominous, dramatic, judgmental tone
- Archaic vocabulary (thou, thy, hath, doth, ere)
- Medieval/biblical imagery (tribunal, ledger, reckoning, judgment)
- Balance accessibility with atmosphere

See `.claude/commands/scribe.md` for full style guide.

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/preview` | Regenerate homepage and open in browser |
| `/test` | Run pytest suite |
| `/standards` | Display design standards |
| `/commit [msg]` | Stage all and commit with message |
| `/card [1-4]` | Load specific card's generation code |
| `/scribe [text]` | Generate archaic copy |
