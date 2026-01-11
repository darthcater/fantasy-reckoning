"""
Fantasy Reckoning - Production Web App
Proper OAuth flow for Yahoo Fantasy API
"""

import os
import time
import json
import glob
import secrets
import threading
from urllib.parse import urlencode
from flask import Flask, render_template_string, request, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Sessions directory - each user gets their own folder
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sessions')
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Session expiry time (24 hours)
SESSION_MAX_AGE_HOURS = 24


def get_session_dir(session_id):
    """Get or create a session directory for a user"""
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def cleanup_old_sessions():
    """Remove session directories older than SESSION_MAX_AGE_HOURS"""
    import shutil
    now = time.time()
    max_age_seconds = SESSION_MAX_AGE_HOURS * 3600
    cleaned = 0

    if not os.path.exists(SESSIONS_DIR):
        return 0

    for session_id in os.listdir(SESSIONS_DIR):
        session_dir = os.path.join(SESSIONS_DIR, session_id)
        if not os.path.isdir(session_dir):
            continue

        # Check directory age based on modification time
        dir_mtime = os.path.getmtime(session_dir)
        age = now - dir_mtime

        if age > max_age_seconds:
            try:
                shutil.rmtree(session_dir)
                cleaned += 1
            except Exception as e:
                print(f"Failed to remove old session {session_id}: {e}")

    return cleaned


# Clean up old sessions on startup
cleaned = cleanup_old_sessions()
if cleaned > 0:
    print(f"Cleaned up {cleaned} old session(s)")


# Yahoo OAuth Config
YAHOO_CLIENT_ID = os.environ.get('YAHOO_CLIENT_ID', 'dj0yJmk9UDZ0MFNTWHZXU3NQJmQ9WVdrOVNqVmhUWEl6YWtnbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTk3')
YAHOO_CLIENT_SECRET = os.environ.get('YAHOO_CLIENT_SECRET', 'da496bd8c9691e22b9fbc6b22e7e7d2b1dfa47bc')

# For local testing, use localhost. For production, use your domain
BASE_URL = os.environ.get('BASE_URL', 'https://localhost:8000')
CALLBACK_URL = f"{BASE_URL}/callback"

# Yahoo OAuth URLs
YAHOO_AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"

# Store for generation jobs (in production, use Redis or database)
generation_jobs = {}

# ============================================================================
# HTML TEMPLATES
# ============================================================================

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Fantasy Reckoning</title>
    <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'EB Garamond', serif;
            background-color: #252a34;
            color: #e8d5b5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            margin: 0;
        }
        h1 {
            font-family: 'Pirata One', cursive;
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        .tagline {
            font-size: 1.25rem;
            opacity: 0.8;
            margin-bottom: 2rem;
        }
        .container {
            background: rgba(61, 68, 80, 0.5);
            padding: 2rem 3rem;
            border-radius: 8px;
            border: 1px solid rgba(232, 213, 181, 0.2);
            text-align: center;
            max-width: 500px;
        }
        .btn {
            font-family: 'EB Garamond', serif;
            font-size: 1.25rem;
            padding: 1rem 2rem;
            background-color: #b8864f;
            color: #e8d5b5;
            border: 2px solid #9e6f47;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background-color: #9e6f47;
            transform: translateY(-2px);
        }
        .note {
            font-size: 0.9rem;
            opacity: 0.7;
            margin-top: 1.5rem;
        }
        .error {
            color: #c96c6c;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <h1>Fantasy Reckoning</h1>
    <p class="tagline">Your fantasy football season, judged.</p>
    <div class="container">
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        <p>Generate season review cards for your entire league and share with your group chat.</p>
        <br>
        <a href="/login" class="btn">Connect with Yahoo</a>
        <p class="note">Secure Yahoo login. We only read your league data.</p>
    </div>
</body>
</html>
"""

LEAGUE_SELECT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Fantasy Reckoning - Select League</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'EB Garamond', serif;
            background-color: #252a34;
            color: #e8d5b5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            margin: 0;
        }
        h1 { font-family: 'Pirata One', cursive; font-size: 2.5rem; margin-bottom: 1rem; text-align: center; }
        .container {
            background: rgba(61, 68, 80, 0.5);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid rgba(232, 213, 181, 0.2);
            max-width: 600px;
            width: 100%;
        }
        .league-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid rgba(232, 213, 181, 0.1);
            gap: 1rem;
        }
        .league-item:last-child { border-bottom: none; }
        .league-name { font-size: 1.1rem; }
        .league-info { font-size: 0.9rem; opacity: 0.7; }
        .btn {
            font-family: 'EB Garamond', serif;
            font-size: 1rem;
            padding: 0.75rem 1.25rem;
            background-color: #b8864f;
            color: #e8d5b5;
            border: none;
            cursor: pointer;
            text-decoration: none;
            white-space: nowrap;
            flex-shrink: 0;
        }
        .btn:hover { background-color: #9e6f47; }
        @media (max-width: 480px) {
            h1 { font-size: 2rem; }
            .league-item { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
            .btn { width: 100%; text-align: center; }
        }
    </style>
</head>
<body>
    <h1>Select Your League</h1>
    <div class="container">
        {% for league in leagues %}
        <div class="league-item">
            <div>
                <div class="league-name">{{ league.name }}</div>
                <div class="league-info">{{ league.num_teams }} teams • {{ league.season }}</div>
            </div>
            <a href="/generate/{{ league.league_id }}" class="btn">Generate</a>
        </div>
        {% endfor %}
    </div>
    <p style="margin-top: 1.5rem; text-align: center; opacity: 0.7;">
        <a href="/my-leagues" style="color: #e8d5b5;">View previously generated leagues</a>
    </p>
</body>
</html>
"""

GENERATING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Fantasy Reckoning - Generating...</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&family=League+Gothic&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'EB Garamond', serif;
            background-color: #252a34;
            color: #e8d5b5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            margin: 0;
        }
        h1 { font-family: 'Pirata One', cursive; font-size: 2.5rem; margin-bottom: 1rem; text-align: center; }
        .container {
            background: rgba(61, 68, 80, 0.5);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid rgba(232, 213, 181, 0.2);
            text-align: center;
            max-width: 500px;
            width: 100%;
        }
        .spinner {
            border: 4px solid rgba(232, 213, 181, 0.3);
            border-top: 4px solid #b8864f;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 1.5rem auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status { font-size: 1.1rem; margin: 1rem 0; }
        .time-note { font-size: 1rem; opacity: 0.8; line-height: 1.5; }

        /* Progress bar - matches Card 1 percentile bars */
        .progress-container { margin: 1.5rem 0; }
        .progress-bar {
            display: flex;
            gap: 4px;
            height: 8px;
            margin-bottom: 0.75rem;
        }
        .progress-segment {
            flex: 1;
            background: rgba(232, 213, 181, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-segment .fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #b8864f, #9e6f47);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .progress-segment.done .fill { width: 100%; }
        .progress-segment.active .fill {
            width: 100%;
            animation: pulse 1.5s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        .progress-labels {
            display: flex;
            justify-content: space-between;
            font-family: 'League Gothic', sans-serif;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .progress-label {
            flex: 1;
            text-align: center;
            opacity: 0.4;
            transition: opacity 0.3s ease, color 0.3s ease;
        }
        .progress-label.done { opacity: 1; color: #6fa86f; }
        .progress-label.active { opacity: 1; color: #b8864f; }

        @media (max-width: 480px) {
            h1 { font-size: 2rem; }
            .status { font-size: 1rem; }
            .time-note { font-size: 0.95rem; }
            .progress-labels { font-size: 0.7rem; }
        }
    </style>
    <script>
        function updateProgress(step) {
            const steps = ['starting', 'pulling', 'calculating', 'building'];
            const stepIndex = steps.indexOf(step);

            document.querySelectorAll('.progress-segment').forEach((seg, i) => {
                seg.classList.remove('done', 'active');
                if (i < stepIndex) seg.classList.add('done');
                else if (i === stepIndex) seg.classList.add('active');
            });

            document.querySelectorAll('.progress-label').forEach((label, i) => {
                label.classList.remove('done', 'active');
                if (i < stepIndex) label.classList.add('done');
                else if (i === stepIndex) label.classList.add('active');
            });
        }

        // Poll for status updates
        setInterval(function() {
            fetch('/status/{{ job_id }}')
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'complete') {
                        window.location.href = '/view/' + data.session_id + '/' + data.league_id;
                    } else if (data.status === 'error') {
                        document.querySelector('.status').textContent = 'Error: ' + data.error;
                    } else {
                        document.querySelector('.status').textContent = data.message || 'Processing...';
                        updateProgress(data.status);
                    }
                });
        }, 2000);
    </script>
</head>
<body>
    <h1>Generating Your Cards</h1>
    <div class="container">
        <div class="spinner"></div>
        <p class="status">Starting...</p>
        <p class="time-note">This typically takes <strong>5-7 minutes</strong> for a full league</p>
        <p class="time-note" style="margin-top: 0.5rem; font-size: 0.85rem;">We're pulling every week of data from Yahoo - grab a coffee!</p>

        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-segment active"><div class="fill"></div></div>
                <div class="progress-segment"><div class="fill"></div></div>
                <div class="progress-segment"><div class="fill"></div></div>
                <div class="progress-segment"><div class="fill"></div></div>
            </div>
            <div class="progress-labels">
                <span class="progress-label active">Connecting</span>
                <span class="progress-label">Pulling</span>
                <span class="progress-label">Calculating</span>
                <span class="progress-label">Building</span>
            </div>
        </div>

        <p style="margin-top: 1.5rem; font-size: 0.9rem; opacity: 0.6;">
            <a href="/leagues" style="color: #e8d5b5;">Taking too long? Start over</a>
            <span style="margin: 0 0.5rem;">•</span>
            <a href="/my-leagues" style="color: #e8d5b5;">View previous generations</a>
        </p>
    </div>
</body>
</html>
"""


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def home():
    """Serve the marketing homepage"""
    homepage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'website', 'index.html')
    if os.path.exists(homepage_path):
        with open(homepage_path, 'r') as f:
            return f.read()
    # Fallback to simple OAuth page if homepage not found
    error = request.args.get('error')
    return render_template_string(HOME_HTML, error=error)


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from website folder (images, fonts, etc.)"""
    from flask import send_from_directory
    website_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'website')
    filepath = os.path.join(website_dir, filename)
    if os.path.exists(filepath) and not os.path.isdir(filepath):
        return send_from_directory(website_dir, filename)
    # If not a static file, return 404
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fantasy Reckoning - Not Found</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'EB Garamond', serif; background: #252a34; color: #e8d5b5; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; margin: 0; }
            h1 { font-family: 'Pirata One', cursive; font-size: 2.5rem; margin-bottom: 1rem; }
            .container { background: rgba(61, 68, 80, 0.5); padding: 2rem; border-radius: 8px; border: 1px solid rgba(232, 213, 181, 0.2); text-align: center; max-width: 500px; }
            a { color: #b8864f; }
            .btn { display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; background: #b8864f; color: #e8d5b5; text-decoration: none; border: none; }
        </style>
    </head>
    <body>
        <h1>Not Found</h1>
        <div class="container">
            <p>The page you're looking for doesn't exist.</p>
            <a href="/" class="btn">Go Home</a>
        </div>
    </body>
    </html>
    """, 404


@app.route('/login')
def login():
    """Redirect to Yahoo for OAuth authorization"""
    params = {
        'client_id': YAHOO_CLIENT_ID,
        'redirect_uri': CALLBACK_URL,
        'response_type': 'code',
    }
    auth_url = f"{YAHOO_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle OAuth callback from Yahoo"""
    error = request.args.get('error')
    if error:
        return redirect(f"/?error={error}")

    code = request.args.get('code')
    if not code:
        return redirect("/?error=No authorization code received")

    # Exchange code for tokens
    try:
        token_data = {
            'client_id': YAHOO_CLIENT_ID,
            'client_secret': YAHOO_CLIENT_SECRET,
            'redirect_uri': CALLBACK_URL,
            'code': code,
            'grant_type': 'authorization_code'
        }

        response = requests.post(YAHOO_TOKEN_URL, data=token_data)
        tokens = response.json()

        if 'access_token' not in tokens:
            return redirect(f"/?error=Failed to get access token: {tokens.get('error', 'Unknown error')}")

        # Create unique session ID for this user
        session_id = secrets.token_hex(16)
        session['session_id'] = session_id
        session['access_token'] = tokens['access_token']
        session['refresh_token'] = tokens.get('refresh_token')
        session['token_time'] = time.time()

        # Create session directory and save oauth2.json there
        session_dir = get_session_dir(session_id)
        oauth_data = {
            'access_token': tokens['access_token'],
            'refresh_token': tokens.get('refresh_token', ''),
            'token_type': tokens.get('token_type', 'bearer'),
            'token_time': time.time(),
            'consumer_key': YAHOO_CLIENT_ID,
            'consumer_secret': YAHOO_CLIENT_SECRET
        }
        with open(os.path.join(session_dir, 'oauth2.json'), 'w') as f:
            json.dump(oauth_data, f)

        return redirect('/leagues')

    except Exception as e:
        return redirect(f"/?error={str(e)}")


@app.route('/leagues')
def leagues():
    """Show user's leagues"""
    if 'access_token' not in session or 'session_id' not in session:
        return redirect('/login')

    try:
        # Use yahoo_fantasy_api to get leagues
        from yahoo_oauth import OAuth2
        import yahoo_fantasy_api as yfa

        session_dir = get_session_dir(session['session_id'])
        oauth_file = os.path.join(session_dir, 'oauth2.json')
        sc = OAuth2(None, None, from_file=oauth_file)
        gm = yfa.Game(sc, 'nfl')

        # Get leagues for current season
        league_ids = gm.league_ids(year=2025)

        leagues_list = []
        for lid in league_ids[:10]:  # Limit to 10 leagues
            try:
                lg = gm.to_league(lid)
                settings = lg.settings()
                leagues_list.append({
                    'league_id': lid.split('.l.')[-1],
                    'name': settings.get('name', 'Unknown League'),
                    'num_teams': settings.get('num_teams', '?'),
                    'season': '2025'
                })
            except:
                continue

        return render_template_string(LEAGUE_SELECT_HTML, leagues=leagues_list)

    except Exception as e:
        return redirect(f"/?error=Failed to fetch leagues: {str(e)}")


@app.route('/generate/<league_id>')
def generate(league_id):
    """Start generation job and redirect to status page"""
    if 'access_token' not in session or 'session_id' not in session:
        return redirect('/login')

    session_id = session['session_id']
    job_id = secrets.token_hex(8)
    generation_jobs[job_id] = {
        'status': 'starting',
        'league_id': league_id,
        'session_id': session_id,
        'message': 'Starting generation...'
    }

    # Start generation in background thread
    thread = threading.Thread(target=run_generation, args=(job_id, league_id, session_id))
    thread.start()

    # Redirect to status page with job_id in URL (survives refresh)
    return redirect(f'/generating/{job_id}')


@app.route('/generating/<job_id>')
def generating(job_id):
    """Show generation progress page"""
    job = generation_jobs.get(job_id)
    if not job:
        return redirect('/leagues')
    return render_template_string(GENERATING_HTML, job_id=job_id)


@app.route('/status/<job_id>')
def status(job_id):
    """Get job status"""
    job = generation_jobs.get(job_id, {'status': 'unknown'})
    return json.dumps(job)


@app.route('/view/<session_id>/<league_id>')
def view(session_id, league_id):
    """View generated league page"""
    session_dir = get_session_dir(session_id)
    output_file = os.path.join(session_dir, f'league_{league_id}_page.html')
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            return f.read()
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fantasy Reckoning - Not Found</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'EB Garamond', serif; background: #252a34; color: #e8d5b5; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; margin: 0; }
            h1 { font-family: 'Pirata One', cursive; font-size: 2.5rem; margin-bottom: 1rem; }
            .container { background: rgba(61, 68, 80, 0.5); padding: 2rem; border-radius: 8px; border: 1px solid rgba(232, 213, 181, 0.2); text-align: center; max-width: 500px; }
            a { color: #b8864f; }
            .btn { display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; background: #b8864f; color: #e8d5b5; text-decoration: none; border: none; }
        </style>
    </head>
    <body>
        <h1>Page Not Found</h1>
        <div class="container">
            <p>This league page doesn't exist or has expired.</p>
            <a href="/" class="btn">Generate Again</a>
        </div>
    </body>
    </html>
    """, 404


@app.route('/my-leagues')
def my_leagues():
    """Show completed generations for current session"""
    if 'session_id' not in session:
        return redirect('/login')

    session_id = session['session_id']
    session_dir = get_session_dir(session_id)

    # Find all completed league pages
    completed = []
    for f in glob.glob(os.path.join(session_dir, 'league_*_page.html')):
        league_id = os.path.basename(f).replace('league_', '').replace('_page.html', '')
        completed.append({
            'league_id': league_id,
            'url': f'/view/{session_id}/{league_id}',
            'generated': datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
        })

    if not completed:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fantasy Reckoning - My Leagues</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'EB Garamond', serif; background: #252a34; color: #e8d5b5; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; margin: 0; }
                h1 { font-family: 'Pirata One', cursive; font-size: 2.5rem; margin-bottom: 1rem; }
                .container { background: rgba(61, 68, 80, 0.5); padding: 2rem; border-radius: 8px; border: 1px solid rgba(232, 213, 181, 0.2); text-align: center; max-width: 500px; }
                a { color: #b8864f; }
                .btn { display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; background: #b8864f; color: #e8d5b5; text-decoration: none; border: none; }
            </style>
        </head>
        <body>
            <h1>My Leagues</h1>
            <div class="container">
                <p>No completed generations yet.</p>
                <a href="/leagues" class="btn">Generate a League</a>
            </div>
        </body>
        </html>
        """

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Generated Leagues</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=EB+Garamond:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'EB Garamond', serif; background: #252a34; color: #e8d5b5; padding: 2rem; }
            h1 { font-family: 'Pirata One', cursive; }
            .league { padding: 1rem; border-bottom: 1px solid rgba(232,213,181,0.2); }
            a { color: #b8864f; }
        </style>
    </head>
    <body>
        <h1>Your Generated Leagues</h1>
    """
    for league in completed:
        html += f'<div class="league"><a href="{league["url"]}">League {league["league_id"]}</a> - Generated {league["generated"]}</div>'
    html += '<p style="margin-top:2rem"><a href="/leagues">Generate another league</a></p></body></html>'
    return html


def run_generation(job_id, league_id, session_id):
    """Background job to generate cards"""
    import subprocess

    try:
        session_dir = get_session_dir(session_id)

        # Step 1: Pull data
        generation_jobs[job_id]['message'] = 'Pulling data from Yahoo...'
        generation_jobs[job_id]['status'] = 'pulling'

        league_file = os.path.join(session_dir, f'league_{league_id}_2025.json')

        # Write .env to session directory
        env_file = os.path.join(session_dir, '.env')
        env_content = f"""YAHOO_CLIENT_ID={YAHOO_CLIENT_ID}
YAHOO_CLIENT_SECRET={YAHOO_CLIENT_SECRET}
LEAGUE_ID={league_id}
SEASON_YEAR=2025
"""
        with open(env_file, 'w') as f:
            f.write(env_content)

        # Run data puller with --work-dir argument (can take 5-7 minutes for large leagues)
        result = subprocess.run(['python3', 'data_puller.py', '--work-dir', session_dir],
                              capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            generation_jobs[job_id] = {'status': 'error', 'error': result.stderr[:200]}
            return

        # Step 2: Calculate metrics
        generation_jobs[job_id]['message'] = 'Calculating metrics...'
        generation_jobs[job_id]['status'] = 'calculating'

        result = subprocess.run(['python3', 'fantasy_wrapped_calculator.py', '--data', league_file, '--work-dir', session_dir],
                              capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            generation_jobs[job_id] = {'status': 'error', 'error': result.stderr[:200]}
            return

        # Step 3: Generate HTML
        generation_jobs[job_id]['message'] = 'Building your cards...'
        generation_jobs[job_id]['status'] = 'building'

        from html_generator import generate_league_html

        with open(league_file, 'r') as f:
            league_data = json.load(f)

        team_map = {t.get('manager_name'): t.get('team_name')
                   for t in league_data.get('teams', [])
                   if t.get('manager_name') and t.get('team_name')}

        card_files = sorted(glob.glob(os.path.join(session_dir, 'fantasy_wrapped_*.json')))
        managers_data = [json.load(open(f)) for f in card_files]

        html = generate_league_html(
            league_data['league']['name'],
            league_id,
            '2025',
            managers_data,
            team_map
        )

        output_file = os.path.join(session_dir, f'league_{league_id}_page.html')
        with open(output_file, 'w') as f:
            f.write(html)

        generation_jobs[job_id] = {
            'status': 'complete',
            'league_id': league_id,
            'session_id': session_id,
            'message': 'Done!'
        }

    except Exception as e:
        generation_jobs[job_id] = {'status': 'error', 'error': str(e)}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    is_production = os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT')

    print("\n" + "="*60)
    print("Fantasy Reckoning - Web App")
    print("="*60)
    print(f"\nCallback URL: {CALLBACK_URL}")
    print("\nMake sure this callback URL is registered in your Yahoo app!")
    print(f"\nOpen {BASE_URL} in your browser")
    if not is_production:
        print("\n(You may need to accept the self-signed certificate warning)")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    if is_production:
        # Production: no SSL (handled by platform), no debug
        app.run(host='0.0.0.0', port=port)
    else:
        # Local development: use self-signed SSL
        app.run(debug=True, port=port, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
