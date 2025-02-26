# services/database_service.py
import pyodbc
from datetime import datetime

# Establish a database connection
def get_db_connection():
    return pyodbc.connect(
        'Driver={ODBC Driver 18 for SQL Server};'
        'Server=tcp:kyanpersonalitystorage.database.windows.net,1433;'
        'Database=KyanOpenAIModel;'
        'Uid=parcival;'
        'Pwd=idontknow@86;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
def get_user_id(user_id):
    """Get the UserID from the UserProfiles table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the UserProfiles table using user_id
    cursor.execute("SELECT UserID FROM UserProfiles WHERE UserID = ?", user_id)
    row = cursor.fetchone()

    if row:
        return row[0]  # Return the UserID if it exists
    else:
        return None

    

def insert_new_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert a new user, automatically generating the user_id
        cursor.execute("""
            INSERT INTO UserProfiles DEFAULT VALUES;
        """)
        conn.commit()

        # Retrieve the newly generated user_id
        cursor.execute("SELECT SCOPE_IDENTITY()")
        new_user_id = cursor.fetchone()[0]

        print(f"New user created with UserID {new_user_id}")
        return new_user_id  # Return the new user ID

    except Exception as e:
        print(f"Error inserting new user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()




# Function to insert conversation history into the database
def insert_conversation(user_id, user_message, sentiment):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:

        # Check for an identical user message with the same sentiment within a reasonable time frame (e.g., 5 minutes)
        cursor.execute("""
            SELECT COUNT(*) FROM ConversationHistory
            WHERE UserID = ? AND Message = ? AND Sentiment = ? AND Timestamp > DATEADD(MINUTE, -5, GETDATE())
        """, user_id, user_message, sentiment)
        
        if cursor.fetchone()[0] > 0:
            print("Duplicate message detected. Skipping insert.")
            return

        # Insert user message and sentiment into the conversation history
        cursor.execute("""
            INSERT INTO ConversationHistory (UserID, Message, Sentiment, Timestamp)
            VALUES (?, ?, ?, ?)
        """, user_id, user_message, sentiment, datetime.now())
    
        conn.commit()
        print("Conversation inserted successfully...")
    except Exception as e:
        print(f"Error inserting conversation: {e}")
    finally:
        cursor.close()
        conn.close()



# Function to get conversation history for a specific user
def get_conversation_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Message, Sentiment, Timestamp 
        FROM ConversationHistory
        WHERE UserID = ?
        ORDER BY Timestamp DESC
    """, user_id)
    
    rows = cursor.fetchall()
    conversation_history = [
        {"message": row[0], "sentiment": row[1], "timestamp": row[2]} for row in rows
    ]
    
    cursor.close()
    conn.close()
    
    return conversation_history
