import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Embedding, LSTM, Dense, Dropout, 
                                     MultiHeadAttention, LayerNormalization, GlobalAveragePooling1D)
import joblib
from sklearn.model_selection import train_test_split

# **1. Define the Dataset**
texts = [
    "you are an idiot", "this is stupid", "i hate you", "you are dumb",
    "shut up", "get lost", "you're so annoying", "that’s a dumb idea",
    "what a piece of trash", "go to hell", "nobody likes you", "this is crap",
    "you're an absolute fool", "screw you", "this is the worst thing ever",
    "you're a joke", "stop being such an idiot", "you are a loser",
    "what a terrible person", "this is a stupid idea", "dumb move",
    "you suck", "that's a ridiculous statement", "your opinion is trash",
    "you're the worst", "idiotic behavior", "stop acting like a fool",
    "you're a failure", "pathetic excuse", "don't be an idiot",
    "this is absolute nonsense", "your work is garbage",
    "what a useless idea", "you're just plain stupid", "nobody cares",
    "stop talking nonsense", "this is the dumbest thing ever",
    "you know nothing", "you're clueless", "that's complete bullshit",
    "this is the worst thing I've seen", "you're such a moron",
    "stupidest thing I've ever heard", "this is utterly pathetic",
    "who even listens to you?", 
    "hello, how are you?", "have a great day", "I appreciate your help",
    "nice to meet you", "you're very kind", "that's an interesting idea",
    "let’s work together", "I respect your opinion", "that's a good suggestion",
    "thanks for your help", "you're doing great", "keep up the good work",
    "I completely understand", "that’s a valid point", "we should discuss this further",
    "let’s find a solution", "your input is valuable", "I agree with you",
    "that’s a creative approach", "I like your perspective", "great teamwork",
    "you have a unique way of thinking", "this is a positive discussion",
    "let’s keep the conversation constructive", "I appreciate your insight",
    "thank you for your contribution", "your support means a lot",
    "this is an amazing project", "I love your enthusiasm",
    "your dedication is inspiring", "this idea is brilliant",
    "I really enjoy working with you", "let’s collaborate more",
    "you have great leadership skills", "you're a great friend",
    "I love the way you think", "that’s a fantastic insight",
    "your work is truly appreciated", "this discussion is insightful",
    "I'm grateful for your feedback", "your kindness is wonderful",
    "I value your perspective", "you always bring great ideas",
    "you're such a great problem solver", "this is a very productive conversation",
    "I'm impressed with your knowledge", "you are making a real impact",
    "this is really valuable input", "you bring positivity to the team",
    "thank you for your hard work", "this is a game-changing idea",
    "your contribution is appreciated", "you’re a role model for others",
    "this project has a lot of potential", "I believe in your abilities"
]
labels = np.array([1] * 50 + [0] * 50)

# **2. Tokenization & Preprocessing**
tokenizer = Tokenizer(oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)

assert len(sequences) == len(labels), f"Mismatch! Sequences: {len(sequences)}, Labels: {len(labels)}"

max_length = 50
X = pad_sequences(sequences, maxlen=max_length, padding="post", truncating="post")
y = np.array(labels)

assert len(X) == len(y), f"Final Mismatch! X: {len(X)}, y: {len(y)}"

# **3. Train-Test Split**
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# **4. Functional API Model**
input_layer = Input(shape=(max_length,))
embedding = Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=128)(input_layer)
lstm_out = LSTM(64, return_sequences=True)(embedding)

attention_out = MultiHeadAttention(num_heads=2, key_dim=64)(lstm_out, lstm_out)
attention_out = LayerNormalization()(attention_out)
dropout = Dropout(0.5)(attention_out)

lstm_out2 = LSTM(32)(dropout)
dense = Dense(16, activation="relu")(lstm_out2)
output_layer = Dense(1, activation="sigmoid")(dense)

model = Model(inputs=input_layer, outputs=output_layer)

# **5. Compile Model**
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# **6. Train Model**
model.fit(X_train, y_train, epochs=15, batch_size=16, validation_data=(X_val, y_val))

# **7. Save Model & Tokenizer**
model.save("profanity_lstm_model.h5")
joblib.dump(tokenizer, "tokenizer.joblib")

print("✅ Model trained and saved successfully!")

# **8. Rule-Based Post-Processing**
def rule_based_filter(text, lstm_prediction):
    profane_keywords = {"hell", "damn", "crap", "stupid", "idiot", "moron", "bullshit", "shit"}
    if any(word in text.lower() for word in profane_keywords):
        return 1
    return lstm_prediction