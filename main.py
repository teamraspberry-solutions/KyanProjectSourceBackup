from services.speech_to_text import recognize_speech
from services.sentiment_analysis import analyze_sentiment
from services.chatbot_service import get_chatbot_response
from services.text_to_speech import text_to_speech
from services.database_service import get_user_id, insert_conversation, insert_new_user

def main():
    print("Starting continuous listening for your input...")



    if not existing_user_id:
        # If the user doesn't exist, insert them into the UserProfiles table
        user_id = insert_new_user()
        if user_id is None:
            print("Error inserting new user. Exiting.")
            return  # Stop the program if user creation fails

    
    
    while True:
        # Listen for speech input from the user
        user_speech = recognize_speech()
        while True:
        # Listen for speech input from the user
        user_speech = recognize_speech()
        
        while True:
        # Listen for speech input from the user
        user_speech = recognize_speech()

        if not user_speech:
            print("No speech detected. Please try again.")
            continue  # Continue the loop if no speech is detected

        #printing the speech 
        print(f"Recognized Speech: {user_speech}")

        # Check if the user wants to exit the conversation
        if user_speech.lower() == "thanks for the assistance.":
            print("Happy to help!")
            input("Press Enter to exit the program.")
            break  # Exit the loop and stop the program

        # Perform sentiment analysis on the speech input
        sentiment_output = analyze_sentiment(user_speech)

        #printing the sentiment scores 

        print(f"Overall Sentiment: {sentiment_output['overall_sentiment']}")
        print(f"Confidence Scores: {sentiment_output['confidence_scores']}")

        # Ensure sentiment is a string before inserting
        sentiment = sentiment_output.get('overall_sentiment', 'Neutral')  # Default to 'Neutral' if sentiment is missing
        insert_conversation(user_id, user_speech, sentiment)

        # Get the chatbot response based on the recognized speech input
        chatbot_response = get_chatbot_response(user_speech, user_id)

        if chatbot_response:
            print(f"Kyan: {chatbot_response}")
            text_to_speech(chatbot_response)
        else:
            print("There was an issue with the chatbot response.")

if __name__ == "__main__":
    main()
