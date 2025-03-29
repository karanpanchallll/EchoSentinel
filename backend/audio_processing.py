import torch
import whisper
import librosa
import soundfile as sf
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.audio import Model
from huggingface_hub import login
import os
from dotenv import load_dotenv
load_dotenv()
# Authenticate with Hugging Face
HF_AUTH_TOKEN = os.getenv("HF_AUTH_TOKEN")
if HF_AUTH_TOKEN:
    login(HF_AUTH_TOKEN)
else:
    raise ValueError("Hugging Face authentication token not found!")

# Load Whisper Model for Transcription
whisper_model = whisper.load_model("medium")

# Load PyAnnote Pretrained Models
model = Model.from_pretrained("pyannote/segmentation-3.0", use_auth_token=HF_AUTH_TOKEN)
pipeline = SpeakerDiarization.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_AUTH_TOKEN)

def separate_speakers(audio_path):
    """
    Performs speaker diarization to identify and separate speakers in an audio file.
    Returns a list of speaker segments with start time, end time, and speaker label.
    """
    try:
        diarization = pipeline({"uri": "file", "audio": audio_path})
        speaker_segments = [
            {"start": turn.start, "end": turn.end, "speaker": speaker}
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]
        return speaker_segments
    except Exception as e:
        print(f"Error during speaker diarization: {e}")
        return []

def transcribe_audio(audio_path):
    """
    Transcribes audio using OpenAI's Whisper model.
    Returns the full transcript text.
    """
    try:
        result = whisper_model.transcribe(audio_path, language="en")  # Force English
        return result["text"]
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

def process_audio(audio_path):
    """
    Handles speaker separation and transcription.
    Returns:
        - Speaker segments (start, end, speaker ID)
        - Transcribed text
    """
    speakers = separate_speakers(audio_path)
    transcript = transcribe_audio(audio_path)
    
    return speakers, transcript
