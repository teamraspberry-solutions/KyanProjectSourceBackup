import azure.cognitiveservices.speech as speechsdk

# Azure Speech Configuration
speech_key, service_region = "EHi9ZkNkweMbzx6tOwtS7IyL4kgGvGF2uzmqDwa9q7dxtPOVrtToJQQJ99AKACqBBLyXJ3w3AAAYACOG03ee", "southeastasia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

def text_to_speech(text: str):
    
    # Create an instance of a speech config with the Azure API key and region
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # Set the voice to "Jenny" (which is a default Azure voice)
    speech_config.speech_synthesis_voice_name = "en-US-EvelynMultilingualNeural"  # Voice name for Jenny

    # Create a speech synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Synthesize speech
    result = synthesizer.speak_text_async(text).get()

    # Check the result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Successfully synthesized the speech.")
    else:
        print(f"Speech synthesis failed: {result.error_details}")

