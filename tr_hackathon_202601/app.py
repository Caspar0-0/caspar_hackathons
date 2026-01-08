from flask import Flask, render_template, jsonify, request, session
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = 'tr_holiday_hackathon'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'game.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores 
                 (id INTEGER PRIMARY KEY, player_name TEXT, score INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS prizes 
                 (id INTEGER PRIMARY KEY, player_name TEXT, score INTEGER, 
                  prize_name TEXT, prize_description TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def draw_prize():
    """Draw a random prize based on probability"""
    prizes = [
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
    
    # Random draw weighted by probability
    rand = random.random()
    cumulative = 0
    
    for prize in prizes:
        cumulative += prize['probability']
        if rand <= cumulative:
            return prize
    
    # Fallback to consolation prize
    return prizes[-1]

# --- ROUTES ---

@app.route('/')
def landing():
    """The Starbucks-style Landing Page"""
    return render_template('landing.html')

@app.route('/play')
def play():
    """The Actual Game"""
    return render_template('game.html')

@app.route('/set_username', methods=['POST'])
def set_username():
    data = request.json
    username = data.get('username', 'Anonymous')
    session['username'] = username
    return jsonify({'status': 'success'})

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.json
    score = data.get('score', 0)
    
    # Get username from session or default
    username = session.get('username', 'Anonymous')
    
    # Store score in session for lottery page
    session['last_score'] = score
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO scores (player_name, score) VALUES (?, ?)", (username, score))
    conn.commit()
    conn.close()
    return jsonify({'status': 'saved', 'redirect': '/lottery'})

@app.route('/lottery')
def lottery():
    """Lottery Prize Draw Page"""
    score = session.get('last_score', 0)
    
    # Draw a prize
    prize = draw_prize()
    
    # Get username
    username = session.get('username', 'Anonymous')
    
    # Save prize to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO prizes (player_name, score, prize_name, prize_description) VALUES (?, ?, ?, ?)",
              (username, score, prize['name'], prize['description']))
    conn.commit()
    conn.close()
    
    return render_template('lottery.html', score=score, prize_data=prize)

def generate_random_name():
    """Generate a random realistic player name"""
    first_names = [
        'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn',
        'Jamie', 'Skylar', 'Dakota', 'Cameron', 'Drew', 'Blake', 'Reese', 'Sage',
        'Charlie', 'Emerson', 'Finley', 'Hayden', 'Jesse', 'Kendall', 'Logan', 'Parker',
        'Sam', 'Ryan', 'Tyler', 'Dylan', 'Chris', 'Pat', 'Robin', 'Ash'
    ]
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
        'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
        'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker'
    ]
    
    import random as rand
    first = rand.choice(first_names)
    last_initial = rand.choice(last_names)[0]
    return f"{first} {last_initial}."

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard Page"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get top 10 scores
    c.execute("SELECT id, player_name, score FROM scores ORDER BY score DESC LIMIT 10")
    raw_scores = c.fetchall()
    
    # Replace names with random names, but keep track of current user
    username = session.get('username', 'Anonymous')
    scores = []
    for score in raw_scores:
        if score[1] == username:
            # Keep current user's actual name
            scores.append(score)
        else:
            # Replace with random name
            scores.append((score[0], generate_random_name(), score[2]))
    
    # Get current user's best score and rank
    c.execute("SELECT MAX(score) FROM scores WHERE player_name = ?", (username,))
    user_best_result = c.fetchone()
    user_best = user_best_result[0] if user_best_result[0] else 0
    
    c.execute("SELECT COUNT(*) FROM (SELECT DISTINCT player_name, MAX(score) as max_score FROM scores GROUP BY player_name HAVING max_score > ?)", (user_best,))
    user_rank = c.fetchone()[0] + 1 if user_best > 0 else None
    
    conn.close()
    
    return render_template('leaderboard.html', 
                         scores=scores, 
                         user_best=user_best, 
                         user_rank=user_rank,
                         current_username=username)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)