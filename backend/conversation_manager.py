import time
from threading import Thread
from datetime import datetime
from database.database import KyanDatabase

class ConversationManager:
    def __init__(self, db):
        self.db = db
        self.conversations = []  # Array to hold conversations temporarily
        self.saving_thread = Thread(target=self.save_conversations_periodically)
        self.saving_thread.start()
    
    def add_conversation(self, conversation, mode, conversation_type, user_id=1):
        """Add a conversation to the temporary array."""
        self.conversations.append({
            'conversation': conversation,
            'mode': mode,
            'conversation_type': conversation_type,
            'user_id': user_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def save_conversations_periodically(self):
        """Periodically save conversations to the database every 15 seconds."""
        while True:
            if self.conversations:
                # Process and save all stored conversations
                for conv in self.conversations:
                    self.save_conversation(conv['conversation'], conv['mode'], conv['conversation_type'], conv['user_id'], conv['timestamp'])
                self.conversations.clear()  # Clear the temporary array after saving
            time.sleep(15)  # Wait for 15 seconds before saving again
    
    def save_conversation(self, conversation, mode, conversation_type, user_id, timestamp):
        """Save a single conversation to the appropriate table."""
        table = "characteristic1_conversation_history" if mode == 1 else "characteristic2_conversation_history"
        
        # Insert conversation into the respective table
        self.db.cursor.execute(
            f"INSERT INTO {table} (conversation, conversation_type, user_id, timestamp) VALUES (?, ?, ?, ?)",
            (conversation, conversation_type, user_id, timestamp)
        )
        self.db.conn.commit()

# Instantiate the ConversationManager and Database connection
db = KyanDatabase()
conversation_manager = ConversationManager(db)
