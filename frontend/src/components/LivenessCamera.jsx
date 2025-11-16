import React, { useState, useRef, useEffect, useCallback } from 'react';

const LivenessCamera = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [instructions, setInstructions] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const [capturedFrames, setCapturedFrames] = useState([]);
  const [faceDetected, setFaceDetected] = useState(false);

  // Liveness detection steps
  const livenessSteps = [
    { instruction: '📱 Look directly at the camera', duration: 2000 },
    { instruction: '😊 Smile naturally', duration: 2000 },
    { instruction: '👁️ Blink your eyes slowly', duration: 2000 },
    { instruction: '↔️ Turn your head slightly left, then right', duration: 3000 },
    { instruction: '📸 Stay still for final capture', duration: 2000 }
  ];

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
        startLivenessDetection();
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      alert('Camera access denied. Please allow camera permissions and try again.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const startLivenessDetection = () => {
    setIsRecording(true);
    setCurrentStep(0);
    processLivenessStep(0);
  };

  const processLivenessStep = (stepIndex) => {
    if (stepIndex >= livenessSteps.length) {
      completeLivenessDetection();
      return;
    }

    const step = livenessSteps[stepIndex];
    setInstructions(step.instruction);
    setCurrentStep(stepIndex);

    // Countdown for this step
    let timeLeft = Math.ceil(step.duration / 1000);
    setCountdown(timeLeft);
    
    const countdownInterval = setInterval(() => {
      timeLeft--;
      setCountdown(timeLeft);
      
      if (timeLeft <= 0) {
        clearInterval(countdownInterval);
        // Capture frame at the end of each step
        captureFrame(stepIndex);
        processLivenessStep(stepIndex + 1);
      }
    }, 1000);
  };

  const captureFrame = (stepIndex) => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      canvas.toBlob((blob) => {
        const frame = {
          step: stepIndex,
          blob: blob,
          timestamp: Date.now(),
          instruction: livenessSteps[stepIndex].instruction
        };
        
        setCapturedFrames(prev => [...prev, frame]);
      }, 'image/jpeg', 0.8);
    }
  };

  const completeLivenessDetection = () => {
    setIsRecording(false);
    setInstructions('✅ Liveness detection complete!');
    
    // Send all frames for liveness analysis
    if (capturedFrames.length > 0) {
      // Use the last frame as the main selfie
      const finalFrame = capturedFrames[capturedFrames.length - 1];
      onCapture({
        mainImage: finalFrame.blob,
        livenessFrames: capturedFrames,
        livenessComplete: true
      });
    }
    
    setTimeout(() => {
      onClose();
    }, 2000);
  };

  const handleManualCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      canvas.toBlob((blob) => {
        onCapture({
          mainImage: blob,
          livenessFrames: [],
          livenessComplete: false
        });
        onClose();
      }, 'image/jpeg', 0.8);
    }
  };

  // Face detection (basic implementation)
  useEffect(() => {
    if (videoRef.current && isRecording) {
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      const detectFace = () => {
        if (video.readyState >= 2) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0);
          
          // Simple brightness-based face detection
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const data = imageData.data;
          let totalBrightness = 0;
          
          for (let i = 0; i < data.length; i += 4) {
            const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
            totalBrightness += brightness;
          }
          
          const avgBrightness = totalBrightness / (data.length / 4);
          setFaceDetected(avgBrightness > 50 && avgBrightness < 200);
        }
      };
      
      const interval = setInterval(detectFace, 500);
      return () => clearInterval(interval);
    }
  }, [isRecording]);

  return (
    <div className="liveness-camera-container">
      <div className="camera-overlay">
        <div className="camera-header">
          <h3>🔒 Liveness Detection</h3>
          <button onClick={onClose} className="close-button">✕</button>
        </div>
        
        <div className="camera-content">
          <div className="video-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="camera-video"
            />
            
            {/* Face detection overlay */}
            <div className={`face-overlay ${faceDetected ? 'face-detected' : 'no-face'}`}>
              <div className="face-circle">
                {faceDetected ? '😊' : '👤'}
              </div>
            </div>
            
            {/* Progress indicator */}
            {isRecording && (
              <div className="progress-overlay">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: `${((currentStep + 1) / livenessSteps.length) * 100}%` 
                    }}
                  />
                </div>
                <span className="step-indicator">
                  Step {currentStep + 1} of {livenessSteps.length}
                </span>
              </div>
            )}
          </div>
          
          <div className="instructions-panel">
            <div className="instruction-text">
              {instructions || 'Initializing camera...'}
            </div>
            
            {countdown > 0 && (
              <div className="countdown">
                {countdown}
              </div>
            )}
            
            <div className="status-indicators">
              <div className={`status-item ${faceDetected ? 'active' : ''}`}>
                👤 Face Detected
              </div>
              <div className={`status-item ${isRecording ? 'active' : ''}`}>
                📹 Recording
              </div>
            </div>
          </div>
          
          <div className="camera-controls">
            {!isRecording ? (
              <>
                <button 
                  onClick={startLivenessDetection}
                  className="start-button"
                  disabled={!faceDetected}
                >
                  🚀 Start Liveness Check
                </button>
                <button 
                  onClick={handleManualCapture}
                  className="manual-button"
                >
                  📸 Manual Capture
                </button>
              </>
            ) : (
              <div className="recording-info">
                <div className="recording-dot"></div>
                Following instructions...
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Hidden canvas for frame capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
};

export default LivenessCamera;
