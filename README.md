EchoSentinel
EchoSentinel is a modern web application that performs real-time sentiment analysis and profanity detection on audio content. Upload audio files (WAV, MP3) and visualize sentiment patterns and inappropriate language through an intuitive, interactive dashboard.
🌟 Features

Real-time Analysis: Watch as your audio is processed sentence by sentence
Dual Metrics: Track both overall sentiment scores and profanity detection simultaneously
Visual Indicators: Color-coded visualization with clear highlighting of concerning content
Interactive Graph: Hover for detailed information about specific sentences
Responsive Design: Works seamlessly across desktop and mobile devices
🚀 Installation
Prerequisites

Node.js (v14.0.0 or higher)
Python (v3.8 or higher)
FastAPI
React.js

Frontend Setup
bashCopy# Clone the repository
git clone https://github.com/yourusername/echo-sentinel.git
cd echo-sentinel/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
Backend Setup
bashCopy# Navigate to the backend directory
cd ../backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000

🔧 Configuration
The application uses a WebSocket connection to communicate between the frontend and backend. The default WebSocket URL is ws://localhost:8000/ws-graph.
To change this configuration, modify the following files:

Frontend: src/SentimentAnalysisGraph.js
Backend: nlp_trial.py

📊 How It Works

Upload Audio: Submit WAV or MP3 files through the interface
Audio Processing: The backend transcribes the audio to text
Sentiment Analysis: Each sentence is analyzed for sentiment score (-1 to 1)
Profanity Detection: Text is analyzed using a custom LSTM model to detect inappropriate language
Visualization: Results are displayed in real-time on an interactive graph
Highlighting: Negative sentiment and profanity are automatically highlighted

🧰 Technology Stack
Frontend

React.js
Chart.js for data visualization
Axios for HTTP requests
WebSocket for real-time updates
Modern CSS with responsive design

Backend

FastAPI (Python)
SpeechRecognition for audio transcription
NLTK and/or Transformers for sentiment analysis
Custom LSTM model for profanity detection
WebSockets for real-time communication

📱 Usage

Click the "Select an audio file" button or drag and drop an audio file
Press "Upload and Process" to begin analysis
Watch as the graph populates with data in real-time
Hover over data points for detailed information
View the summary statistics below the graph
Use the legend to understand the color coding

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

📞 Contact
Karan Panchal - panchalkaran677@gmail.com
