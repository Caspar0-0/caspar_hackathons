# 🐰 TaskRabbit Merrython Game

A Starbucks-style "Merrython" endless runner game featuring TaskRabbit branding, built for the TR Holiday Hackathon 2026.


## 🎮 Overview

Players control a cute TaskRabbit bunny running through San Francisco streets, collecting task items, tips, and TR Badges while avoiding obstacles. The game features:

- **3D Graphics** powered by Three.js
- **Real-time data tracking** via Snowflake integration
- **Lottery prize system** with weighted probabilities
- **Leaderboard** with real player data
- **TaskRabbit fun facts** displayed during gameplay

## ✨ Features

### Gameplay
- 🐰 Cute animated bunny character with TaskRabbit vest
- 🌉 San Francisco backdrop with glowing Golden Gate Bridge
- 💵 Collect dollars (+10 pts) - "I got some tip!"
- 🔧 Collect task items (+20 pts) - screwdriver, mop, IKEA box
- 🐰 Collect TR Badges (+50 pts) - premium collectible
- 🚧 Avoid traffic cones (-1 life)
- ❤️ 3-life system with invincibility frames
- 📊 Real TaskRabbit statistics shown as fun facts

### Data Engineering
- ❄️ **Snowflake Integration** - All game data stored in cloud data warehouse
- 📈 **Event Tracking** - Every game action tracked for analytics
- 🔄 **Funnel Analytics** - User journey from landing to social share
- 🏆 **Real Leaderboard** - Actual player names and scores
- 🔐 **SSO Authentication** - Secure browser-based Okta login

### Prize System
| Prize | Probability |
|-------|-------------|
| 🏆 Grand Prize (Free Tasks for a Year) | 0.01% |
| 💵 $25 TaskRabbit Coupon | 5% |
| 💳 $15 TaskRabbit Coupon | 15% |
| ☕ Daily Boost (2x Earnings) | 20% |
| 🎫 $5 TaskRabbit Coupon | 30% |
| 🥕 TaskRabbit Stickers | ~30% |

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML5, CSS3, JavaScript |
| 3D Engine | Three.js (r128) |
| Database | Snowflake |
| Authentication | SSO via Okta (externalbrowser) |
| Styling | Custom CSS with animations |

## 📁 Project Structure

```
tr_hackathon_202601/
├── app.py                 # Flask application & API routes
├── snowflake_db.py        # Snowflake database operations
├── requirements.txt       # Python dependencies
├── env.example            # Environment variables template
├── static/
│   ├── game.js            # Three.js game logic
│   ├── game.css           # Game page styles
│   ├── landing.css        # Landing page styles
│   ├── lottery.css        # Prize draw page styles
│   └── leaderboard.css    # Leaderboard styles
├── templates/
│   ├── landing.html       # Main landing page
│   ├── game.html          # Game page
│   ├── lottery.html       # Prize draw page
│   └── leaderboard.html   # Leaderboard page
└── DATA_ENGINEERING_IDEAS.md  # Future feature ideas
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Snowflake account with SSO access
- Modern web browser

### Installation

1. **Clone and navigate:**
   ```bash
   cd tr_hackathon_202601
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your Snowflake credentials:
   ```
   SNOWFLAKE_ACCOUNT
   SNOWFLAKE_USER
   SNOWFLAKE_WAREHOUSE
   SNOWFLAKE_DATABASE
   SNOWFLAKE_SCHEMA
   SNOWFLAKE_ROLE
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```
   
   A browser window will open for SSO authentication via Okta.

6. **Play the game:**
   Open [http://localhost:5001](http://localhost:5001)

## 📊 Snowflake Tables

The game creates the following tables in `DEV.MERRYTHON_GAME`:

### GAME_SCORES
```sql
- ID (autoincrement)
- SESSION_ID
- PLAYER_NAME
- SCORE
- GAME_DURATION_SECONDS
- ITEMS_COLLECTED
- OBSTACLES_HIT
- CREATED_AT
```

### GAME_PRIZES
```sql
- ID (autoincrement)
- SESSION_ID
- PLAYER_NAME
- SCORE
- PRIZE_NAME
- PRIZE_DESCRIPTION
- PRIZE_ICON
- PRIZE_PROBABILITY
- CREATED_AT
```

### GAME_EVENTS
```sql
- ID (autoincrement)
- SESSION_ID
- PLAYER_NAME
- EVENT_TYPE (item_collected, crash, jump, etc.)
- EVENT_DATA (VARIANT/JSON)
- GAME_TIME_MS
- SCORE_AT_EVENT
- POSITION_X, POSITION_Z
- CREATED_AT
```

### FUNNEL_EVENTS
```sql
- ID (autoincrement)
- SESSION_ID
- PLAYER_NAME
- FUNNEL_STAGE (landing_page, enter_name, game_start, game_end, lottery_view, social_share)
- PAGE_URL
- REFERRER
- USER_AGENT
- DEVICE_TYPE
- BROWSER
- TIME_ON_STAGE_MS
- CREATED_AT
```

## 🔌 API Endpoints

### Pages
| Route | Description |
|-------|-------------|
| `GET /` | Landing page |
| `GET /play` | Game page |
| `GET /lottery` | Prize draw page |
| `GET /leaderboard` | Leaderboard page |

### Game APIs
| Route | Method | Description |
|-------|--------|-------------|
| `/set_username` | POST | Set player name |
| `/save_score` | POST | Save game score |
| `/track_event` | POST | Track single game event |
| `/track_events_batch` | POST | Track multiple events |
| `/track_funnel` | POST | Track funnel stage |
| `/track_share` | POST | Track social share |

### Analytics APIs
| Route | Description |
|-------|-------------|
| `GET /api/stats/daily` | Daily game statistics |
| `GET /api/stats/prizes` | Prize distribution |
| `GET /api/stats/funnel` | Funnel conversion rates |
| `GET /api/stats/hourly` | Hourly activity patterns |
| `GET /api/stats/items` | Item collection stats |
| `GET /health` | Health check + Snowflake status |

## 🎯 Sample Queries

```sql
-- Top players today
SELECT PLAYER_NAME, MAX(SCORE) as HIGH_SCORE
FROM DEV.MERRYTHON_GAME.GAME_SCORES
WHERE DATE(CREATED_AT) = CURRENT_DATE()
GROUP BY PLAYER_NAME
ORDER BY HIGH_SCORE DESC
LIMIT 10;

-- Prize distribution
SELECT PRIZE_NAME, COUNT(*) as WINS,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as PCT
FROM DEV.MERRYTHON_GAME.GAME_PRIZES
GROUP BY PRIZE_NAME
ORDER BY WINS DESC;

-- Funnel conversion
SELECT FUNNEL_STAGE, COUNT(DISTINCT SESSION_ID) as USERS
FROM DEV.MERRYTHON_GAME.FUNNEL_EVENTS
GROUP BY FUNNEL_STAGE;

-- Most collected items
SELECT EVENT_DATA:item_type::STRING as ITEM, COUNT(*) as COLLECTIONS
FROM DEV.MERRYTHON_GAME.GAME_EVENTS
WHERE EVENT_TYPE = 'item_collected'
GROUP BY 1
ORDER BY 2 DESC;
```

## 🎨 Game Controls

| Control | Action |
|---------|--------|
| ← / A | Move left |
| → / D | Move right |
| ↑ / W / Space | Jump |
| 🔊 Button | Toggle music |

## 🏗 Future Ideas

See [DATA_ENGINEERING_IDEAS.md](DATA_ENGINEERING_IDEAS.md) for planned features:
- Real-time analytics dashboard
- A/B testing framework
- Demand forecasting display
- Task matching visualization
- Advanced leaderboard with percentiles

## 📝 Legal

- [TaskRabbit Terms](https://www.taskrabbit.com/terms)
- [Privacy Policy](https://support.taskrabbit.com/hc/en-us/articles/360035206832-Taskrabbit-Global-Privacy-Policy)

## 👨‍💻 Author

Built for TaskRabbit Holiday Hackathon 2026

---

*TaskRabbit - We Do Chores. You Live Life.* 🐰
