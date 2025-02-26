from backend.emotion_display import EmotionDisplay
import requests
import time
import threading
from backend.config import AZURE_SENTIMENT_API_KEY, AZURE_SENTIMENT_ENDPOINT
from datetime import datetime, timedelta
from database.database import KyanDatabase

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analyzer and EmotionDisplay."""
        self.api_key = AZURE_SENTIMENT_API_KEY
        self.endpoint = AZURE_SENTIMENT_ENDPOINT
        self.db = KyanDatabase()
        self.emotion_display = EmotionDisplay()

        self.emotion_mapping = {
            "positive": "happy",
            "neutral": "neutral",
            "negative": "sad"
        }


    def analyze_sentiment(self, text):
        """Analyzes sentiment using Azure API and triggers an emotion display."""
        if not text:
            return "neutral"

        sentiment_url = f"{self.endpoint}/text/analytics/v3.0/sentiment"
        headers = {'Ocp-Apim-Subscription-Key': self.api_key, 'Content-Type': 'application/json'}
        body = {'documents': [{'id': '1', 'text': text}]}

        try:
            response = requests.post(sentiment_url, headers=headers, json=body)
            response_data = response.json()

            if response.status_code != 200:
                raise Exception(f"Error analyzing sentiment: {response_data}")

            sentiment = response_data['documents'][0]['sentiment']
            scores = response_data['documents'][0]['confidenceScores']

            # Define thresholds for emotions based on sentiment scores
            if sentiment == "positive":
                if scores["positive"] > 0.8:  # Strong positive sentiment
                    detected_emotion = "happy"
                elif scores["positive"] > 0.4:  # Moderate positive sentiment
                    detected_emotion = "surprised"
                else:
                    detected_emotion = "neutral"
            elif sentiment == "negative":
                if scores["negative"] > 0.95:  # Strong negative sentiment
                    detected_emotion = "angry"
                elif scores["negative"] > 0.4:  # Moderate negative sentiment
                    detected_emotion = "sad"
                else:
                    detected_emotion = "neutral"
            else:
                # Neutral sentiment case
                detected_emotion = "neutral"

            # Update Emotion Display
            self.emotion_display.set_emotion(detected_emotion)
            return detected_emotion

        except Exception as e:
            print(f"Sentiment Analysis Error: {e}")
            return "neutral"


    def save_sentiment_to_db(self, sentiment):
        """Saves analyzed sentiment to the database."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.db.insert_sentiment(sentiment, timestamp)
        except Exception as e:
            print(f"Error saving sentiment to DB: {e}")

    # def periodic_sentiment_analysis(self):
    #     """Runs sentiment analysis every 10 seconds on the latest user text."""
    #     while True:
    #         try:
    #             last_timestamp = datetime.now() - timedelta(minutes=1)
    #             user_input = self.db.get_last_conversation_in_timeframe(last_timestamp)

    #             if user_input:
    #                 sentiment = self.analyze_sentiment(user_input)
    #                 self.save_sentiment_to_db(sentiment)

    #         except Exception as e:
    #             print(f"Error in periodic sentiment analysis: {e}")

    #         time.sleep(10)

