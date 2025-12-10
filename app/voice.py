import os
import pyttsx3
import asyncio
from faster_whisper import WhisperModel

# Initialize Whisper model once
stt_model_size = "base"
stt_model = None

# Initialize pyttsx3 engine
try:
    tts_engine = pyttsx3.init()
except Exception as e:
    print(f"Warning: Could not initialize TTS engine: {e}")
    tts_engine = None

def get_stt_model():
    global stt_model
    if stt_model is None:
        try:
            # compute_type="int8" is faster on CPU
            stt_model = WhisperModel(stt_model_size, device="cpu", compute_type="int8")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
    return stt_model

def transcribe_audio(audio_path):
    """
    Transcribes audio file to text using Faster Whisper.
    """
    model = get_stt_model()
    if not model:
        return "Error: Speech-to-Text model failed to load."

    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        text = ""
        for segment in segments:
            text += segment.text + " "
        return text.strip()
    except Exception as e:
        return f"Error transcribing audio: {e}"

def run_tts(text, output_file="output.mp3"):
    """
    Converts text to speech using pyttsx3 (Offline).
    """
    if not tts_engine:
        return None

    try:
        # Saving to file
        tts_engine.save_to_file(text, output_file)
        tts_engine.runAndWait()
        return output_file
    except Exception as e:
        print(f"TTS Failed: {e}")
        return None
