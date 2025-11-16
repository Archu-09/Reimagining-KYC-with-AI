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

const VERIFICATION_STEPS = [
  'Analyzing images',
  'Classifying document',
  'Extracting information',
  'Matching faces',
  'Validating document',
  'Computing risk score',
]

export default function App() {
  const [idFile, setIdFile] = useState(null)
  const [selfieFile, setSelfieFile] = useState(null)
  const [idPreview, setIdPreview] = useState(null)
  const [selfiePreview, setSelfiePreview] = useState(null)
  const [idQuality, setIdQuality] = useState(null)
  const [selfieQuality, setSelfieQuality] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [uploadErrors, setUploadErrors] = useState({ id: null, selfie: null })

  const handleImageSelect = async (e, type) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setUploadErrors((prev) => ({ ...prev, [type]: 'Please select a valid image file' }))
      return
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setUploadErrors((prev) => ({ ...prev, [type]: 'File size must be less than 10MB' }))
      return
    }

    // Create preview
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

    // Analyze quality
    try {
      const quality = await analyzeImageQuality(file)
      if (type === 'id') {
        setIdQuality(quality)
      } else {
        setSelfieQuality(quality)
      }
      setUploadErrors((prev) => ({ ...prev, [type]: null }))
    } catch (err) {
      console.error('Quality analysis failed:', err)
    }
  }

  const canSubmit = () => {
    return (
      idFile &&
      selfieFile &&
      !uploadErrors.id &&
      !uploadErrors.selfie &&
      (idQuality?.quality === 'good' || idQuality?.score > 50) &&
      (selfieQuality?.quality === 'good' || selfieQuality?.score > 50)
    )
  }

  const simulateProgress = async () => {
    // Simulate step-by-step progress
    for (let i = 1; i <= VERIFICATION_STEPS.length; i++) {
      setCurrentStep(i)
      await new Promise((resolve) => setTimeout(resolve, 800))
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    if (!canSubmit()) {
      setError('Please ensure both images have acceptable quality and are selected.')
      return
    }

    setLoading(true)
    setError(null)
    setCurrentStep(0)
    setResult(null)

    try {
      const form = new FormData()
      form.append('id_image', idFile)
      form.append('selfie', selfieFile)

      // Simulate progress
      const progressPromise = simulateProgress()

      // Make request
      const res = await fetch('/api/verify', { method: 'POST', body: form })
      const json = await res.json()

      // Wait for progress animation to finish
      await progressPromise

      if (!res.ok) {
        setError(json.detail || 'Verification failed. Please try again.')
      } else {
        setResult(json)
      }
    } catch (err) {
      setError(err.message || 'Network error. Please check your connection and try again.')
    } finally {
      setLoading(false)
      setCurrentStep(0)
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
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🔐 Reimagining KYC with AI</h1>
        <p>Fast, secure, and transparent identity verification</p>
      </header>

      <main className="app-main">
        {result ? (
          <>
            <ResultCard result={result} />
            <div className="action-buttons">
              <button className="btn btn-primary" onClick={handleRetry}>
                ↻ Verify Another Person
              </button>
            </div>
          </>
        ) : loading ? (
          <div className="loading-section">
            <ProgressBar step={currentStep} totalSteps={VERIFICATION_STEPS.length} />
            <LoadingSpinner step={currentStep} totalSteps={VERIFICATION_STEPS.length} />
            <div className="steps-info">
              {VERIFICATION_STEPS.map((step, idx) => (
                <div
                  key={idx}
                  className={`step-info ${idx < currentStep ? 'completed' : ''} ${
                    idx === currentStep - 1 ? 'active' : ''
                  }`}
                >
                  {idx < currentStep - 1 ? '✓' : idx === currentStep - 1 ? '→' : '○'} {step}
                </div>
              ))}
            </div>
          </div>
        ) : error ? (
          <>
            <ErrorAlert
              error={error}
              onRetry={handleRetry}
              onDismiss={() => setError(null)}
            />
          </>
        ) : (
          <form onSubmit={submit} className="upload-form">
            <div className="upload-section">
              <FileUploadBox
                label="ID Image (Aadhaar, Passport, or Driver's License)"
                onFileSelect={(e) => handleImageSelect(e, 'id')}
                error={uploadErrors.id}
                preview={idPreview}
                quality={idQuality}
              />

              <FileUploadBox
                label="Selfie (Recent Photo)"
                onFileSelect={(e) => handleImageSelect(e, 'selfie')}
                error={uploadErrors.selfie}
                preview={selfiePreview}
                quality={selfieQuality}
              />
            </div>

            <div className="submit-section">
              <button type="submit" disabled={!canSubmit()} className="btn btn-verify">
                ✓ Verify Identity
              </button>
              {!canSubmit() && (
                <p className="submit-hint">
                  {!idFile || !selfieFile
                    ? 'Please select both images'
                    : 'Images must have acceptable quality'}
                </p>
              )}
            </div>
          </form>
        )}
      </main>

      <footer className="app-footer">
        <p>🔒 Your data is encrypted and processed securely | Privacy Policy | Terms of Service</p>
      </footer>
    </div>
  )
}
