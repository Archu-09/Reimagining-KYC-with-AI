import React, { useState } from 'react'
import { analyzeImageQuality } from './utils/imageQuality'
import {
  LoadingSpinner,
  ProgressBar,
  ImageQualityFeedback,
  ErrorAlert,
  ResultCard,
  FileUploadBox,
} from './components/UI'
import LivenessCamera from './components/LivenessCamera'

// KYC Steps
const STEPS = {
  DOCUMENT_TYPE: 'document_type',
  DOCUMENT_UPLOAD: 'document_upload',
  DOCUMENT_REVIEW: 'document_review',
  LIVENESS: 'liveness',
  VERIFICATION: 'verification',
  RESULT: 'result',
}

const DOCUMENT_TYPES = [
  { id: 'aadhaar', label: 'Aadhaar Card', icon: '🇮🇳' },
  { id: 'passport', label: 'Passport', icon: '📕' },
  { id: 'driving_license', label: "Driver's License", icon: '🎫' },
  { id: 'pan_card', label: 'PAN Card', icon: '🆔' },
]

const VERIFICATION_STEPS = [
  'Analyzing documents',
  'Extracting information',
  'Detecting forgery',
  'Face matching',
  'Liveness verification',
  'Computing risk score',
]

export default function App() {
  // State management
  const [currentStep, setCurrentStep] = useState(STEPS.DOCUMENT_TYPE)
  const [documentType, setDocumentType] = useState(null)
  const [idFile, setIdFile] = useState(null)
  const [idPreview, setIdPreview] = useState(null)
  const [idQuality, setIdQuality] = useState(null)
  const [idUploadError, setIdUploadError] = useState(null)
  const [selfieFile, setSelfieFile] = useState(null)
  const [selfiePreview, setSelfiePreview] = useState(null)
  const [selfieQuality, setSelfieQuality] = useState(null)
  const [livenessAttestation, setLivenessAttestation] = useState(null)
  const [livenessError, setLivenessError] = useState(null)
  const [showLiveCamera, setShowLiveCamera] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [verificationStep, setVerificationStep] = useState(0)

  // Handlers
  const selectDocumentType = (typeId) => {
    setDocumentType(typeId)
    setCurrentStep(STEPS.DOCUMENT_UPLOAD)
  }

  const handleImageSelect = async (e, type) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      if (type === 'id') setIdUploadError('Please select a valid image file')
      else setLivenessError('Please select a valid image file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      if (type === 'id') setIdUploadError('File size must be less than 10MB')
      else setLivenessError('File size must be less than 10MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      if (type === 'id') {
        setIdPreview(event.target.result)
        setIdFile(file)
      } else {
        setSelfiePreview(event.target.result)
        setSelfieFile(file)
      }
    }
    reader.readAsDataURL(file)

    try {
      const quality = await analyzeImageQuality(file)
      if (type === 'id') {
        setIdQuality(quality)
        setIdUploadError(null)
      } else {
        setSelfieQuality(quality)
        setLivenessError(null)
      }
    } catch (err) {
      console.error('Quality analysis failed:', err)
    }
  }

  const handleLiveCapture = async (captureData) => {
    try {
      let file, attestation = null;
      
      // Handle enhanced liveness capture data
      if (captureData.mainImage && captureData.livenessFrames) {
        file = new File([captureData.mainImage], 'selfie.jpg', { type: 'image/jpeg' });
        attestation = {
          captured_at: new Date().toISOString(),
          method: captureData.livenessComplete ? 'advanced_liveness' : 'live_camera',
          liveness_complete: captureData.livenessComplete,
          frames_captured: captureData.livenessFrames?.length || 0,
          attestation_score: captureData.livenessComplete ? 0.95 : 0.7
        };
      } else {
        // Fallback for simple file capture
        file = captureData;
        attestation = {
          captured_at: new Date().toISOString(),
          method: 'live_camera',
          attestation_score: 0.7
        };
      }
      
      const reader = new FileReader();
      reader.onload = (event) => {
        setSelfiePreview(event.target.result);
        setSelfieFile(file);
      }
      reader.readAsDataURL(file);

      const quality = await analyzeImageQuality(file);
      setSelfieQuality(quality);
      
      // Enhanced attestation with quality
      attestation.quality_score = quality.score;
      setLivenessAttestation(attestation);
      setLivenessError(null);
      
    } catch (err) {
      console.error('Quality analysis failed:', err);
      setLivenessError('Failed to process live capture');
    }

    setShowLiveCamera(false);
  }

  const canProceedDocumentReview = () => {
    return (
      idFile &&
      !idUploadError &&
      (idQuality?.quality === 'good' || idQuality?.score > 50)
    )
  }

  const canProceedLiveness = () => {
    return (
      selfieFile &&
      !livenessError &&
      (selfieQuality?.quality === 'good' || selfieQuality?.score > 50)
    )
  }

  const simulateVerificationProgress = async () => {
    for (let i = 1; i <= VERIFICATION_STEPS.length; i++) {
      setVerificationStep(i)
      await new Promise((resolve) => setTimeout(resolve, 800))
    }
  }

  const submitVerification = async (e) => {
    e?.preventDefault()
    if (!canProceedDocumentReview() || !canProceedLiveness()) {
      setError('Please ensure all images have acceptable quality.')
      return
    }

    setLoading(true)
    setError(null)
    setVerificationStep(0)
    setResult(null)
    setCurrentStep(STEPS.VERIFICATION)

    try {
      const form = new FormData()
      form.append('id_image', idFile)
      form.append('selfie', selfieFile)
      form.append('document_type', documentType)
      if (livenessAttestation) {
        form.append('liveness_attestation', JSON.stringify(livenessAttestation))
      }

      const progressPromise = simulateVerificationProgress()
      
      // Debug: Log what we're sending
      console.log('🚀 Sending verification request...')
      console.log('Form data entries:')
      for (let pair of form.entries()) {
        if (pair[1] instanceof File) {
          console.log(`${pair[0]}: File(${pair[1].name}, ${pair[1].size} bytes, ${pair[1].type})`)
        } else {
          console.log(`${pair[0]}: ${pair[1]}`)
        }
      }
      
      const res = await fetch('http://localhost:8000/api/verify', { 
        method: 'POST', 
        body: form,
        // Don't set Content-Type header - let browser set it with boundary for multipart/form-data
      })
      
      console.log('📥 Response received:', {
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries())
      })
      
      // Check if response is ok before trying to parse JSON
      if (!res.ok) {
        const errorText = await res.text()
        console.error('❌ Verification failed:', res.status, errorText)
        setError(`Verification failed: ${res.status} ${res.statusText}`)
        setCurrentStep(STEPS.LIVENESS)
        return
      }
      
      // Get response text first to debug
      const responseText = await res.text()
      console.log('📄 Raw response:', responseText.substring(0, 200) + '...')
      
      let json
      try {
        json = JSON.parse(responseText)
        console.log('✅ Successfully parsed JSON:', json)
      } catch (parseError) {
        console.error('❌ JSON parse error:', parseError)
        console.error('Raw response text:', responseText)
        
        // Provide more helpful error message
        let errorMessage = 'Invalid response from server.'
        if (responseText.includes('<!DOCTYPE html>')) {
          errorMessage = 'Server returned HTML instead of JSON. Check if backend is running correctly.'
        } else if (responseText.trim() === '') {
          errorMessage = 'Server returned empty response. Check backend logs.'
        } else if (responseText.includes('404')) {
          errorMessage = 'API endpoint not found. Check if backend server is running on port 8000.'
        } else {
          errorMessage = `Server response parse error: ${parseError.message}`
        }
        
        setError(errorMessage)
        setCurrentStep(STEPS.LIVENESS)
        return
      }
      
      await progressPromise

      setResult(json)
      setCurrentStep(STEPS.RESULT)
    } catch (err) {
      console.error('Verification error:', err)
      await progressPromise // Ensure progress completes
      setError(err.message || 'Network error. Please check your connection.')
      setCurrentStep(STEPS.LIVENESS)
    } finally {
      setLoading(false)
      setVerificationStep(0)
    }
  }

  const handleRetry = () => {
    setError(null)
    setResult(null)
    setIdFile(null)
    setSelfieFile(null)
    setIdPreview(null)
    setSelfiePreview(null)
    setIdQuality(null)
    setSelfieQuality(null)
    setDocumentType(null)
    setCurrentStep(STEPS.DOCUMENT_TYPE)
    setShowLiveCamera(false)
  }

  const documentTypeLabel = DOCUMENT_TYPES.find((d) => d.id === documentType)?.label || ''

  // Render functions
  const renderDocumentTypeSelection = () => (
    <div className="kyc-section">
      <h2>Step 1: Select Document Type</h2>
      <p className="section-hint">Choose the identity document you want to verify</p>

      <div className="document-type-grid">
        {DOCUMENT_TYPES.map((doc) => (
          <button
            key={doc.id}
            onClick={() => selectDocumentType(doc.id)}
            className="document-type-card"
          >
            <div className="doc-icon">{doc.icon}</div>
            <div className="doc-label">{doc.label}</div>
          </button>
        ))}
      </div>
    </div>
  )

  const renderDocumentUpload = () => (
    <div className="kyc-section">
      <div className="section-header">
        <button
          className="btn-back"
          onClick={() => {
            setDocumentType(null)
            setCurrentStep(STEPS.DOCUMENT_TYPE)
          }}
        >
          ← Back
        </button>
        <h2>Step 2: Upload {documentTypeLabel}</h2>
        <div></div>
      </div>

      <div className="upload-container">
        <div className="upload-box-wrapper">
          <h3>📄 {documentTypeLabel}</h3>
          <p className="upload-hint">
            Ensure the entire document is visible, well-lit, and clearly readable
          </p>
          <FileUploadBox
            label={`Upload ${documentTypeLabel}`}
            onFileSelect={(e) => handleImageSelect(e, 'id')}
            error={idUploadError}
            preview={idPreview}
            quality={idQuality}
          />
          {canProceedDocumentReview() && (
            <button
              className="btn btn-primary btn-full"
              onClick={() => setCurrentStep(STEPS.DOCUMENT_REVIEW)}
            >
              ✓ Document Looks Good
            </button>
          )}
        </div>
      </div>
    </div>
  )

  const renderDocumentReview = () => (
    <div className="kyc-section">
      <div className="section-header">
        <button
          className="btn-back"
          onClick={() => setCurrentStep(STEPS.DOCUMENT_UPLOAD)}
        >
          ← Back
        </button>
        <h2>Step 3: Review {documentTypeLabel}</h2>
        <div></div>
      </div>

      <div className="review-container">
        <div className="review-image">
          <img src={idPreview} alt="Document preview" />
          {idQuality && (
            <div className={`quality-badge quality-${idQuality.quality}`}>
              {idQuality.quality === 'good' ? '✓ Good' : '⚠ Fair'} Quality
            </div>
          )}
        </div>

        <div className="review-checklist">
          <h3>Document Checklist</h3>
          <ul>
            <li>
              <input type="checkbox" defaultChecked disabled /> All corners visible
            </li>
            <li>
              <input type="checkbox" defaultChecked disabled /> Text is clear and readable
            </li>
            <li>
              <input type="checkbox" defaultChecked disabled /> No glare or shadows
            </li>
            <li>
              <input type="checkbox" defaultChecked disabled /> Photo is recent and in color
            </li>
          </ul>

          <div className="review-actions">
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentStep(STEPS.DOCUMENT_UPLOAD)}
            >
              ✎ Re-upload
            </button>
            <button
              className="btn btn-primary"
              onClick={() => setCurrentStep(STEPS.LIVENESS)}
            >
              ✓ Proceed to Liveness
            </button>
          </div>
        </div>
      </div>
    </div>
  )

  const renderLiveness = () => (
    <div className="kyc-section">
      <div className="section-header">
        <button
          className="btn-back"
          onClick={() => setCurrentStep(STEPS.DOCUMENT_REVIEW)}
        >
          ← Back
        </button>
        <h2>Step 4: Liveness Verification</h2>
        <div></div>
      </div>

      {showLiveCamera ? (
        <LivenessCamera
          onCapture={handleLiveCapture}
          onClose={() => setShowLiveCamera(false)}
        />
      ) : (
        <div className="liveness-container">
          {!selfieFile ? (
            <div className="liveness-prompt">
              <div className="liveness-icon">📸</div>
              <h3>Take a Selfie</h3>
              <p>
                Position your face clearly in the frame. Ensure good lighting and a neutral background.
              </p>

              <div className="liveness-tips">
                <h4>Tips for best results:</h4>
                <ul>
                  <li>✓ Face the camera directly</li>
                  <li>✓ Good lighting (avoid backlighting)</li>
                  <li>✓ Neutral expression</li>
                  <li>✓ No glasses or hats (if possible)</li>
                  <li>✓ Recent photo (same day/outfit)</li>
                </ul>
              </div>

              <button
                className="btn btn-primary btn-full btn-lg"
                onClick={() => setShowLiveCamera(true)}
              >
                🎥 Start Camera
              </button>

              <div className="divider">OR</div>

              <div className="upload-box-wrapper">
                <FileUploadBox
                  label="Upload Selfie"
                  onFileSelect={(e) => handleImageSelect(e, 'selfie')}
                  error={livenessError}
                  preview={null}
                  quality={null}
                />
              </div>
            </div>
          ) : (
            <div className="liveness-review">
              <div className="review-image">
                <img src={selfiePreview} alt="Selfie preview" />
                {selfieQuality && (
                  <div className={`quality-badge quality-${selfieQuality.quality}`}>
                    {selfieQuality.quality === 'good' ? '✓ Good' : '⚠ Fair'} Quality
                  </div>
                )}
              </div>

              <div className="review-actions">
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setSelfieFile(null)
                    setSelfiePreview(null)
                    setSelfieQuality(null)
                  }}
                >
                  ✎ Retake
                </button>
                <button className="btn btn-primary" onClick={submitVerification}>
                  ✓ Verify Identity
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )

  const renderVerification = () => (
    <div className="kyc-section">
      <h2>Verification in Progress</h2>
      <div className="verification-progress">
        <ProgressBar
          step={verificationStep}
          totalSteps={VERIFICATION_STEPS.length}
        />
        <LoadingSpinner
          step={verificationStep}
          totalSteps={VERIFICATION_STEPS.length}
        />
        <div className="steps-info">
          {VERIFICATION_STEPS.map((step, idx) => (
            <div
              key={idx}
              className={`step-info ${idx < verificationStep ? 'completed' : ''} ${
                idx === verificationStep - 1 ? 'active' : ''
              }`}
            >
              {idx < verificationStep - 1 ? '✓' : idx === verificationStep - 1 ? '→' : '○'}{' '}
              {step}
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderResult = () => (
    <div className="kyc-section">
      <ResultCard result={result} />
      <div className="result-actions">
        <button className="btn btn-primary" onClick={handleRetry}>
          ↻ Verify Another Person
        </button>
      </div>
    </div>
  )

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🔐 KYC Verification</h1>
        <p>Fast, secure, and transparent identity verification powered by AI</p>
      </header>

      <main className="app-main">
        {error && (
          <ErrorAlert
            error={error}
            onRetry={
              currentStep === STEPS.VERIFICATION ? () => setCurrentStep(STEPS.LIVENESS) : null
            }
            onDismiss={() => setError(null)}
          />
        )}

        {currentStep === STEPS.DOCUMENT_TYPE && renderDocumentTypeSelection()}
        {currentStep === STEPS.DOCUMENT_UPLOAD && renderDocumentUpload()}
        {currentStep === STEPS.DOCUMENT_REVIEW && renderDocumentReview()}
        {currentStep === STEPS.LIVENESS && renderLiveness()}
        {currentStep === STEPS.VERIFICATION && renderVerification()}
        {currentStep === STEPS.RESULT && renderResult()}
      </main>

      <footer className="app-footer">
        <p>🔒 Your data is encrypted and processed securely | Privacy Policy | Terms of Service</p>
      </footer>
    </div>
  )
}
