# Fantasy Reckoning - User Journey

## What is Fantasy Reckoning?

Fantasy Reckoning is a personalized year-end review for your fantasy football season. Like Spotify Wrapped, but for fantasy football - it analyzes your entire season and generates 4 distinct cards that tell the story of your performance.

## The 4 Cards

### Card 1: The Leader
**How you played and stacked up against your rivals**
- ONE manager archetype that defines your playing style (e.g., "The Tinkerer", "The Hermit", "The Gambler")
- 4 skill percentiles vs league: Draft Performance, Lineup Efficiency, Bye Week Management, Waiver Activity
- Each metric weighted equally (25%) for overall excellence score
- Clean, character stats card format

### Card 2: The Ledger
**Where your points came from (and where they went)**
- Points breakdown: Draft, Waivers, Trades, Costly Drops
- Best Value: Your most cost-efficient draft pick
- Biggest Bust: Your most expensive disappointment
- Trade Win/Loss: Net impact of your trades
- Worst Drop: Most valuable player you gave away

### Card 3: The Lineup
**How you deployed your roster in battle**
- Lineup efficiency percentage (actual vs optimal points)
- Bench points wasted
- With-perfect-lineups record (what your record would be)
- Fatal errors (biggest missed opportunities)
- Preventable losses count

### Card 4: The Legend
**The story of your season, where fate and folly intertwined**
- Win attribution (draft impact, lineup decisions, schedule luck)
- All-play record vs actual record (skill vs luck)
- True skill record (schedule-adjusted performance)
- Playoff results and comparison
- Schedule luck quantification

## How It Works

### 1. Data Collection
The system pulls data from Yahoo Fantasy Football API:
- League settings and rosters
- Weekly matchups and scores
- Draft results
- All transactions (adds, drops, trades)
- Player performance week-by-week

### 2. Data Processing
The calculator analyzes:
- **Draft performance**: Compares where players were drafted vs how they finished
- **Lineup efficiency**: Actual points vs optimal possible points each week
- **Bye week management**: How well you handled roster constraints when starters were on bye
- **Waiver activity**: Net value added via waiver pickups (points started minus costly drops)
- **Trade impact**: Points gained or lost through trades
- **Schedule luck**: Difference between actual record and all-play record

### 3. Card Generation
Each card is generated independently with specific metrics:
- The Ledger, The Lineup, and The Legend are generated first (they collect the raw data)
- The Leader is generated last (it synthesizes data from other cards)

### 4. Output
Generates JSON files for each manager:
```
fantasy_wrapped_{manager_name}.json
```

## Getting Started

### Prerequisites
- Python 3.7+
- Yahoo Fantasy Football league (2025 season)
- League data exported as JSON

### Installation
```bash
# Clone the repository
git clone [your-repo-url]
cd fantasy_wrapped_data_puller

# Install dependencies
pip install -r requirements.txt
```

### Running the Calculator
```bash
# Place your league JSON file in the directory
# Named as: league_{league_id}_{season}.json

# Run the calculator
python3 fantasy_wrapped_calculator.py

# Output files will be generated as fantasy_wrapped_{manager_name}.json
```

## Understanding Your Results

### Excellence Score (The Leader)
- 80-100: Elite season, top tier performance
- 60-80: Strong season, above average
- 40-60: Average season, middle of the pack
- 20-40: Below average season, struggled in key areas
- 0-20: Poor season, major weaknesses

### Manager Archetypes (The Leader)
Your archetype is determined by your behavior and play style:
- **Activity level**: How often you make moves
- **Trading behavior**: Frequency and impact of trades
- **Risk profile**: Variance in your scoring and roster decisions
- **Lineup management**: How efficiently you set lineups
- **Consistency**: Week-to-week scoring stability

10 Core Archetypes:
- **The Tinkerer**: Constantly adjusting, never satisfied
- **The Loyalist**: Rides with drafted players through triumph and tragedy
- **The Dealer**: Lives to negotiate, thrives in the marketplace
- **The Hermit**: Builds in isolation, trusts no one
- **The Gambler**: Swings for the fences, chasing upside over safety
- **The Conservative**: Plays the percentages, avoids variance
- **The Optimizer**: Squeezes every possible point from thy roster
- **The Erratic**: Trusts gut over data, often incorrectly
- **The Rock**: Reliable week after week, unwavering consistency
- **The Rollercoaster**: Wild swings define thy season

### Draft Grades (The Ledger)
- **A**: Elite draft, found multiple steals
- **B**: Good draft, solid foundation
- **C**: Average draft, mixed results
- **D**: Poor draft, costly busts
- **F**: Terrible draft, season-killing mistakes

### Lineup Efficiency (The Lineup)
- **85%+**: Excellent lineup management
- **75-85%**: Good lineup management
- **65-75%**: Average lineup management
- **50-65%**: Poor lineup management, leaving points on bench
- **<50%**: Severe lineup issues

## File Structure
```
fantasy_wrapped_data_puller/
├── fantasy_wrapped_calculator.py  # Main calculator engine
├── card_1_overview.py             # Card 1: The Leader generation
├── card_2_ledger.py               # Card 2: The Ledger generation
├── card_3_lineups.py              # Card 3: The Lineup generation
├── card_4_story.py                # Card 4: The Legend generation
├── archetypes.py                  # Manager archetype determination (10 archetypes, max 3 per)
├── bye_week_calculation.py        # Bye week management analysis
├── league_metrics.py              # Shared metric calculations
├── costly_drops_calculation.py    # Costly drops analysis
├── trade_impact_calculation.py    # Trade impact analysis
├── league_{league_id}_{season}.json  # Your league data (input)
└── fantasy_wrapped_{manager}.json    # Generated reports (output)
```

## Customization

### Adjusting Weights (The Leader)
Edit `card_1_overview.py` to adjust how different dimensions contribute to excellence score:
```python
weights = {
    'draft': 0.25,        # 25% - Foundation of your team
    'lineups': 0.25,      # 25% - Weekly decision-making
    'bye_weeks': 0.25,    # 25% - Planning and depth under constraints
    'waivers': 0.25       # 25% - Roster improvement
}
```

### Adding New Archetypes
Edit `archetypes.py` to add new manager personality types

### Modifying Metrics
Each card file contains its own metric calculations and can be customized independently

## Troubleshooting

### Common Issues

**"No league data file found"**
- Ensure your league JSON is named correctly: `league_{league_id}_{season}.json`
- Check that the file is in the same directory as the calculator

**"Card generation failed"**
- Check the error message in the output
- Ensure all required data fields are present in your league JSON
- Verify that the season has enough weeks of data (minimum 4 weeks recommended)
- Check that player data uses 'actual_points' field (not 'points')

## Future Enhancements
- Web interface for viewing cards
- Visual card designs (currently JSON only)
- Support for other fantasy platforms (ESPN, Sleeper)
- Multi-season comparisons
- League-wide leaderboards

## Questions or Issues?
Open an issue on GitHub or check existing documentation

---

**Remember**: This is a FUN season review tool. Don't take the grades too seriously - fantasy football has a lot of luck involved!
