import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import SentimentAnalysisGraph from './SentimentAnalysisGraph';

const App = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [statusType, setStatusType] = useState(''); // 'uploading', 'success', 'error'
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      // Reset upload status when a new file is selected
      setUploadStatus('');
      setStatusType('');
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      setStatusType('error');
      return;
    }

    // Validate file type
    const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg'];
    if (!allowedTypes.includes(selectedFile.type)) {
      setUploadStatus('Invalid file type. Please upload an audio file (WAV, MP3).');
      setStatusType('error');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setUploadStatus('Preparing to upload...');
      setStatusType('uploading');
      setIsProcessing(true);
      setUploadProgress(0);

      const response = await axios.post('http://localhost:8000/upload-audio/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
          setUploadStatus(`Uploading: ${percentCompleted}%`);
        }
      });

      setUploadStatus('Upload successful! Processing audio...');
      setStatusType('success');
      console.log('Upload response:', response.data);

    } catch (error) {
      console.error('Upload error:', error);
      setStatusType('error');
      
      // More detailed error handling
      if (error.response) {
        // The request was made and the server responded with a status code
        setUploadStatus(`Upload failed: ${error.response.data.message || 'Server error'}`);
      } else if (error.request) {
        // The request was made but no response was received
        setUploadStatus('No response from server. Please check your connection.');
      } else {
        // Something happened in setting up the request
        setUploadStatus('Error setting up upload request');
      }

      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setUploadStatus('');
    setStatusType('');
    setUploadProgress(0);
    setIsProcessing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="audio-uploader-container">
      <div className="file-upload-section">
        <div className="file-upload-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
            <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
          </svg>
          <h2>Audio Sentiment Analysis</h2>
        </div>
        
        <div className="file-input-container">
          <label htmlFor="audio-file">Select an audio file (WAV, MP3)</label>
          <div className="file-input-wrapper">
            <input 
              id="audio-file"
              type="file" 
              accept="audio/wav,audio/mp3,audio/mpeg"
              onChange={handleFileSelect}
              ref={fileInputRef}
              disabled={isProcessing}
            />
          </div>
          
          {selectedFile && (
            <div className="selected-file-info">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 18h.01"></path>
                <path d="M12 12h.01"></path>
                <path d="M12 6h.01"></path>
                <path d="M12 2v2"></path>
                <path d="M12 20v2"></path>
                <path d="M6 12H4"></path>
                <path d="M20 12h-2"></path>
                <path d="m14.833 9.167-1.666 1.666"></path>
                <path d="m14.833 14.833-1.666-1.666"></path>
                <path d="m9.167 9.167 1.666 1.666"></path>
                <path d="m9.167 14.833 1.666-1.666"></path>
              </svg>
              <span className="selected-file-name">{selectedFile.name}</span>
              <span className="selected-file-size">({formatFileSize(selectedFile.size)})</span>
            </div>
          )}
        </div>
        
        <div className="button-container">
          <button 
            onClick={handleUpload} 
            disabled={!selectedFile || isProcessing}
          >
            {!isProcessing ? (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                Upload and Process
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="animate-spin">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                Processing...
              </>
            )}
          </button>
          
          <button 
            onClick={handleReset}
            disabled={!selectedFile || isProcessing}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 6h18"></path>
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
            </svg>
            Reset
          </button>
        </div>
        
        {uploadStatus && (
          <div className={`upload-status ${statusType}`}>
            {statusType === 'uploading' && (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
              </svg>
            )}
            {statusType === 'success' && (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            )}
            {statusType === 'error' && (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            )}
            {uploadStatus}
          </div>
        )}
        
        {statusType === 'uploading' && (
          <div className="progress-container">
            <div className="progress-bar" style={{ width: `${uploadProgress}%` }}></div>
          </div>
        )}
      </div>
      
      <SentimentAnalysisGraph />
    </div>
  );
};

export default App;