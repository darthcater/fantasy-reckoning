---
description: Show project design standards
---

Reference the Fantasy Reckoning design standards:

## Typography
- **League Gothic**: Section headers, labels (uppercase, 0.9-1.0rem, letter-spacing: 0.05em)
- **EB Garamond**: Player names (0.95rem, #b8864f gold, font-weight: 600), stats, descriptions
- **Pirata One**: Logo/wordmark only

## Colors
- Gold (player names): `#b8864f`
- Cream (labels): `#e8d5b5`
- Green (positive): `#6fa86f`
- Red (negative): `#c96c6c`
- Neutral (zero values): `#e8d5b5` (no +/- sign)

## Layout
- Card size: 1080x1920px (Instagram story)
- Tables: CSS grid `grid-template-columns: auto 1fr auto`
- Labels left, content center, values right

## Card Structure
1. **The Leader** - Archetype + skill percentiles
2. **The Ledger** - Your Balance + Key Moves (5 items)
3. **The Lineup** - Efficiency + pivotal moment
4. **The Legend** - True skill record + luck factors

Always apply these standards when editing card generation code.
