"""
Snowflake Database Integration for TaskRabbit Merrython Game
============================================================
This module handles all Snowflake database operations including:
- User scores
- Prize draws
- Game events (collections, crashes, jumps)
- User funnel tracking
"""

import os
import snowflake.connector
from datetime import datetime
from contextlib import contextmanager

# ============================================
# CONFIGURATION - Load from environment variables
# ============================================
# All credentials must be set in .env file - no defaults for sensitive data

SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),         # Required: e.g., 'MX08059-TASKRABBIT'
    'user': os.getenv('SNOWFLAKE_USER'),               # Required: e.g., 'USER@TASKRABBIT.COM'
    'authenticator': 'externalbrowser',                 # SSO via browser (Okta/SAML)
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),     # Required: e.g., 'DATA_ANALYST_WAREHOUSE'
    'database': os.getenv('SNOWFLAKE_DATABASE'),       # Required: e.g., 'DEV'
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'MERRYTHON_GAME'),  # Default schema name is OK
    'role': os.getenv('SNOWFLAKE_ROLE'),               # Required: e.g., 'DATA_ENGINEER'
}

def validate_config():
    """Validate that all required config values are set"""
    required = ['account', 'user', 'warehouse', 'database', 'role']
    missing = [key for key in required if not SNOWFLAKE_CONFIG.get(key)]
    
    if missing:
        print("❌ Missing required environment variables:")
        for key in missing:
            print(f"   - SNOWFLAKE_{key.upper()}")
        print("\n   Please set them in your .env file. See env.example for reference.")
        return False
    return True

# ============================================
# CONNECTION MANAGEMENT
# ============================================

@contextmanager
def get_connection():
    """Context manager for Snowflake connections using SSO"""
    conn = None
    try:
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_CONFIG['account'],
            user=SNOWFLAKE_CONFIG['user'],
            authenticator=SNOWFLAKE_CONFIG['authenticator'],  # SSO via browser
            warehouse=SNOWFLAKE_CONFIG['warehouse'],
            database=SNOWFLAKE_CONFIG['database'],
            schema=SNOWFLAKE_CONFIG['schema'],
            role=SNOWFLAKE_CONFIG['role']
        )
        yield conn
    finally:
        if conn:
            conn.close()

def test_connection():
    """Test Snowflake connection"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            print(f"✅ Connected to Snowflake version: {version}")
            return True
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        return False

# ============================================
# SCHEMA AND TABLE INITIALIZATION
# ============================================

def init_schema():
    """Create the schema if it doesn't exist"""
    with get_connection() as conn:
        cursor = conn.cursor()
        schema_name = SNOWFLAKE_CONFIG['schema']
        
        try:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            cursor.execute(f"USE SCHEMA {schema_name}")
            print(f"✅ Schema '{schema_name}' ready")
            conn.commit()
        except Exception as e:
            print(f"⚠️  Schema creation: {e}")

def init_tables():
    """Create all necessary tables in Snowflake"""
    
    # First ensure schema exists
    init_schema()
    
    create_statements = [
        # Scores table - stores final game scores
        """
        CREATE TABLE IF NOT EXISTS GAME_SCORES (
            ID NUMBER AUTOINCREMENT PRIMARY KEY,
            SESSION_ID VARCHAR(64),
            PLAYER_NAME VARCHAR(100),
            SCORE NUMBER,
            GAME_DURATION_SECONDS NUMBER,
            ITEMS_COLLECTED NUMBER,
            OBSTACLES_HIT NUMBER,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """,
        
        # Prizes table - stores lottery results
        """
        CREATE TABLE IF NOT EXISTS GAME_PRIZES (
            ID NUMBER AUTOINCREMENT PRIMARY KEY,
            SESSION_ID VARCHAR(64),
            PLAYER_NAME VARCHAR(100),
            SCORE NUMBER,
            PRIZE_NAME VARCHAR(100),
            PRIZE_DESCRIPTION VARCHAR(500),
            PRIZE_ICON VARCHAR(10),
            PRIZE_PROBABILITY FLOAT,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """,
        
        # Game events table - detailed event tracking
        """
        CREATE TABLE IF NOT EXISTS GAME_EVENTS (
            ID NUMBER AUTOINCREMENT PRIMARY KEY,
            SESSION_ID VARCHAR(64),
            PLAYER_NAME VARCHAR(100),
            EVENT_TYPE VARCHAR(50),
            EVENT_DATA VARIANT,
            GAME_TIME_MS NUMBER,
            SCORE_AT_EVENT NUMBER,
            POSITION_X FLOAT,
            POSITION_Z FLOAT,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """,
        
        # Funnel events table - user journey tracking
        """
        CREATE TABLE IF NOT EXISTS FUNNEL_EVENTS (
            ID NUMBER AUTOINCREMENT PRIMARY KEY,
            SESSION_ID VARCHAR(64),
            PLAYER_NAME VARCHAR(100),
            FUNNEL_STAGE VARCHAR(50),
            PAGE_URL VARCHAR(500),
            REFERRER VARCHAR(500),
            USER_AGENT VARCHAR(1000),
            DEVICE_TYPE VARCHAR(50),
            BROWSER VARCHAR(100),
            TIME_ON_STAGE_MS NUMBER,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
    ]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        for statement in create_statements:
            try:
                cursor.execute(statement)
                print(f"✅ Table created/verified")
            except Exception as e:
                print(f"❌ Error creating table: {e}")
        conn.commit()
    
    print("✅ All tables initialized")

# ============================================
# SCORE OPERATIONS
# ============================================

def save_score(session_id, player_name, score, game_duration=0, items_collected=0, obstacles_hit=0):
    """Save a game score to Snowflake"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO GAME_SCORES 
            (SESSION_ID, PLAYER_NAME, SCORE, GAME_DURATION_SECONDS, ITEMS_COLLECTED, OBSTACLES_HIT)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session_id, player_name, score, game_duration, items_collected, obstacles_hit))
        conn.commit()
    return True

def get_top_scores(limit=10):
    """Get top scores for leaderboard"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID, PLAYER_NAME, SCORE, CREATED_AT
            FROM GAME_SCORES
            ORDER BY SCORE DESC
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()

def get_player_best_score(player_name):
    """Get a player's best score"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(SCORE) as BEST_SCORE
            FROM GAME_SCORES
            WHERE PLAYER_NAME = %s
        """, (player_name,))
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0

def get_player_rank(player_name):
    """Get a player's rank based on their best score"""
    best_score = get_player_best_score(player_name)
    if best_score == 0:
        return None
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT PLAYER_NAME) + 1 as RANK
            FROM (
                SELECT PLAYER_NAME, MAX(SCORE) as MAX_SCORE
                FROM GAME_SCORES
                GROUP BY PLAYER_NAME
                HAVING MAX_SCORE > %s
            )
        """, (best_score,))
        result = cursor.fetchone()
        return result[0] if result else 1

# ============================================
# PRIZE OPERATIONS
# ============================================

def save_prize(session_id, player_name, score, prize):
    """Save a prize draw result to Snowflake"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO GAME_PRIZES 
            (SESSION_ID, PLAYER_NAME, SCORE, PRIZE_NAME, PRIZE_DESCRIPTION, PRIZE_ICON, PRIZE_PROBABILITY)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session_id,
            player_name,
            score,
            prize['name'],
            prize['description'],
            prize['icon'],
            prize['probability']
        ))
        conn.commit()
    return True

def get_prize_stats():
    """Get prize distribution statistics"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                PRIZE_NAME,
                COUNT(*) as WIN_COUNT,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as WIN_PERCENTAGE
            FROM GAME_PRIZES
            GROUP BY PRIZE_NAME
            ORDER BY WIN_COUNT DESC
        """)
        return cursor.fetchall()

# ============================================
# GAME EVENT OPERATIONS
# ============================================

def save_game_event(session_id, player_name, event_type, event_data=None, 
                    game_time_ms=0, score_at_event=0, position_x=0, position_z=0):
    """Save a game event (collection, crash, jump, etc.)"""
    import json
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO GAME_EVENTS 
            (SESSION_ID, PLAYER_NAME, EVENT_TYPE, EVENT_DATA, GAME_TIME_MS, 
             SCORE_AT_EVENT, POSITION_X, POSITION_Z)
            VALUES (%s, %s, %s, PARSE_JSON(%s), %s, %s, %s, %s)
        """, (
            session_id,
            player_name,
            event_type,
            json.dumps(event_data) if event_data else '{}',
            game_time_ms,
            score_at_event,
            position_x,
            position_z
        ))
        conn.commit()
    return True

def save_game_events_batch(events):
    """Save multiple game events in a batch for efficiency"""
    import json
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Prepare batch data
        values = []
        for e in events:
            values.append((
                e.get('session_id'),
                e.get('player_name'),
                e.get('event_type'),
                json.dumps(e.get('event_data', {})),
                e.get('game_time_ms', 0),
                e.get('score_at_event', 0),
                e.get('position_x', 0),
                e.get('position_z', 0)
            ))
        
        cursor.executemany("""
            INSERT INTO GAME_EVENTS 
            (SESSION_ID, PLAYER_NAME, EVENT_TYPE, EVENT_DATA, GAME_TIME_MS, 
             SCORE_AT_EVENT, POSITION_X, POSITION_Z)
            VALUES (%s, %s, %s, PARSE_JSON(%s), %s, %s, %s, %s)
        """, values)
        conn.commit()
    return True

def get_event_stats(session_id=None):
    """Get event statistics, optionally filtered by session"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        where_clause = "WHERE SESSION_ID = %s" if session_id else ""
        params = (session_id,) if session_id else ()
        
        cursor.execute(f"""
            SELECT 
                EVENT_TYPE,
                COUNT(*) as EVENT_COUNT,
                AVG(SCORE_AT_EVENT) as AVG_SCORE
            FROM GAME_EVENTS
            {where_clause}
            GROUP BY EVENT_TYPE
            ORDER BY EVENT_COUNT DESC
        """, params)
        return cursor.fetchall()

# ============================================
# FUNNEL TRACKING OPERATIONS
# ============================================

def save_funnel_event(session_id, player_name, funnel_stage, page_url='', 
                      referrer='', user_agent='', device_type='', browser='', time_on_stage_ms=0):
    """Save a funnel event (page view, conversion step)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO FUNNEL_EVENTS 
            (SESSION_ID, PLAYER_NAME, FUNNEL_STAGE, PAGE_URL, REFERRER, 
             USER_AGENT, DEVICE_TYPE, BROWSER, TIME_ON_STAGE_MS)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session_id,
            player_name,
            funnel_stage,
            page_url,
            referrer,
            user_agent,
            device_type,
            browser,
            time_on_stage_ms
        ))
        conn.commit()
    return True

def get_funnel_stats():
    """Get funnel conversion statistics"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            WITH funnel_counts AS (
                SELECT 
                    FUNNEL_STAGE,
                    COUNT(DISTINCT SESSION_ID) as UNIQUE_SESSIONS
                FROM FUNNEL_EVENTS
                GROUP BY FUNNEL_STAGE
            ),
            total_sessions AS (
                SELECT COUNT(DISTINCT SESSION_ID) as TOTAL 
                FROM FUNNEL_EVENTS 
                WHERE FUNNEL_STAGE = 'landing_page'
            )
            SELECT 
                f.FUNNEL_STAGE,
                f.UNIQUE_SESSIONS,
                ROUND(f.UNIQUE_SESSIONS * 100.0 / NULLIF(t.TOTAL, 0), 2) as CONVERSION_RATE
            FROM funnel_counts f
            CROSS JOIN total_sessions t
            ORDER BY 
                CASE f.FUNNEL_STAGE
                    WHEN 'landing_page' THEN 1
                    WHEN 'enter_name' THEN 2
                    WHEN 'game_start' THEN 3
                    WHEN 'game_end' THEN 4
                    WHEN 'lottery_view' THEN 5
                    WHEN 'social_share' THEN 6
                    ELSE 99
                END
        """)
        return cursor.fetchall()

# ============================================
# ANALYTICS QUERIES
# ============================================

def get_daily_stats(days=7):
    """Get daily aggregated statistics"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                DATE(CREATED_AT) as GAME_DATE,
                COUNT(*) as GAMES_PLAYED,
                COUNT(DISTINCT PLAYER_NAME) as UNIQUE_PLAYERS,
                AVG(SCORE) as AVG_SCORE,
                MAX(SCORE) as HIGH_SCORE
            FROM GAME_SCORES
            WHERE CREATED_AT >= DATEADD(day, -%s, CURRENT_DATE())
            GROUP BY DATE(CREATED_AT)
            ORDER BY GAME_DATE DESC
        """, (days,))
        return cursor.fetchall()

def get_hourly_activity():
    """Get hourly activity patterns"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                HOUR(CREATED_AT) as HOUR_OF_DAY,
                COUNT(*) as GAMES_PLAYED,
                AVG(SCORE) as AVG_SCORE
            FROM GAME_SCORES
            GROUP BY HOUR(CREATED_AT)
            ORDER BY HOUR_OF_DAY
        """)
        return cursor.fetchall()

def get_item_collection_stats():
    """Get statistics on which items are collected most"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                EVENT_DATA:item_type::STRING as ITEM_TYPE,
                COUNT(*) as COLLECTION_COUNT,
                AVG(EVENT_DATA:points::NUMBER) as AVG_POINTS
            FROM GAME_EVENTS
            WHERE EVENT_TYPE = 'item_collected'
            GROUP BY EVENT_DATA:item_type::STRING
            ORDER BY COLLECTION_COUNT DESC
        """)
        return cursor.fetchall()


# ============================================
# MAIN - For testing
# ============================================

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    
    print("Testing Snowflake connection with SSO...")
    
    # Validate all required config is present
    if not validate_config():
        exit(1)
    
    print("🔐 Opening browser for SSO authentication...")
    if test_connection():
        print("\nInitializing tables...")
        init_tables()
