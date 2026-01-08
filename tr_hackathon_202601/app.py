from flask import Flask, render_template, jsonify, request, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'taskrabbit_secret_key'


# --- Database Setup (SQL) ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Create Table: User Progress
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, carrots INTEGER, position INTEGER, energy INTEGER)''')
    # Create Table: Board Nodes (SF Neighborhoods)
    c.execute('''CREATE TABLE IF NOT EXISTS board 
                 (id INTEGER PRIMARY KEY, name TEXT, type TEXT, description TEXT)''')

    # Seed the Board with SF Locations if empty
    c.execute('SELECT count(*) FROM board')
    if c.fetchone()[0] == 0:
        neighborhoods = [
            (0, 'Start: TaskRabbit HQ', 'start', 'Welcome to the hustle!'),
            (1, 'SoMa', 'task', 'Tech startup needs office cleaning.'),
            (2, 'Mission District', 'chance', 'Burrito break! Gain 5 energy.'),
            (3, 'Castro', 'task', 'Help move a couch up 3 flights of stairs.'),
            (4, 'Painted Ladies', 'landmark', 'Badge Unlocked: Full House!'),
            (5, 'Marina', 'task', 'Mount a TV for a client.'),
            (6, 'Golden Gate Park', 'chance', 'Fog rolls in. Lose a turn.'),
            (7, 'Presidio', 'task', 'Assemble a complicated bookshelf.'),
            (8, 'Fisherman\'s Wharf', 'prize', 'Grand Prize: Tasker for Life!')
        ]
        c.executemany('INSERT INTO board VALUES (?,?,?,?)', neighborhoods)

        # Create a default user
        c.execute("INSERT INTO users (name, carrots, position, energy) VALUES ('Player1', 0, 0, 5)")

    conn.commit()
    conn.close()


# --- Routes ---

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get user state (simplified for single player demo)
    user = c.execute('SELECT * FROM users WHERE id=1').fetchone()

    # Get board
    board = c.execute('SELECT * FROM board ORDER BY id').fetchall()
    conn.close()

    return render_template('game.html', user=user, board=board)


@app.route('/roll', methods=['POST'])
def roll_dice():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch user
    c.execute('SELECT * FROM users WHERE id=1')
    user = c.fetchone()
    current_pos = user[3]  # position column
    energy = user[4]  # energy column

    if energy <= 0:
        return jsonify({'status': 'error', 'message': 'Out of Energy! Complete real tasks to recharge.'})

    # Game Logic
    roll = random.randint(1, 2)  # Small moves for this small board
    new_pos = min(current_pos + roll, 8)  # Max board size is 8

    # Fetch Tile Info
    c.execute('SELECT * FROM board WHERE id=?', (new_pos,))
    tile = c.fetchone()

    # Update Stats
    new_energy = energy - 1
    new_carrots = user[2]
    message = f"Rolled a {roll}! Landed in {tile[1]}."

    if tile[2] == 'task':
        new_carrots += 50
        message += " Task Completed! +50 Carrots."
    elif tile[2] == 'prize':
        message += " YOU WIN THE GRAND PRIZE!"

    c.execute('UPDATE users SET position=?, energy=?, carrots=? WHERE id=1',
              (new_pos, new_energy, new_carrots))
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'new_pos': new_pos,
        'roll': roll,
        'carrots': new_carrots,
        'energy': new_energy,
        'message': message
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)