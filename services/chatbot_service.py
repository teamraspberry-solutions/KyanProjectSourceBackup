import requests
from services.database_service import insert_conversation  # Import your insert function

# Global conversation context
conversation_context = {}

# Configuration
API_KEY = "Cg10kdlEepiZPkzbDNhY6qQm4W7gulx0Ylol5ofhKbcNYTEQSFj6JQQJ99AKAC77bzfXJ3w3AAABACOGsGeY"
ENDPOINT = "https://kyanopenaimodel.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview"

# Headers
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

def get_chatbot_response(user_input: str, user_id: int) -> str:
    global conversation_context

    # Initialize context for the user if not already present
    if user_id not in conversation_context:
        conversation_context[user_id] = [
            {"role": "system", "content": """You are Kyan, a friendly and supportive assistant. 
                                             You help students with their learning and mental health, so your responses should be short and easy to understand."""}
        ]

    # Add the user's message to the conversation context
    conversation_context[user_id].append({"role": "user", "content": user_input})

    # Create the payload with the dynamic conversation context
    payload = {
        "messages": conversation_context[user_id],
        "temperature": 0.9,
        "top_p": 0.1,
        "max_tokens": 800,
    }

    # Send the POST request to the API
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        response_data = response.json()
        assistant_reply = response_data['choices'][0]['message']['content']

        # Add the assistant's reply to the conversation context
        conversation_context[user_id].append({"role": "assistant", "content": assistant_reply})

   
        if len(conversation_context[user_id]) > 20:  # Example limit for storing conversation
            # Store the conversation in the database
            store_conversation(user_id, conversation_context[user_id])
            # Optionally, clear the in-memory context to save memory
            conversation_context[user_id] = []

        return assistant_reply
    except requests.RequestException as e:
        print(f"Failed to make the request. Error: {e}")
        return "I'm sorry, I couldn't process your request."

# Function to store the conversation in the database
def store_conversation(user_id: int, context: list):
    for entry in context:
        # You can include sentiment analysis or any other processing if needed
        sentiment = "neutral"  # For simplicity, assuming neutral sentiment
        insert_conversation(user_id, entry["content"], sentiment)
