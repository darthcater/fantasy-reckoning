# Fantasy Wrapped - Yahoo API Data Puller

A Python script to extract complete fantasy football season data from Yahoo Fantasy Sports API for Fantasy Wrapped analysis.

## Features

- OAuth2 authentication with Yahoo Fantasy API
- Extract league metadata, teams, and standings
- Pull weekly scoring and roster data for all teams
- Retrieve complete transaction history
- Get draft results
- Calculate optimal lineups (points left on bench)
- Export all data to structured JSON format

---

## Setup Instructions

### 1. Yahoo Developer App Setup

**First, register your application with Yahoo:**

1. Go to https://developer.yahoo.com/apps/create/
2. Sign in with your Yahoo account (the one with your fantasy league)
3. Click "Create an App"
4. Fill in the form:
   - **Application Name:** `Fantasy Wrapped Data Puller` (or any name)
   - **Application Type:** Select **"Installed Application"**
   - **Description:** Optional
   - **Callback Domain:** `localhost`
   - **API Permissions:** Check **"Fantasy Sports"** and select **"Read"**
5. Click "Create App"
6. **Save your credentials:**
   - **Client ID** (Consumer Key)
   - **Client Secret** (Consumer Secret)

### 2. Find Your League ID

1. Go to your Yahoo Fantasy Football league page
2. Look at the URL: `https://football.fantasysports.yahoo.com/f1/12345/...`
3. The number after `/f1/` is your **League ID** (e.g., `12345`)

### 3. Install Python Dependencies

```bash
cd fantasy_wrapped_data_puller
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:
```
YAHOO_CLIENT_ID=your_actual_client_id
YAHOO_CLIENT_SECRET=your_actual_client_secret
LEAGUE_ID=your_league_id
SEASON_YEAR=2024
```

### 5. Create OAuth Configuration File

Create a file named `oauth2.json` in the same directory:

```json
{
  "consumer_key": "your_client_id",
  "consumer_secret": "your_client_secret"
}
```

**Important:** Replace `your_client_id` and `your_client_secret` with your actual Yahoo credentials.

---

## Usage

### Run the Data Puller

```bash
python data_puller.py
```

### What Happens:

1. **First Time Authentication:**
   - A browser window will open
   - You'll be asked to authorize the app
   - Copy the verification code from the URL
   - Paste it into the terminal

2. **Data Extraction:**
   - The script will fetch all league data
   - Progress will be shown for each team and week
   - This may take 2-5 minutes depending on league size

3. **Output:**
   - JSON file: `league_[id]_[year].json`
   - Contains all data needed for Fantasy Wrapped analysis

### Subsequent Runs

After the first authentication, the OAuth token is saved to `oauth2.json`. You won't need to re-authorize unless the token expires (typically 1 hour).

---

## Output Data Structure

The generated JSON contains:

```json
{
  "league": {
    "league_id": "12345",
    "name": "Your League Name",
    "season": 2024,
    "num_teams": 14,
    "playoff_start_week": 15
  },
  "teams": [
    {
      "team_id": "1",
      "team_name": "Team Name",
      "manager_name": "Manager Name",
      "final_standing": 6,
      "wins": 7,
      "losses": 7,
      "points_for": 1247.5,
      "points_against": 1456.8
    }
  ],
  "weekly_data": {
    "team_id": {
      "week_1": {
        "week": 1,
        "actual_points": 112.4,
        "projected_points": 105.2,
        "bench_points": 28.6,
        "opponent_id": "5",
        "opponent_points": 98.3,
        "result": "W",
        "roster": {
          "starters": [...],
          "bench": [...]
        },
        "optimal_lineup": {
          "optimal_points": 125.8,
          "actual_points": 112.4,
          "points_left_on_bench": 13.4,
          "bench_mistakes": [...]
        }
      }
    }
  },
  "transactions": [...],
  "draft": [...],
  "generated_at": "2024-12-08T..."
}
```

---

## Troubleshooting

### "Authentication failed" or "Invalid token"

- Make sure your `oauth2.json` file has the correct Client ID and Secret
- Delete `oauth2.json` and run again to re-authenticate
- Check that your Yahoo app has "Fantasy Sports" API permission enabled

### "League ID not found"

- Verify your League ID is correct (from the URL)
- Make sure you're logged into Yahoo with the correct account
- Ensure the league is from the correct season year

### "Rate limit exceeded"

- The script has built-in delays (0.5s between requests)
- If you still hit limits, increase the delay in `_make_api_call_with_delay()`

### "Module not found" errors

- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Try using a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

---

## Next Steps

Once you have successfully extracted your league data:

1. **Validate the data:** Open the JSON file and spot-check a few weeks
2. **Calculate metrics:** Use this data to compute Fantasy Wrapped metrics
3. **Build visualizations:** Create charts and graphics for your wrapped summary

---

## Data Privacy

- Your OAuth tokens are stored locally in `oauth2.json`
- The extracted data is saved locally as JSON
- No data is sent to external servers
- Keep your `.env` and `oauth2.json` files private (they're in `.gitignore`)

---

## Support

For issues or questions:
- Check the Yahoo Fantasy Sports API docs: https://developer.yahoo.com/fantasysports/guide/
- Review the troubleshooting section above
- Ensure all setup steps were completed correctly

---

## License

This is a personal project for Fantasy Wrapped analysis.
