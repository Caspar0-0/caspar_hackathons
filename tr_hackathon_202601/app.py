"""
TaskRabbit Merrython Game - Flask Application
=============================================
Backend server with Snowflake integration for:
- User scores and leaderboard
- Prize lottery system
- Game event tracking
- User funnel analytics
"""

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import os
import random
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Snowflake module
import snowflake_db

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'tr_holiday_hackathon_2026')

# ============================================
# PRIZE CONFIGURATION
# ============================================

PRIZES = [
    {
        'name': 'GRAND PRIZE',
        'description': 'Free Tasks for a Year!',
        'icon': '🏆',
        'probability': 0.0001  # 0.01%
    },
    {
        'name': '$25 TaskRabbit Coupon',
        'description': '$25 Off Your Next Task',
        'icon': '💵',
        'probability': 0.05  # 5%
    },
    {
        'name': '$15 TaskRabbit Coupon',
        'description': '$15 Off Your Next Task',
        'icon': '💳',
        'probability': 0.15  # 15%
    },
    {
        'name': 'Daily Boost',
        'description': '2x Earnings for 24 Hours',
        'icon': '☕',
        'probability': 0.20  # 20%
    },
    {
        'name': '$5 TaskRabbit Coupon',
        'description': '$5 Off Your Next Task',
        'icon': '🎫',
        'probability': 0.30  # 30%
    },
    {
        'name': 'Consolation Prize',
        'description': 'TaskRabbit Stickers',
        'icon': '🥕',
        'probability': 0.2999  # 29.99%
    }
]

def draw_prize():
    """Draw a random prize based on probability"""
    rand = random.random()
    cumulative = 0
    
    for prize in PRIZES:
        cumulative += prize['probability']
        if rand <= cumulative:
            return prize
    
    return PRIZES[-1]  # Fallback to consolation prize

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_session_id():
    """Get or create a unique session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def parse_user_agent(user_agent):
    """Parse user agent to extract device and browser info"""
    device_type = 'desktop'
    browser = 'unknown'
    
    ua_lower = user_agent.lower()
    
    # Detect device type
    if 'mobile' in ua_lower or 'android' in ua_lower:
        device_type = 'mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        device_type = 'tablet'
    
    # Detect browser
    if 'chrome' in ua_lower and 'edg' not in ua_lower:
        browser = 'Chrome'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = 'Safari'
    elif 'edg' in ua_lower:
        browser = 'Edge'
    
    return device_type, browser

# ============================================
# PAGE ROUTES
# ============================================

@app.route('/')
def landing():
    """Landing page - track funnel event"""
    session_id = get_session_id()
    player_name = session.get('username', 'Anonymous')
    
    # Track funnel event
    try:
        user_agent = request.headers.get('User-Agent', '')
        device_type, browser = parse_user_agent(user_agent)
        
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=player_name,
            funnel_stage='landing_page',
            page_url=request.url,
            referrer=request.referrer or '',
            user_agent=user_agent,
            device_type=device_type,
            browser=browser
        )
    except Exception as e:
        print(f"Warning: Could not save funnel event: {e}")
    
    return render_template('landing.html')

@app.route('/play')
def play():
    """Game page"""
    session_id = get_session_id()
    player_name = session.get('username', 'Anonymous')
    
    # Track funnel event
    try:
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=player_name,
            funnel_stage='game_start',
            page_url=request.url
        )
    except Exception as e:
        print(f"Warning: Could not save funnel event: {e}")
    
    return render_template('game.html')

@app.route('/lottery')
def lottery():
    """Lottery prize draw page"""
    session_id = get_session_id()
    score = session.get('last_score', 0)
    username = session.get('username', 'Anonymous')
    
    # Draw a prize
    prize = draw_prize()
    
    # Save prize to Snowflake
    try:
        snowflake_db.save_prize(
            session_id=session_id,
            player_name=username,
            score=score,
            prize=prize
        )
        
        # Track funnel event
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=username,
            funnel_stage='lottery_view',
            page_url=request.url
        )
    except Exception as e:
        print(f"Warning: Could not save to Snowflake: {e}")
    
    return render_template('lottery.html', score=score, prize_data=prize)

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard page - shows real player data from Snowflake"""
    username = session.get('username', 'Anonymous')
    
    try:
        # Get top scores from Snowflake - real data, real names
        scores = snowflake_db.get_top_scores(limit=10)
        
        # Get current user's best score and rank
        user_best = snowflake_db.get_player_best_score(username)
        user_rank = snowflake_db.get_player_rank(username)
        
    except Exception as e:
        print(f"Warning: Could not fetch from Snowflake: {e}")
        scores = []
        user_best = 0
        user_rank = None
    
    return render_template('leaderboard.html', 
                         scores=scores, 
                         user_best=user_best, 
                         user_rank=user_rank,
                         current_username=username)

# ============================================
# API ROUTES
# ============================================

@app.route('/set_username', methods=['POST'])
def set_username():
    """Set the player's username"""
    data = request.json
    username = data.get('username', 'Anonymous')
    session['username'] = username
    
    session_id = get_session_id()
    
    # Track funnel event
    try:
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=username,
            funnel_stage='enter_name',
            page_url=request.referrer or ''
        )
    except Exception as e:
        print(f"Warning: Could not save funnel event: {e}")
    
    return jsonify({'status': 'success', 'session_id': session_id})

@app.route('/save_score', methods=['POST'])
def save_score():
    """Save game score to Snowflake"""
    data = request.json
    score = data.get('score', 0)
    game_duration = data.get('game_duration', 0)
    items_collected = data.get('items_collected', 0)
    obstacles_hit = data.get('obstacles_hit', 0)
    
    session_id = get_session_id()
    username = session.get('username', 'Anonymous')
    
    # Store score in session for lottery page
    session['last_score'] = score
    
    # Save to Snowflake
    try:
        snowflake_db.save_score(
            session_id=session_id,
            player_name=username,
            score=score,
            game_duration=game_duration,
            items_collected=items_collected,
            obstacles_hit=obstacles_hit
        )
        
        # Track funnel event
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=username,
            funnel_stage='game_end',
            page_url=request.referrer or ''
        )
    except Exception as e:
        print(f"Warning: Could not save score to Snowflake: {e}")
    
    return jsonify({'status': 'saved', 'redirect': '/lottery'})

@app.route('/track_event', methods=['POST'])
def track_event():
    """Track a game event (collection, crash, jump, etc.)"""
    data = request.json
    
    session_id = get_session_id()
    username = session.get('username', 'Anonymous')
    
    try:
        snowflake_db.save_game_event(
            session_id=session_id,
            player_name=username,
            event_type=data.get('event_type', 'unknown'),
            event_data=data.get('event_data', {}),
            game_time_ms=data.get('game_time_ms', 0),
            score_at_event=data.get('score', 0),
            position_x=data.get('position_x', 0),
            position_z=data.get('position_z', 0)
        )
    except Exception as e:
        print(f"Warning: Could not save game event: {e}")
    
    return jsonify({'status': 'tracked'})

@app.route('/track_events_batch', methods=['POST'])
def track_events_batch():
    """Track multiple game events in a batch"""
    data = request.json
    events = data.get('events', [])
    
    session_id = get_session_id()
    username = session.get('username', 'Anonymous')
    
    # Add session info to each event
    for event in events:
        event['session_id'] = session_id
        event['player_name'] = username
    
    try:
        snowflake_db.save_game_events_batch(events)
    except Exception as e:
        print(f"Warning: Could not save game events batch: {e}")
    
    return jsonify({'status': 'tracked', 'count': len(events)})

@app.route('/track_funnel', methods=['POST'])
def track_funnel():
    """Track a funnel event"""
    data = request.json
    
    session_id = get_session_id()
    username = session.get('username', 'Anonymous')
    
    user_agent = request.headers.get('User-Agent', '')
    device_type, browser = parse_user_agent(user_agent)
    
    try:
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=username,
            funnel_stage=data.get('stage', 'unknown'),
            page_url=data.get('page_url', ''),
            referrer=data.get('referrer', ''),
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            time_on_stage_ms=data.get('time_on_stage_ms', 0)
        )
    except Exception as e:
        print(f"Warning: Could not save funnel event: {e}")
    
    return jsonify({'status': 'tracked'})

@app.route('/track_share', methods=['POST'])
def track_share():
    """Track social share event"""
    data = request.json
    
    session_id = get_session_id()
    username = session.get('username', 'Anonymous')
    
    try:
        snowflake_db.save_funnel_event(
            session_id=session_id,
            player_name=username,
            funnel_stage='social_share',
            page_url=request.referrer or ''
        )
        
        # Also save as game event with more detail
        snowflake_db.save_game_event(
            session_id=session_id,
            player_name=username,
            event_type='social_share',
            event_data={
                'platform': data.get('platform', 'unknown'),
                'prize_won': data.get('prize_won', ''),
                'score': data.get('score', 0)
            }
        )
    except Exception as e:
        print(f"Warning: Could not save share event: {e}")
    
    return jsonify({'status': 'tracked'})

# ============================================
# ANALYTICS API (for dashboards)
# ============================================

@app.route('/api/stats/daily')
def api_daily_stats():
    """Get daily game statistics"""
    try:
        stats = snowflake_db.get_daily_stats(days=7)
        return jsonify({'status': 'success', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stats/prizes')
def api_prize_stats():
    """Get prize distribution statistics"""
    try:
        stats = snowflake_db.get_prize_stats()
        return jsonify({'status': 'success', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stats/funnel')
def api_funnel_stats():
    """Get funnel conversion statistics"""
    try:
        stats = snowflake_db.get_funnel_stats()
        return jsonify({'status': 'success', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stats/hourly')
def api_hourly_stats():
    """Get hourly activity patterns"""
    try:
        stats = snowflake_db.get_hourly_activity()
        return jsonify({'status': 'success', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stats/items')
def api_item_stats():
    """Get item collection statistics"""
    try:
        stats = snowflake_db.get_item_collection_stats()
        return jsonify({'status': 'success', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/health')
def health():
    """Health check endpoint"""
    snowflake_connected = False
    try:
        snowflake_connected = snowflake_db.test_connection()
    except:
        pass
    
    return jsonify({
        'status': 'healthy',
        'snowflake_connected': snowflake_connected,
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    # Initialize Snowflake tables on startup
    print("🚀 Starting TaskRabbit Merrython Game Server...")
    
    try:
        # Validate Snowflake config
        if not snowflake_db.validate_config():
            print("⚠️  Snowflake config incomplete - running in local mode")
            print("⚠️  Data will not be persisted. Set up .env file to enable Snowflake.")
        else:
            print("📊 Testing Snowflake connection...")
            if snowflake_db.test_connection():
                print("📊 Initializing Snowflake tables...")
                snowflake_db.init_tables()
            else:
                print("⚠️  Snowflake not connected - running in local mode")
    except Exception as e:
        print(f"⚠️  Snowflake initialization failed: {e}")
        print("⚠️  Running without Snowflake - data will not be persisted")
    
    app.run(debug=True, port=5001)
