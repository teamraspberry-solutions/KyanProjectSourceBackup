import time
import threading
import psycopg2
import cv2
import sys
import mediapipe as mp
from backend.speech_processing import SpeechProcessor
from database.database import KyanDatabase
from backend.focus_tracker import FocusTracker
from backend.sentiment_analysis import SentimentAnalyzer
from backend.conversation_manager import ConversationManager
from backend.emotion_display import EmotionDisplay
from backend.utils import get_current_timestamp
from backend.error_handler import ErrorHandler
from backend.config import STANDBY_TIMEOUT, CLOUD_DB_HOST, CLOUD_DB_PORT, CLOUD_DB_NAME, CLOUD_DB_USER, CLOUD_DB_PASSWORD, SYNC_INTERVAL, SYNC_TABLES, LOCAL_DB_PATH
import sqlite3  # for SQLite connection

class KyanBot:
    def __init__(self):
        """Initialize the bot and its components."""
        self.db = KyanDatabase()
        self.speech = SpeechProcessor()
        self.focus_tracker = FocusTracker()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_manager = ConversationManager(self.db)
        self.error_handler = ErrorHandler()
        self.emotion_display = EmotionDisplay()

        self.characteristic_mode = 1  # Default: Friendly mode
        self.in_study_mode = False
        self.last_interaction_time = time.time()
        self.running = True
        self.standby_mode = False

        print("Kyan is starting...")

    def run(self):
        """Main loop for KyanBot."""
        print("Kyan is now active and listening...")
        while self.running:
            try:
                # Enter standby mode if no interaction for STANDBY_TIMEOUT seconds
                if time.time() - self.last_interaction_time > STANDBY_TIMEOUT:
                    self.enter_standby_mode()

                # Listen for user input
                user_input = self.speech.recognize_speech()
                if not user_input:
                    continue  # Skip iteration if no speech detected

                self.last_interaction_time = time.time()  # Reset standby timer

                # Process user input
                self.process_input(user_input)

            except Exception as e:
                self.error_handler.log_error(e)

    # def run_sentiment_analysis_loop(self):
    #         """Runs sentiment analysis every 60 seconds in Friendly Mode."""
    #         while self.running:
    #             if self.characteristic_mode == 1:  # Only run in Friendly Mode
    #                 self.sentiment_analyzer.periodic_sentiment_analysis()
    #             time.sleep(60)

    def update_emotion_display(self, emotion):
        """Transitions from live display to detected emotion smoothly."""
        self.emotion_display.transition_to_emotion(emotion)

    def enter_standby_mode(self):
        """Puts the bot in standby mode and listens for 'Hey Kyan'."""
        if not self.standby_mode:
            self.standby_mode = True
            print("Kyan is now in standby mode...")

        while self.standby_mode:
            wake_word = self.speech.recognize_speech()
            if wake_word and "hey" in wake_word.lower():
                self.standby_mode = False
                print("Kyan has been awakened!")
                self.speak("Hello there!")
                return


    def process_input(self, user_input):
        """Processes user input and determines the appropriate response."""
        print(f"User said: {user_input}")

        user_input_lower = user_input.lower()
        # Analyze sentiment right after getting user input
        sentiment = self.sentiment_analyzer.analyze_sentiment(user_input)
        self.sentiment_analyzer.save_sentiment_to_db(sentiment)

        # Wake-up phrase while in standby mode
        if self.standby_mode and "hey." in user_input_lower:
            self.standby_mode = False
            self.speak("Hello! How can I assist you?")
            return

        # Special Commands to Change Mode
        if "switch to friendly mode" in user_input_lower:
            self.characteristic_mode = 1
            self.speak("I am now in friendly mode! Let's chat.")
            return

        if "switch to study mode" in user_input_lower:
            self.characteristic_mode = 2
            self.speak("I am now in study mode. Let's focus!")
            return

        # Start Study Session
        if "start a study session" in user_input_lower or "let's study" in user_input_lower:
            self.start_study_session()
            return

        # End Study Session
        if "end the study session" in user_input_lower or "stop studying" in user_input_lower:
            self.end_study_session()
            return

        # Shutdown Command
        if "goodbye" in user_input_lower or "turn off" in user_input_lower:
            self.shutdown_bot()
            return

        # Process General Conversation
        response = self.generate_response(user_input)
        self.speak(response)


    def generate_response(self, user_input):
        """Generates a response using the chatbot and sentiment analysis."""
        user_name, user_age = self.db.get_user_info() or ("User", 0)
        bot_characteristic = self.db.get_characteristic(self.characteristic_mode)
        recent_messages = self.db.get_recent_conversations(self.characteristic_mode)

        context = f"{user_name}, Age: {user_age}\nMode: {bot_characteristic}\n"
        context += "Recent Conversations:\n" + "\n".join(recent_messages)

        response = self.speech.generate_chatbot_response(user_input, context)

        # Store both user input and bot response in temporary cache
        self.conversation_manager.add_conversation(
            conversation=user_input, 
            mode=self.characteristic_mode, 
            conversation_type='user', 
            user_id=1  # Assume user_id is 1 for this example
        )
        self.conversation_manager.add_conversation(
            conversation=response, 
            mode=self.characteristic_mode, 
            conversation_type='kyan', 
            user_id=1  # Assume user_id is 1 for this example
        )
        
        return response

    def start_study_session(self):
        """Activates study mode, enabling focus tracking and disabling sentiment analysis."""
        if self.in_study_mode:
            self.speak("You're already in a study session.")
            return

        self.in_study_mode = True
        self.characteristic_mode = 2
        session_id = self.db.insert_session()

        # Start focus tracking (runs every 30 sec)
        self.focus_tracker = FocusTracker()
        focus_thread = threading.Thread(target=self.focus_tracker.track_focus, args=(session_id,))
        focus_thread.daemon = True
        focus_thread.start()

        self.speak("Study session started. Stay focused!")

    def end_study_session(self):
        """Deactivates study mode and re-enables friendly mode."""
        if not self.in_study_mode:
            self.speak("No active study session found.")
            return
        
        self.in_study_mode = False
        self.characteristic_mode = 1
        self.db.end_session()  # Ends the most recent session

        if hasattr(self, "focus_tracker"):
            self.focus_tracker.stop()
            self.focus_thread.join()  # Ensure the thread stops properly

        self.speak("Study session ended. How else can I assist you?")

    def shutdown_bot(self):
        """Shuts down the bot safely and closes the emotion display."""
        self.running = False  # Stop main loop
        self.speak("Goodbye! Shutting down now.")
  
        # Stop emotion display properly
        cv2.destroyAllWindows()
        self.emotion_display.stop_display()  # Close the OpenCV window

        # Sync database before shutting down
        self.sync_to_cloud()

        print("Kyan has been turned off.")
        sys.exit(0)  # Force exit

    def speak(self, text):
        """Converts text to speech and speaks it."""
        print(f"Kyan says: {text}")
        self.speech.text_to_speech(text)

        self.last_interaction_time = time.time()




    def sync_to_cloud(self):
        """Sync local SQLite database to cloud PostgreSQL database with primary key enforcement and duplication handling."""
        
        # Connect to the cloud database
        conn = psycopg2.connect(
            host=CLOUD_DB_HOST,
            port=CLOUD_DB_PORT,
            dbname=CLOUD_DB_NAME,
            user=CLOUD_DB_USER,
            password=CLOUD_DB_PASSWORD
        )
        cursor = conn.cursor()

        for table in SYNC_TABLES:
            print(f"Syncing table: {table}")

            # Connect to local SQLite
            sqlite_conn = sqlite3.connect(LOCAL_DB_PATH)
            sqlite_cursor = sqlite_conn.cursor()

            try:
                # Get the schema from SQLite
                sqlite_cursor.execute(f"PRAGMA table_info({table})")
                columns = sqlite_cursor.fetchall()  # [(cid, name, type, notnull, dflt_value, pk), ...]

                if not columns:
                    print(f"⚠ Skipping {table}: No columns found in SQLite.")
                    continue

                column_defs = []
                column_names = []

                boolean_columns = set()

                # Set first column as primary key
                primary_key_column = columns[0][1]  # First column name

                for col in columns:
                    col_name = col[1]
                    col_type = col[2].upper()

                    if "INT" in col_type:
                        col_type = "INTEGER"
                    elif "TEXT" in col_type:
                        col_type = "TEXT"
                    elif "BOOLEAN" in col_type:
                        col_type = "BOOLEAN"
                        boolean_columns.add(col_name)
                    elif "REAL" in col_type:
                        col_type = "FLOAT"

                    if col_name == primary_key_column:
                        column_defs.append(f'"{col_name}" {col_type} PRIMARY KEY')
                    else:
                        column_defs.append(f'"{col_name}" {col_type}')
                    
                    column_names.append(f'"{col_name}"')

                column_defs_str = ", ".join(column_defs)
                column_names_str = ", ".join(column_names)

                # Check if table exists in PostgreSQL
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    print(f"🔹 Table '{table}' does not exist in PostgreSQL. Creating it...")
                    create_table_query = f'CREATE TABLE "{table}" ({column_defs_str})'
                    cursor.execute(create_table_query)

                # Check for missing columns
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
                existing_columns = {row[0] for row in cursor.fetchall()}

                missing_columns = set(col[1] for col in columns) - existing_columns
                for col in missing_columns:
                    col_type = next(c[2].upper() for c in columns if c[1] == col)
                    cursor.execute(f'ALTER TABLE "{table}" ADD COLUMN "{col}" {col_type}')
                    print(f"🛠 Added missing column '{col}' in '{table}'.")

                # Fetch data from SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()

                if rows:
                    placeholders = ",".join(["%s"] * len(rows[0]))

                    # Insert with ON CONFLICT DO NOTHING to avoid duplicates
                    insert_query = f'''
                        INSERT INTO "{table}" ({column_names_str})
                        VALUES ({placeholders})
                        ON CONFLICT ("{primary_key_column}") DO NOTHING
                    '''

                    for row in rows:
                        row = list(row)

                        # Convert boolean-like integers (0/1) to True/False
                        for i, col_name in enumerate(column_names):
                            if col_name.strip('"') in boolean_columns:
                                row[i] = bool(row[i])

                        cursor.execute(insert_query, row)

                sqlite_conn.close()

            except sqlite3.OperationalError:
                print(f"⚠ Error: Table '{table}' does not exist in SQLite!")

        # Commit changes and close PostgreSQL connection
        conn.commit()
        cursor.close()
        conn.close()



    def periodic_sync(self):
        """Run the sync function periodically."""
        while self.running:
            self.sync_to_cloud()
            time.sleep(SYNC_INTERVAL)

# To start sync process in a separate thread:
sync_thread = threading.Thread(target=KyanBot().periodic_sync, daemon=True)
sync_thread.start()

if __name__ == "__main__":
    bot = KyanBot()
    bot.run()
