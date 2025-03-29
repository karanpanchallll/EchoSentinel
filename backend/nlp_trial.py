import asyncio
from fastapi import FastAPI, UploadFile, File, WebSocket,WebSocketDisconnect
from starlette.websockets import WebSocketState
import shutil
import os
import re
import random
import matplotlib.pyplot as plt
import io
import base64
from fastapi.responses import JSONResponse
from audio_processing import process_audio
from nlp_analysis import analyze_transcript
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Adjust if frontend runs on another port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload directory exists

# Store uploaded filenames for reference
uploaded_files = {}

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    """
    Uploads an audio file and processes it completely.
    Returns full analysis results.
    """
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    uploaded_files["latest"] = file.filename

    try:
        # Process audio (transcription + speaker separation)
        speakers, transcript = process_audio(file_path)

        # Analyze entire transcript
        full_analysis = analyze_transcript(transcript)

        # Prepare comprehensive response
        response = {
            "filename": file.filename,
            "transcript": transcript,
            "speakers": speakers,
            "analysis": full_analysis,
            "summary": {
                "total_sentences": len(full_analysis),
                "profane_sentences": sum(1 for item in full_analysis if item['profanity'] != "Clean"),
                "negative_sentiment_sentences": sum(1 for item in full_analysis if item['sentiment']['compound'] < 0)
            }
        }

        return response

    except Exception as e:
        return {"error": str(e), "filename": file.filename}
    
real_time_graph_data = {
    "timestamps": [],
    "sentiment_scores": [],
    "profanity_flags": []
}

@app.websocket("/ws-graph")
async def websocket_graph_endpoint(websocket: WebSocket):
    """
    Handles real-time graph streaming for audio transcription analysis.
    """
    await websocket.accept()
    
    # Reset graph data for new session
    real_time_graph_data = {
        "timestamps": [],
        "sentiment_scores": [],
        "profanity_flags": []
    }
    
    try:
        while True:
            try:
                # Wait for filename or control message from frontend
                message = await websocket.receive_text()
                
                file_name = uploaded_files.get("latest", None)
                if not file_name:
                    await safe_send(websocket, {"error": "No file uploaded yet."})
                    continue

                file_path = os.path.join(UPLOAD_FOLDER, file_name)

                # Validate file exists
                if not os.path.exists(file_path):
                    await safe_send(websocket, {"error": f"File not found: {file_path}"})
                    continue

                # Process audio in real-time
                speakers, transcript = process_audio(file_path)
                
                # Sentence-level analysis
                sentences = [s.strip() for s in re.split(r'[.!?]', transcript) if s.strip()]
                
                for i, sentence in enumerate(sentences):
                    # Check if connection is still open
                    if websocket.client_state != WebSocketState.CONNECTED:
                        break

                    # Analyze each sentence
                    sentence_analyses = analyze_transcript(sentence)
                    
                    if not sentence_analyses:
                        continue
                    
                    sentence_analysis = sentence_analyses[0]
                    
                    # Extract sentiment and profanity data
                    sentiment_score = sentence_analysis.get('sentiment', {}).get('compound', 0)
                    is_profane = sentence_analysis.get('profanity', 'Clean') != "Clean"
                    
                    # Update real-time graph data
                    real_time_graph_data["timestamps"].append(i)
                    real_time_graph_data["sentiment_scores"].append(sentiment_score)
                    real_time_graph_data["profanity_flags"].append(1 if is_profane else 0)
                    
                    # Prepare graph data to send
                    graph_data = {
                        "type": "graph_update",
                        "timestamps": real_time_graph_data["timestamps"],
                        "sentiment_scores": real_time_graph_data["sentiment_scores"],
                        "profanity_flags": real_time_graph_data["profanity_flags"]
                    }
                    
                    # Send graph data
                    await safe_send(websocket, graph_data)
                    
                    # Simulate real-time processing
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                
                # Send final graph completion message
                await safe_send(websocket, {
                    "type": "graph_complete",
                    "final_data": real_time_graph_data
                })
                
                # Break the main loop after processing
                break
                
            except Exception as processing_error:
                await safe_send(websocket, {
                    "type": "error",
                    "message": f"Processing failed: {str(processing_error)}"
                })
                break

    except WebSocketDisconnect:
        print("WebSocket connection closed by client")
    except Exception as e:
        print(f"Unexpected error in WebSocket: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

async def safe_send(websocket: WebSocket, data: dict):
    """
    Safely send data through WebSocket, handling potential connection issues.
    """
    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(data)
    except Exception as e:
        print(f"Error sending WebSocket message: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles real-time streaming of analysis results.
    Provides incremental updates as audio is processed.
    """
    await websocket.accept()
    try:
        while True:
            # Wait for filename from frontend
            message = await websocket.receive_text()
            print("Received from frontend:", message)

            file_name = uploaded_files.get("latest", None)
            if not file_name:
                await websocket.send_json({"error": "No file uploaded yet."})
                continue

            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Validate file exists
            if not os.path.exists(file_path):
                await websocket.send_json({"error": f"File not found: {file_path}"})
                continue

            # Step 1: Process audio (transcription + speaker separation)
            try:
                speakers, transcript = process_audio(file_path)
                
                # Send initial metadata
                await websocket.send_json({
                    "message": "Audio Processing Started",
                    "speakers": speakers,
                    "total_transcript_length": len(transcript)
                })

                # Step 2: Stream analysis results in real-time
                # More robust sentence splitting
                sentences = [s.strip() for s in re.split(r'[.!?]', transcript) if s.strip()]
                analysis_results = []

                for i, sentence in enumerate(sentences):
                    try:
                        # Ensure sentence is not empty
                        if not sentence:
                            continue

                        # Analyze each sentence
                        sentence_analyses = analyze_transcript(sentence)
                        
                        # Skip if no analysis results
                        if not sentence_analyses:
                            continue

                        sentence_analysis = sentence_analyses[0]

                        # Robust data preparation with error handling
                        result = {
                            "message": "Streaming Analysis",
                            "sentence_index": i,
                            "text": sentence,
                            "sentiment": {
                                "positive": sentence_analysis.get('sentiment', {}).get('pos', 0),
                                "negative": sentence_analysis.get('sentiment', {}).get('neg', 0),
                                "neutral": sentence_analysis.get('sentiment', {}).get('neu', 0),
                                "compound": sentence_analysis.get('sentiment', {}).get('compound', 0)
                            },
                            "profanity": sentence_analysis.get('profanity', 'Clean'),
                            "flags": {
                                "is_negative_sentiment": sentence_analysis.get('sentiment', {}).get('compound', 0) < 0,
                                "is_profane": sentence_analysis.get('profanity', 'Clean') != "Clean"
                            }
                        }

                        analysis_results.append(result)
                        await websocket.send_json(result)
                        
                        # Simulate real-time processing with some randomness
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                    
                    except Exception as sentence_error:
                        print(f"Error processing sentence {i}: {sentence_error}")
                        await websocket.send_json({
                            "message": "Sentence Analysis Error",
                            "sentence_index": i,
                            "error": str(sentence_error),
                            "text": sentence
                        })
                        continue

                # Send final complete analysis
                await websocket.send_json({
                    "message": "Analysis Complete",
                    "full_results": analysis_results
                })

            except Exception as processing_error:
                print(f"Audio processing error: {processing_error}")
                await websocket.send_json({
                    "error": f"Processing failed: {str(processing_error)}",
                    "stage": "audio_processing"
                })


    except Exception as connection_error:
        print(f"WebSocket connection error: {connection_error}")
    finally:
        await websocket.close()
    