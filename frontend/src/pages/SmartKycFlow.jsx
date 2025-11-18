import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const SmartKycFlow = () => {
  const [currentStep, setCurrentStep] = useState('document_type');
  const [documentType, setDocumentType] = useState(null);
  const [idFile, setIdFile] = useState(null);
  const [idPreview, setIdPreview] = useState(null);
  const [selfieFile, setSelfieFile] = useState(null);
  const [selfiePreview, setSelfiePreview] = useState(null);
  const [aiGuidance, setAiGuidance] = useState('');
  const [imageQuality, setImageQuality] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [realTimeInsights, setRealTimeInsights] = useState([]);
  
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const documentTypes = [
    { 
      id: 'aadhaar', 
      name: 'Aadhaar Card', 
      icon: '🆔', 
      description: 'Government-issued unique identity',
      aiTips: 'Ensure all 12 digits are visible and not blurred'
    },
    { 
      id: 'passport', 
      name: 'Passport', 
      icon: '📘', 
      description: 'International travel document',
      aiTips: 'Machine-readable zone (MRZ) must be clearly visible'
    },
    { 
      id: 'driving_license', 
      name: "Driver's License", 
      icon: '🚗', 
      description: 'State-issued driving permit',
      aiTips: 'Both front and back sides may be required'
    }
  ];

  useEffect(() => {
    // Simulate real-time AI guidance
    const guidanceMessages = [
      'AI is ready to guide you through the process',
      'Smart document detection is active',
      'Fraud prevention algorithms are running',
      'Quality assessment is in progress'
    ];
    
    let index = 0;
    const interval = setInterval(() => {
      setRealTimeInsights(prev => [
        ...prev.slice(-2), // Keep last 2 insights
        {
          id: Date.now(),
          message: guidanceMessages[index % guidanceMessages.length],
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      index++;
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const analyzeImageQuality = async (file) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const quality = {
          brightness: Math.random() * 40 + 60, // 60-100
          sharpness: Math.random() * 30 + 70, // 70-100
          resolution: Math.random() * 20 + 80, // 80-100
          overall: Math.random() * 20 + 80 // 80-100
        };
        resolve(quality);
      }, 1000);
    });
  };

  const handleDocumentSelect = (docType) => {
    setDocumentType(docType);
    setAiGuidance(`Great choice! The AI will optimize verification for ${docType.name}. ${docType.aiTips}`);
    setCurrentStep('document_upload');
  };

  const handleFileSelect = async (e, type) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    setAiGuidance('AI is analyzing the image...');

    try {
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        if (type === 'id') {
          setIdPreview(event.target.result);
          setIdFile(file);
        } else {
          setSelfiePreview(event.target.result);
          setSelfieFile(file);
        }
      };
      reader.readAsDataURL(file);

      // Analyze quality
      const quality = await analyzeImageQuality(file);
      setImageQuality(quality);

      // Provide AI guidance based on quality
      if (quality.overall > 90) {
        setAiGuidance('✅ Excellent quality! Your document is perfectly captured.');
      } else if (quality.overall > 75) {
        setAiGuidance('✅ Good quality. The AI can process this effectively.');
      } else if (quality.brightness < 70) {
        setAiGuidance('💡 Try capturing in better lighting for optimal results.');
      } else if (quality.sharpness < 80) {
        setAiGuidance('📷 Please hold steady and ensure the document is in focus.');
      } else {
        setAiGuidance('⚠️ Consider retaking for better verification accuracy.');
      }

      // Add real-time insight
      setRealTimeInsights(prev => [...prev, {
        id: Date.now(),
        message: `${type === 'id' ? 'Document' : 'Selfie'} quality: ${quality.overall.toFixed(1)}%`,
        timestamp: new Date().toLocaleTimeString()
      }]);

    } finally {
      setIsProcessing(false);
    }
  };

  const processVerification = async () => {
    setIsProcessing(true);
    setCurrentStep('processing');
    
    const steps = [
      'Classifying document type with CNN model',
      'Extracting text using advanced OCR',
      'Detecting forgery with Vision Transformers', 
      'Matching faces using FaceNet model',
      'Performing liveness detection',
      'Cross-referencing with PEP/AML databases',
      'Computing risk score with explainable AI'
    ];

    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      setRealTimeInsights(prev => [...prev, {
        id: Date.now(),
        message: steps[i],
        timestamp: new Date().toLocaleTimeString()
      }]);
    }

    // Generate mock verification result
    const result = {
      status: 'completed',
      score: Math.random() * 20 + 80,
      riskLevel: Math.random() > 0.7 ? 'low' : 'medium',
      faceMatch: Math.random() > 0.2,
      livenessCheck: Math.random() > 0.1,
      documentAuthenticity: Math.random() > 0.15,
      extractedData: {
        name: 'Aarav Kumar',
        documentNumber: 'XXXX XXXX 1234',
        dateOfBirth: '1995-08-15',
        expiryDate: '2030-08-15'
      },
      aiExplanation: {
        confidence: (Math.random() * 15 + 85).toFixed(1),
        factors: [
          'Document structure matches official templates',
          'No signs of digital manipulation detected',
          'Face biometrics successfully matched',
          'Liveness detection passed all checks'
        ]
      }
    };

    setVerificationResult(result);
    setCurrentStep('result');
    setIsProcessing(false);
  };

  const renderDocumentTypeSelection = () => (
    <div className="smart-kyc-section">
      <div className="step-header">
        <h2>🎯 Choose Your Document</h2>
        <p>Our AI will optimize the verification process based on your document type</p>
      </div>
      
      <div className="document-grid">
        {documentTypes.map((doc) => (
          <div 
            key={doc.id}
            className="document-card"
            onClick={() => handleDocumentSelect(doc)}
          >
            <div className="doc-icon">{doc.icon}</div>
            <h3>{doc.name}</h3>
            <p className="doc-description">{doc.description}</p>
            <div className="ai-tip">
              <span className="tip-icon">💡</span>
              <span className="tip-text">{doc.aiTips}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDocumentUpload = () => (
    <div className="smart-kyc-section">
      <div className="step-header">
        <h2>📷 Smart Document Capture</h2>
        <p>AI-powered guidance for perfect document capture</p>
      </div>

      <div className="upload-grid">
        <div className="upload-section">
          <h3>📄 Upload {documentType.name}</h3>
          <input 
            type="file" 
            ref={fileInputRef}
            accept="image/*"
            onChange={(e) => handleFileSelect(e, 'id')}
            style={{display: 'none'}}
          />
          
          <div 
            className="smart-upload-area"
            onClick={() => fileInputRef.current?.click()}
          >
            {idPreview ? (
              <div className="preview-container">
                <img src={idPreview} alt="Document preview" className="preview-image" />
                <div className="quality-overlay">
                  {imageQuality && (
                    <div className="quality-metrics">
                      <div className="metric">
                        <span>Quality: {imageQuality.overall.toFixed(0)}%</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="upload-prompt">
                <div className="upload-icon">📷</div>
                <p>Click to capture or upload</p>
                <span className="upload-hint">AI will guide you in real-time</span>
              </div>
            )}
          </div>

          {idPreview && (
            <div className="upload-actions">
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="retake-btn"
              >
                📷 Retake
              </button>
              <button 
                onClick={() => setCurrentStep('selfie')}
                className="continue-btn"
                disabled={!imageQuality || imageQuality.overall < 70}
              >
                Continue ✨
              </button>
            </div>
          )}
        </div>

        {currentStep === 'selfie' && (
          <div className="upload-section">
            <h3>🤳 Liveness Check</h3>
            <input 
              type="file" 
              accept="image/*"
              onChange={(e) => handleFileSelect(e, 'selfie')}
              style={{display: 'none'}}
              id="selfie-input"
            />
            
            <div 
              className="smart-upload-area selfie-area"
              onClick={() => document.getElementById('selfie-input')?.click()}
            >
              {selfiePreview ? (
                <div className="preview-container">
                  <img src={selfiePreview} alt="Selfie preview" className="preview-image" />
                </div>
              ) : (
                <div className="upload-prompt">
                  <div className="upload-icon">🤳</div>
                  <p>Take a selfie</p>
                  <span className="upload-hint">Look directly at the camera</span>
                </div>
              )}
            </div>

            {selfiePreview && (
              <button 
                onClick={processVerification}
                className="verify-btn"
                disabled={isProcessing}
              >
                {isProcessing ? '🔄 Processing...' : '🚀 Verify Now'}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );

  const renderProcessing = () => (
    <div className="smart-kyc-section processing-section">
      <div className="step-header">
        <h2>🤖 AI Verification in Progress</h2>
        <p>Multiple AI models are analyzing your documents</p>
      </div>

      <div className="processing-visualization">
        <div className="ai-brain">🧠</div>
        <div className="processing-steps">
          <div className="step-indicator active">Document Classification</div>
          <div className="step-indicator active">OCR Extraction</div>
          <div className="step-indicator active">Forgery Detection</div>
          <div className="step-indicator active">Face Matching</div>
          <div className="step-indicator">Risk Assessment</div>
        </div>
      </div>
    </div>
  );

  const renderResult = () => (
    <div className="smart-kyc-section result-section">
      <div className="step-header">
        <h2>✅ Verification Complete</h2>
        <p>Your identity has been successfully verified using AI</p>
      </div>

      {verificationResult && (
        <div className="result-dashboard">
          <div className="result-score">
            <div className="score-circle">
              <span className="score-number">{verificationResult.score.toFixed(0)}</span>
              <span className="score-label">Confidence Score</span>
            </div>
            <div className="risk-badge low">
              🛡️ {verificationResult.riskLevel} Risk
            </div>
          </div>

          <div className="result-details">
            <div className="detail-card">
              <h4>🔍 Extracted Information</h4>
              <div className="extracted-data">
                <div className="data-row">
                  <span>Name:</span>
                  <span>{verificationResult.extractedData.name}</span>
                </div>
                <div className="data-row">
                  <span>Document:</span>
                  <span>{verificationResult.extractedData.documentNumber}</span>
                </div>
                <div className="data-row">
                  <span>DOB:</span>
                  <span>{verificationResult.extractedData.dateOfBirth}</span>
                </div>
              </div>
            </div>

            <div className="detail-card">
              <h4>🤖 AI Explanation</h4>
              <div className="ai-explanation">
                <p>Confidence: {verificationResult.aiExplanation.confidence}%</p>
                <ul className="ai-factors">
                  {verificationResult.aiExplanation.factors.map((factor, index) => (
                    <li key={index}>✓ {factor}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="result-actions">
            <button 
              onClick={() => navigate('/dashboard')}
              className="dashboard-btn"
            >
              📊 View Dashboard
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="retry-btn"
            >
              🔄 Verify Another
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="smart-kyc-container">
      <div className="kyc-header">
        <button 
          onClick={() => navigate('/dashboard')}
          className="back-btn"
        >
          ← Dashboard
        </button>
        <h1>🚀 AI-Powered KYC Verification</h1>
      </div>

      <div className="kyc-layout">
        <div className="main-content">
          {currentStep === 'document_type' && renderDocumentTypeSelection()}
          {(currentStep === 'document_upload' || currentStep === 'selfie') && renderDocumentUpload()}
          {currentStep === 'processing' && renderProcessing()}
          {currentStep === 'result' && renderResult()}
        </div>

        <div className="ai-sidebar">
          <div className="ai-guidance-panel">
            <h3>🤖 AI Assistant</h3>
            <div className="guidance-message">
              {aiGuidance || 'AI is ready to guide you through verification'}
            </div>
            {isProcessing && (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <span>AI Processing...</span>
              </div>
            )}
          </div>

          <div className="insights-panel">
            <h4>⚡ Real-time Insights</h4>
            <div className="insights-list">
              {realTimeInsights.slice(-3).map((insight) => (
                <div key={insight.id} className="insight-item">
                  <span className="insight-message">{insight.message}</span>
                  <span className="insight-time">{insight.timestamp}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartKycFlow;
