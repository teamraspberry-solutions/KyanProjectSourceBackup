import azure.cognitiveservices.speech as speechsdk
import openai
import requests
import time
import threading
from backend.config import (AZURE_SPEECH_API_KEY,AZURE_SPEECH_REGION,AZURE_OPENAI_API_KEY,OPENAI_MODEL,)

class SpeechProcessor:
    def __init__(self):
        """Initialize Azure Speech Services and OpenAI configurations."""
        self.speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_API_KEY, region=AZURE_SPEECH_REGION
        )
        self.speech_config.speech_synthesis_voice_name = "en-US-EvelynMultilingualNeural"

        self.speaking = False

        # Ensure microphone availability
        try:
            self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        except RuntimeError:
            print("Warning: Microphone not available. Speech recognition may not work.")
            self.audio_config = None

        # Recognizer for Speech-to-Text
        if self.audio_config:
            self.recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, audio_config=self.audio_config
            )
        else:
            self.recognizer = None

        # Synthesizer for Text-to-Speech
        self.synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        )

        # OpenAI API Configuration
        self.API_KEY = "Cg10kdlEepiZPkzbDNhY6qQm4W7gulx0Ylol5ofhKbcNYTEQSFj6JQQJ99AKAC77bzfXJ3w3AAABACOGsGeY"
        self.ENDPOINT = "https://kyanopenaimodel.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview"       
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.API_KEY,
        }

    def recognize_speech(self):
        """Recognizes speech, ensuring the bot has finished speaking and avoiding microphone lock issues."""
        if not self.audio_config:
            print("Microphone not available.")
            return "Speech recognition unavailable."
        
        print("Waiting for bot response to finish...")
        while self.is_speaking():  # Wait until the bot finishes speaking
            time.sleep(0.1)
        
        print("Listening for speech...")
        last_spoken_time = time.time()
        recognized_text = None

        def listen():
            """Internal function to recognize speech and update the last spoken time."""
            nonlocal recognized_text, last_spoken_time
            
            try:
                recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config, audio_config=self.audio_config
                )
                result = recognizer.recognize_once()
                recognizer = None  # Release the recognizer

                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    recognized_text = result.text
                    print(f"Recognized: {recognized_text}")
                    last_spoken_time = time.time()
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    print("No speech recognized.")
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    print(f"Speech recognition canceled: {cancellation.reason}")
                    if cancellation.reason == speechsdk.CancellationReason.Error:
                        print(f"Error details: {cancellation.error_details}")
            except Exception as e:
                print(f"Error in speech recognition: {e}")
        
        recognition_thread = threading.Thread(target=listen)
        recognition_thread.start()
        
        while recognition_thread.is_alive() or (time.time() - last_spoken_time) < 1:
            time.sleep(0.1)
        
        return recognized_text


    def is_speaking(self):
        """Returns True if the bot is still speaking, False otherwise."""
        return self.speaking
    
    def text_to_speech(self, text):
        """Converts text into speech using Azure TTS."""
        if not text:
            return
        
        self.speaking = True
        # print(f"Kyan says: {text}")
        time.sleep(len(text) * 0.05)  # Approximate duration
        try:
            speech_synthesis_result = self.synthesizer.speak_text_async(text).get()

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesis completed successfully.")
            elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speech_synthesis_result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")
        except Exception as e:
            print(f"Error in speech synthesis: {e}")

        self.speaking = False  # Speech finished

    def generate_chatbot_response(self, user_input: str, context: str) -> str:
        """
        Generates a response from OpenAI based on user input and context.

        Args:
            user_input (str): The user's input.
            context (str): Additional context for the chatbot.

        Returns:
            str: The chatbot's response.
        """
        prompt = f"Context: {context}\nUser: {user_input}\nBot:"

        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "n": 1,
        }

        self.API_KEY = "Cg10kdlEepiZPkzbDNhY6qQm4W7gulx0Ylol5ofhKbcNYTEQSFj6JQQJ99AKAC77bzfXJ3w3AAABACOGsGeY"
        self.ENDPOINT = "https://kyanopenaimodel.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview"

        try:
            response = requests.post(self.ENDPOINT, headers=self.headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            chatbot_response = response_data["choices"][0]["message"]["content"].strip()
            # print(f"Bot response: {chatbot_response}")
            return chatbot_response
        except requests.RequestException as e:
            print(f"Error generating chatbot response: {e}")
            return "Sorry, I couldn't understand that. Could you please rephrase?"


    def generate_recap_summary(self, context):
        """Generates a summary of the last study session using a different chatbot model."""
        prompt = f"Summarize the following study session:\n{context}\nProvide a brief, short but informative recap."
        return self.generate_chatbot_response(prompt, context)
