import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of the given text using Azure Text Analytics.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing overall sentiment, confidence scores, and categorized sentences.
    """
    # Azure Text Analytics endpoint and key
    endpoint = "https://kyansentimentanalysismodel.cognitiveservices.azure.com/"
    key = "8svMt89ekLhLNXt7zOSMz9YrQ6Iic7n7Gtp383tYyStqFQg0K6u5JQQJ99AKACqBBLyXJ3w3AAAaACOGREMD"

    # Initialize the Text Analytics Client
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Analyze sentiment of the text
    documents = [text]
    result = text_analytics_client.analyze_sentiment(documents, show_opinion_mining=True)
    docs = [doc for doc in result if not doc.is_error]

    # Prepare response
    sentiment_result = {
        "overall_sentiment": None,
        "confidence_scores": None,
        "positive_sentences": [],
        "neutral_sentences": [],
        "negative_sentences": []
    }

    if docs:
        doc = docs[0]
        sentiment_result["overall_sentiment"] = doc.sentiment
        sentiment_result["confidence_scores"] = {
            "positive": doc.confidence_scores.positive,
            "neutral": doc.confidence_scores.neutral,
            "negative": doc.confidence_scores.negative
        }

        # Process each sentence
        for sentence in doc.sentences:
            if sentence.sentiment == "positive":
                sentiment_result["positive_sentences"].append(sentence.text)
            elif sentence.sentiment == "neutral":
                sentiment_result["neutral_sentences"].append(sentence.text)
            elif sentence.sentiment == "negative":
                sentiment_result["negative_sentences"].append(sentence.text)

    return sentiment_result