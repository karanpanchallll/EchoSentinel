import React, { useState, useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import "./Sentiment.css"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const SentimentAnalysisGraph = () => {
  const [graphData, setGraphData] = useState({
    timestamps: [],
    sentimentScores: [],
    profanityFlags: []
  });
  const [isConnected, setIsConnected] = useState(false);
  const websocketRef = useRef(null);

  useEffect(() => {
    // Establish WebSocket connection
    websocketRef.current = new WebSocket('ws://localhost:8000/ws-graph');

    websocketRef.current.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
    };

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Handle different types of graph updates
      switch(data.type) {
        case 'graph_update':
          setGraphData(prevData => ({
            timestamps: data.timestamps,
            sentimentScores: data.sentiment_scores,
            profanityFlags: data.profanity_flags
          }));
          break;
        
        case 'graph_complete':
          console.log('Graph analysis complete', data.final_data);
          break;
        
        case 'error':
          console.error('Graph processing error:', data.message);
          break;
      }
    };

    websocketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    websocketRef.current.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
    };

    // Cleanup on component unmount
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  // Trigger WebSocket to start processing
  const startProcessing = () => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send('start_processing');
    }
  };

  // Generate point background colors based on profanity flags and sentiment scores
  const generatePointBackgroundColors = () => {
    return graphData.timestamps.map((_, index) => {
      const isProfane = graphData.profanityFlags[index] === 1;
      const isNegativeSentiment = graphData.sentimentScores[index] < 0;
      
      if (isProfane && isNegativeSentiment) {
        return 'rgb(153, 0, 0)'; // Dark red for both profane and negative
      } else if (isProfane) {
        return 'rgb(255, 0, 0)'; // Red for profane
      } else if (isNegativeSentiment) {
        return 'rgb(255, 165, 0)'; // Orange for negative sentiment
      }
      return 'rgb(0, 128, 0)'; // Green for normal points
    });
  };

  // Generate point border colors (same as background but with full opacity)
  const generatePointBorderColors = () => {
    return generatePointBackgroundColors();
  };

  // Generate point sizes based on flags (larger points for flagged content)
  const generatePointSizes = () => {
    return graphData.timestamps.map((_, index) => {
      const isProfane = graphData.profanityFlags[index] === 1;
      const isNegativeSentiment = graphData.sentimentScores[index] < 0;
      
      if (isProfane || isNegativeSentiment) {
        return 8; // Larger points for flagged content
      }
      return 4; // Normal size for regular points
    });
  };

  // Prepare chart data
  const chartData = {
    labels: graphData.timestamps,
    datasets: [
      {
        label: 'Sentiment Score',
        data: graphData.sentimentScores,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: generatePointBackgroundColors(),
        borderWidth: 1,
        pointRadius: generatePointSizes(),
        pointBorderColor: generatePointBorderColors(),
        tension: 0.1
      },
      {
        label: 'Profanity Flag',
        data: graphData.profanityFlags,
        borderColor: 'rgb(255, 99, 132)',
        pointRadius: (context) => {
          const index = context.dataIndex;
          return graphData.profanityFlags[index] === 1 ? 8 : 4;
        },
        pointBackgroundColor: (context) => {
          const index = context.dataIndex;
          return graphData.profanityFlags[index] === 1 ? 'rgb(255, 0, 0)' : 'rgb(255, 99, 132)';
        },
        tension: 0.1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Real-Time Sentiment and Profanity Analysis'
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const index = context.dataIndex;
            const isProfane = graphData.profanityFlags[index] === 1;
            const isNegativeSentiment = graphData.sentimentScores[index] < 0;
            
            let labels = [];
            
            if (context.dataset.label === 'Sentiment Score') {
              labels.push(`Sentiment: ${context.raw.toFixed(2)}`);
              if (isNegativeSentiment) {
                labels.push('⚠️ Negative Sentiment Detected');
              }
            } else {
              labels.push(`Profanity: ${context.raw === 1 ? 'Yes' : 'No'}`);
            }
            
            if (isProfane) {
              labels.push('⚠️ Profanity Detected');
            }
            
            return labels;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Score / Flag'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Sentence Index'
        }
      }
    }
  };

  return (
    <div className="sentiment-analysis-graph">
      <div className="graph-controls">
        <button 
          onClick={startProcessing}
          disabled={!isConnected}
        >
          {isConnected ? 'Start Processing' : 'Connecting...'}
        </button>
        
        {!isConnected && (
          <p className="connection-status">
            Attempting to connect to WebSocket...
          </p>
        )}
      </div>

      <div className="graph-container">
        <Line 
          data={chartData} 
          options={chartOptions} 
        />
      </div>

      <div className="graph-summary">
        <p>Total Sentences Processed: {graphData.timestamps.length}</p>
        <p>Negative Sentiment Sentences: <span style={{color: 'orange', fontWeight: 'bold'}}>{graphData.sentimentScores.filter(score => score < 0).length}</span></p>
        <p>Profane Sentences: <span style={{color: 'red', fontWeight: 'bold'}}>{graphData.profanityFlags.filter(flag => flag === 1).length}</span></p>
      </div>
      
      <div className="legend">
        <h4>Indicators:</h4>
        <div className="legend-item">
          <span className="legend-dot" style={{backgroundColor: 'rgb(0, 128, 0)'}}></span>
          <span>Normal content</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{backgroundColor: 'rgb(255, 165, 0)'}}></span>
          <span>Negative sentiment</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{backgroundColor: 'rgb(255, 0, 0)'}}></span>
          <span>Profanity detected</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{backgroundColor: 'rgb(153, 0, 0)'}}></span>
          <span>Both negative sentiment and profanity</span>
        </div>
      </div>

      <style jsx>{`
        .graph-summary span {
          font-weight: bold;
        }
        .legend {
          margin-top: 20px;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 5px;
        }
        .legend-item {
          display: flex;
          align-items: center;
          margin-bottom: 5px;
        }
        .legend-dot {
          display: inline-block;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 8px;
        }
      `}</style>
    </div>
  );
};

export default SentimentAnalysisGraph;