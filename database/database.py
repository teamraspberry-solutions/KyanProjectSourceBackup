import sqlite3
import os
from datetime import datetime

DB_PATH = "kyan_local.db"

class KyanDatabase:
    def __init__(self):
        """Initialize database connection and create tables if they don't exist."""
        os.makedirs("database", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        

    def create_tables(self):
        """Creates all necessary tables."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS focus_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                isFocused BOOLEAN NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS session (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                end_time TEXT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (DATE('now')),
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                sentimentRecorded TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS kyan_characteristic1 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                kyanDetails TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS kyan_characteristic2 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                kyanDetails TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS characteristic1_conversation_history (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (DATE('now')),
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                conversation TEXT NOT NULL,
                conversation_type TEXT NOT NULL,  -- 'user' or 'bot'
                user_id INTEGER DEFAULT 1  -- Placeholder for future user-specific tracking
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS characteristic2_conversation_history (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (DATE('now')),
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                conversation TEXT NOT NULL,
                conversation_type TEXT NOT NULL,  -- 'user' or 'bot'
                user_id INTEGER DEFAULT 1,  -- Placeholder for future user-specific tracking
                session_id INTEGER,  -- New column to link to session_id
                FOREIGN KEY (session_id) REFERENCES session(session_id)  -- Foreign key constraint
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS recapKyan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detail TEXT NOT NULL
            )
            """
        ]
        
        for query in queries:
            self.cursor.execute(query)
        self.conn.commit()
        

    def insert_user(self, name, age):
        """Inserts or updates the single user record."""
        self.cursor.execute(
            "INSERT INTO user (id, name, age) VALUES (1, ?, ?) ON CONFLICT(id) DO UPDATE SET name = excluded.name, age = excluded.age",
            (name, age),
        )
        self.conn.commit()

    def insert_focus_tracker(self, session_id, isFocused):
        """Records focus tracking data."""
        self.cursor.execute(
            "INSERT INTO focus_tracker (session_id, isFocused) VALUES (?, ?)",
            (session_id, isFocused),
        )
        self.conn.commit()

    def insert_session(self):
        """Starts a new study session and returns its session_id."""
        self.cursor.execute("INSERT INTO session (start_time) VALUES (CURRENT_TIMESTAMP)")
        self.conn.commit()
        return self.cursor.lastrowid

    def end_session(self):
        """Ends the last session by setting its end_time to the current timestamp."""
        self.cursor.execute("""
            UPDATE session 
            SET end_time = CURRENT_TIMESTAMP 
            WHERE session_id = (SELECT session_id FROM session ORDER BY session_id DESC LIMIT 1)
        """)
        self.conn.commit()


    def insert_sentiment(self, sentiment, timestamp):
        """Inserts sentiment data into the sentiment table."""
        self.cursor.execute(
            "INSERT INTO sentiment (sentimentRecorded, timestamp) VALUES (?, ?)",
            (sentiment, timestamp),
        )
        self.conn.commit()


    def insert_characteristic1_history(self, conversation, conversation_type, user_id):
        """Logs friendly mode conversation history with conversation type and user ID."""
        self.cursor.execute(
            "INSERT INTO characteristic1_conversation_history (conversation, conversation_type, user_id) VALUES (?, ?, ?)",
            (conversation, conversation_type, user_id)
        )
        self.conn.commit()


    def insert_characteristic2_history(self, conversation, conversation_type, user_id, session_id):
        """Logs friendly mode conversation history with conversation type, user ID, and session ID."""
        self.cursor.execute(
            "INSERT INTO characteristic2_conversation_history (conversation, conversation_type, user_id, session_id) VALUES (?, ?, ?, ?)",
            (conversation, conversation_type, user_id, session_id)
        )
        self.conn.commit()


    def get_user_info(self):
        """Fetches the user record."""
        self.cursor.execute("SELECT name, age FROM user WHERE id = 1")
        return self.cursor.fetchone()

    def get_characteristic(self, mode):
        """Fetches the bot's characteristic details based on the mode."""
        table = "kyan_characteristic1" if mode == 1 else "kyan_characteristic2"
        self.cursor.execute(f"SELECT kyanDetails FROM {table} WHERE id = 1")
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_recent_conversations(self, mode):
        """Fetches the most recent 10 messages from conversation history."""
        table = "characteristic1_conversation_history" if mode == 1 else "characteristic2_conversation_history"
        self.cursor.execute(
            f"SELECT conversation FROM {table} ORDER BY timestamp DESC LIMIT 10"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        """Closes the database connection."""
        self.conn.close()


    def get_last_conversation_in_timeframe(self, timestamp):
        """Fetches the most recent conversation within the given timeframe."""
        self.cursor.execute(
            "SELECT conversation FROM characteristic1_conversation_history WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 1",
            (timestamp,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_active_session_id(self):
        """Fetch the most recent session ID from the session table."""
        self.cursor.execute("SELECT session_id FROM session ORDER BY start_time DESC LIMIT 1")
        return self.cursor.fetchone()
    

    def get_last_completed_session_id(self):
        """Fetches the session ID of the last completed study session (excluding the current active one)."""
        self.cursor.execute("""
            SELECT session.session_id FROM session  -- Explicitly mention table name
            WHERE end_time IS NOT NULL
            ORDER BY end_time DESC
            LIMIT 1 OFFSET 1
        """)
        result = self.cursor.fetchone()
        return result[0] if result else None



    def get_characteristic2_conversation_history(self, session_id):
        """Fetches conversation history for a given study session ID."""
        self.cursor.execute("""
            SELECT conversation FROM characteristic2_conversation_history 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """, (session_id,))
        return [row[0] for row in self.cursor.fetchall()]


    def get_recap_details(self, session_id):
        """Fetches the recap details from recapKyan table for a given session ID."""
        self.cursor.execute("""
            SELECT detail FROM recapKyan 
            WHERE session_id = ?
        """, (session_id,))
        result = self.cursor.fetchone()
        return result[0] if result and result[0] else "No additional context available."