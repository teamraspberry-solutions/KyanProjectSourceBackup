import requests
import time
from backend.config import AZURE_SENTIMENT_API_KEY, AZURE_SENTIMENT_ENDPOINT
from datetime import datetime, timedelta
from database.database import KyanDatabase

class SentimentAnalyzer:
    def __init__(self):
        self.api_key = AZURE_SENTIMENT_API_KEY
        self.endpoint = AZURE_SENTIMENT_ENDPOINT
        self.db = KyanDatabase()
        self.emotion_mapping = {
            "positive": "happiness",
            "neutral": "neutral",
            "negative": "sadness"  # Default mapping, adjusted later
        }

    def analyze_sentiment(self, text):
        """Analyzes sentiment using Azure's API and maps it to one of the seven emotions."""
        sentiment_url = f"{self.endpoint}/text/analytics/v3.0/sentiment"

        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Content-Type': 'application/json'
        }

        body = {
            'documents': [{'id': '1', 'text': text}]
        }

        response = requests.post(sentiment_url, headers=headers, json=body)
        response_data = response.json()

        if response.status_code == 200:
            sentiment = response_data['documents'][0]['sentiment']

            # Map Azure sentiment categories to the required seven emotions
            if sentiment == "negative":
                # Further classify negative sentiment based on confidence scores
                scores = response_data['documents'][0]['confidenceScores']
                if scores['negative'] > 0.7:
                    detected_emotion = "anger" if "angry" in text.lower() else "worry"
                else:
                    detected_emotion = "sadness"
            elif sentiment == "positive":
                detected_emotion = "happiness" if "love" not in text.lower() else "love"
            else:
                detected_emotion = "neutral"
            
            return detected_emotion
        else:
            raise Exception(f"Error analyzing sentiment: {response_data}")

    def save_sentiment_to_db(self, sentiment, timestamp):
        """Saves the analyzed sentiment to the database."""
        try:
            self.db.insert_sentiment(sentiment, timestamp)
        except Exception as e:
            print(f"Error saving sentiment to DB: {e}")

    def periodic_sentiment_analysis(self):
        """Runs sentiment analysis every 60 seconds on the latest user text."""
        while True:
            last_minute_timestamp = datetime.now() - timedelta(minutes=1)
            user_input = self.db.get_last_conversation_in_timeframe(last_minute_timestamp)

            if user_input:
                sentiment = self.analyze_sentiment(user_input)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_sentiment_to_db(sentiment, timestamp)
            
            time.sleep(60)  # Wait 60 seconds before analyzing again
