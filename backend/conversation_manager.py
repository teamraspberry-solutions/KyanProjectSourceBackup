import time
from threading import Thread
from datetime import datetime
from database.database import KyanDatabase

class ConversationManager:
    def __init__(self, db):
        self.db = db
        self.characteristic1_conversations = []  # Temporary storage for characteristic1
        self.characteristic2_conversations = []  # Temporary storage for characteristic2
        self.saving_thread = Thread(target=self.save_conversations_periodically, daemon=True)
        self.saving_thread.start()
    
    def add_characteristic1_conversation(self, conversation, conversation_type, user_id=1):
        """Add a conversation to the characteristic1 temporary array."""
        self.characteristic1_conversations.append({
            'conversation': conversation,
            'conversation_type': conversation_type,
            'user_id': user_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def add_characteristic2_conversation(self, conversation, conversation_type, session_id, user_id=1):
        """Add a conversation to the characteristic2 temporary array, including session_id."""
        self.characteristic2_conversations.append({
            'conversation': conversation,
            'conversation_type': conversation_type,
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def save_conversations_periodically(self):
        """Periodically save conversations to the database every 15 seconds."""
        while True:
            if self.characteristic1_conversations:
                for conv in self.characteristic1_conversations:
                    self.db.insert_characteristic1_history(
                        conv['conversation'], conv['conversation_type'], conv['user_id']
                    )
                self.characteristic1_conversations.clear()

            if self.characteristic2_conversations:
                for conv in self.characteristic2_conversations:
                    self.db.insert_characteristic2_history(
                        conv['conversation'], conv['conversation_type'], conv['user_id'], conv['session_id']
                    )
                self.characteristic2_conversations.clear()
            
            time.sleep(15)  # Wait for 15 seconds before checking again

# Instantiate the ConversationManager and Database connection
db = KyanDatabase()
conversation_manager = ConversationManager(db)
