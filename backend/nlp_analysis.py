import os
import numpy as np
import tensorflow as tf
import joblib
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure TensorFlow uses CPU if GPU is unavailable
if not tf.config.experimental.list_physical_devices('GPU'):
    print("Using CPU for TensorFlow operations.")

# Load pre-trained LSTM model for profanity detection
try:
    MODEL_PATH = "profanity_lstm_model.h5"  # Update with actual path
    model = load_model(MODEL_PATH)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Load trained tokenizer
try:
    tokenizer = joblib.load("tokenizer.joblib")  # Ensure tokenizer is saved from training
    print("✅ Tokenizer loaded successfully.")
except Exception as e:
    print(f"❌ Error loading tokenizer: {e}")
    tokenizer = None

# Vader Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Match sequence length to training data
MAX_SEQUENCE_LENGTH = 50

# Expanded profanity list
PROFANITY_WORDS = {
    "fuck", "shit", "bitch", "bastard", "asshole", "dumbass", "crap", "dick",
    "piss", "bollocks", "prick", "motherfucker", "slut", "whore", "cock", "cunt",
    "bugger", "wanker", "twat", "tosser", "dipshit", "jackass", "son of a bitch",
    "arse", "arsehole", "bloody hell", "bollocking", "gobshite", "horseshit",
    "fuckface", "fuckwad", "shithead", "shitface", "asshat", "asswipe", "scumbag",
    "skank", "pussy", "douche", "douchebag", "dickhead", "motherless", "arsewipe",
    "numbnuts", "bellend", "clunge", "chode", "cumdumpster", "jizz", "jizzrag",
    "twatwaffle", "knobhead", "knobend", "minge", "muppet", "nonce", "pillock",
    "plonker", "turd", "wazzock", "wog", "spaz", "retard", "mong", "cocksucker",
    "shitstain", "shitshow", "whoremonger", "fucktard", "cumstain", "motherfucking",
    "bastarding", "goddamn", "goddammit"
}

# Mild words that are flagged only in negative sentiment
MILD_PROFANITY_WORDS = {
    "hell", "damn", "ridiculous", "stupid", "crap", "dumb", "idiot", "moron", 
    "fool", "loser", "jerk", "suck", "lame", "trash", "bullshit", "useless", 
    "nonsense", "pathetic", "lazy", "gross", "annoying", "disgusting", "terrible", 
    "horrible", "awful", "freak", "weirdo", "screw", "shady", "dirty", "cheap",
    "clown", "shameless", "nasty", "stinking", "miserable", "dammit", "idiotic"
}
def preprocess_text(text):
    """Tokenizes and pads input text for LSTM model."""
    if tokenizer is None:
        print("⚠️ Warning: Tokenizer not available.")
        return None
    sequences = tokenizer.texts_to_sequences([text])
    padded_seq = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    return padded_seq

def detect_profanity(text, sentiment_score):
    """Detects profanity using LSTM model and keyword matching."""
    words = set(text.lower().split())

    # Check for strong profanity words
    if any(word in words for word in PROFANITY_WORDS):
        return "Profane"

    # Check for mild profanity only if sentiment is negative
    if any(word in words for word in MILD_PROFANITY_WORDS) and sentiment_score["compound"] < -0.3:
        return "Mildly Profane"

    # Use LSTM model if available
    if model:
        processed_text = preprocess_text(text)
        if processed_text is not None:
            prediction = model.predict(processed_text)[0][0]  # Binary classification (0=clean, 1=profanity)
            if prediction > 0.8:
                return "Profane"
            elif prediction > 0.5:
                return "Mildly Profane"

    return "Clean"

def analyze_sentiment(text):
    """Analyze sentiment using Vader."""
    return sia.polarity_scores(text)

def analyze_transcript(transcript):
    """Process and analyze a given transcript."""
    try:
        sentences = sent_tokenize(transcript)
        results = []

        for sentence in sentences:
            try:
                sentiment = analyze_sentiment(sentence)
                profanity = detect_profanity(sentence, sentiment)

                results.append({
                    "sentence": sentence,
                    "sentiment": sentiment,
                    "profanity": profanity
                })

            except Exception as inner_e:
                print(f"⚠️ Error processing sentence: {sentence} | {inner_e}")

        return results

    except Exception as e:
        print(f"❌ Error analyzing transcript: {e}")
        return []