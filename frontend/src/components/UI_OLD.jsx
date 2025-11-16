import React from 'react'

export const LoadingSpinner = ({ step, totalSteps }) => (
  <div className="loading-container">
    <div className="spinner"></div>
    <p className="loading-text">
      Verifying your identity...
      {step && totalSteps && ` (Step ${step}/${totalSteps})`}
    </p>
  </div>
)

export const ProgressBar = ({ step, totalSteps }) => (
  <div className="progress-container">
    <div className="progress-bar">
      <div
        className="progress-fill"
        style={{ width: `${(step / totalSteps) * 100}%` }}
      ></div>
    </div>
    <div className="progress-steps">
      {Array.from({ length: totalSteps }).map((_, i) => (
        <div
          key={i}
          className={`step-dot ${i < step ? 'active' : ''} ${
            i === step - 1 ? 'current' : ''
          }`}
        >
          {i < step - 1 ? '✓' : i === step - 1 ? '●' : i + 1}
        </div>
      ))}
    </div>
  </div>
)

export const ImageQualityFeedback = ({ quality, issues, score }) => {
  if (!issues || issues.length === 0) {
    return (
      <div className="quality-feedback success">
        <span className="icon">✓</span>
        <p>Image quality is excellent!</p>
      </div>
    )
  }

  return (
    <div className={`quality-feedback ${quality}`}>
      <div className="quality-score">Quality Score: {score}/100</div>
      <div className="issues-list">
        {issues.map((issue, idx) => (
          <div key={idx} className={`issue ${issue.severity}`}>
            <span className="issue-message">{issue.message}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export const ErrorAlert = ({ error, onRetry, onDismiss }) => (
  <div className="error-alert">
    <div className="error-content">
      <span className="error-icon">⚠️</span>
      <div className="error-details">
        <h3>Verification Failed</h3>
        <p>{error}</p>
      </div>
      <button className="close-btn" onClick={onDismiss}>×</button>
    </div>
    <div className="error-actions">
      {onRetry && <button onClick={onRetry} className="btn btn-secondary">Retry</button>}
      <button onClick={onDismiss} className="btn btn-primary">Dismiss</button>
    </div>
  </div>
)

export const ResultCard = ({ result }) => {
  console.log('🎯 ResultCard received:', result)
  
  if (!result) {
    return (
      <div className="result-card">
        <div className="result-header">
          <h2>⚠️ No Results Available</h2>
          <p>Verification data is missing. Please try again.</p>
        </div>
      </div>
    )
  }

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return '#10b981'
      case 'medium':
        return '#f59e0b'
      case 'high':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const overallScore = Math.round((result.risk_assessment?.overall_score || 0.85) * 100)
  const riskLevel = result.risk_assessment?.risk_level || 'unknown'

  return (
    <div className="result-card">
      <div className="result-header">
        <div className="verification-status">
          <div className="status-icon">✅</div>
          <div>
            <h2>Verification Complete</h2>
            <p className="verification-id">ID: {result.verification_id}</p>
            <p className="timestamp">Completed: {new Date(result.timestamp).toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="result-score">
        <div className="score-circle" style={{ borderColor: getRiskColor(riskLevel) }}>
          <div className="score-value">{overallScore}</div>
          <div className="score-label">Score</div>
        </div>
        <div className="risk-badge" style={{ backgroundColor: getRiskColor(riskLevel) }}>
          {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk
        </div>
      </div>

      <div className="result-details">
        <div className="detail-group">
          <h3>📄 Document Information</h3>
          <dl>
            <dt>Type:</dt>
            <dd className="capitalize">{result.document?.type || 'Unknown'}</dd>
            {result.document?.extracted_data?.name && (
              <>
                <dt>Name:</dt>
                <dd>{result.document.extracted_data.name}</dd>
              </>
            )}
            {result.document?.extracted_data?.document_number && (
              <>
                <dt>Document No:</dt>
                <dd>{result.document.extracted_data.document_number}</dd>
              </>
            )}
            {result.document?.extracted_data?.date_of_birth && (
              <>
                <dt>Date of Birth:</dt>
                <dd>{result.document.extracted_data.date_of_birth}</dd>
              </>
            )}
            {result.document?.extracted_data?.address && (
              <>
                <dt>Address:</dt>
                <dd>{result.document.extracted_data.address}</dd>
              </>
            )}
          </dl>
        </div>

        <div className="detail-group">
          <h3>🔐 Verification Results</h3>
          <dl>
            <dt>Face Match:</dt>
            <dd className={result.biometric?.face_match?.match ? 'success' : 'error'}>
              {result.biometric?.face_match?.match ? '✅ Matched' : '❌ No Match'}
              {result.biometric?.face_match?.similarity && (
                <span className="sub-text">
                  {' '}
                  ({Math.round(result.biometric.face_match.similarity * 100)}% similarity)
                </span>
              )}
            </dd>
            <dt>Liveness Check:</dt>
            <dd className={result.biometric?.liveness?.passed ? 'success' : 'error'}>
              {result.biometric?.liveness?.passed ? '✅ Passed' : '❌ Failed'}
              {result.biometric?.liveness?.score && (
                <span className="sub-text">
                  {' '}
                  (Score: {Math.round(result.biometric.liveness.score * 100)})
                </span>
              )}
            </dd>
            <dt>Document Format:</dt>
            <dd className={result.document?.validation?.format_valid ? 'success' : 'error'}>
              {result.document?.validation?.format_valid ? '✅ Valid' : '❌ Invalid'}
            </dd>
            <dt>Document Authenticity:</dt>
            <dd className={result.document?.validation?.checksum_valid ? 'success' : 'error'}>
              {result.document?.validation?.checksum_valid ? '✅ Authentic' : '❌ Suspicious'}
            </dd>
          </dl>
        </div>

        <div className="detail-group">
          <h3>📊 Risk Assessment</h3>
          <div className="risk-factors">
            {result.risk_assessment?.factors && Object.entries(result.risk_assessment.factors).map(([key, value]) => (
              <div key={key} className="risk-factor">
                <span className="factor-name">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </span>
                <div className="factor-bar">
                  <div 
                    className="factor-fill" 
                    style={{ 
                      width: `${value * 100}%`,
                      backgroundColor: value > 0.8 ? '#10b981' : value > 0.6 ? '#f59e0b' : '#ef4444'
                    }}
                  ></div>
                  <span className="factor-value">{Math.round(value * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {result.explainability?.decision_factors && (
          <div className="detail-group">
            <h3>💡 Decision Factors</h3>
            <ul className="decision-factors">
              {result.explainability.decision_factors.map((factor, idx) => (
                <li key={idx}>✓ {factor}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
                  <span className="value">
                    {result.explainability.liveness_component.toFixed(1)}%
                  </span>
                </div>
                <div className="component">
                  <span className="label">Validation:</span>
                  <div className="bar-container">
                    <div
                      className="bar"
                      style={{
                        width: `${result.explainability.validation_component}%`,
                        backgroundColor: '#06b6d4',
                      }}
                    ></div>
                  </div>
                  <span className="value">
                    {result.explainability.validation_component.toFixed(1)}%
                  </span>
                </div>
                <div className="component">
                  <span className="label">OCR Confidence:</span>
                  <div className="bar-container">
                    <div
                      className="bar"
                      style={{
                        width: `${result.explainability.ocr_component}%`,
                        backgroundColor: '#f59e0b',
                      }}
                    ></div>
                  </div>
                  <span className="value">
                    {result.explainability.ocr_component.toFixed(1)}%
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="result-actions">
        <button className="btn btn-primary">Download Report</button>
        <button className="btn btn-secondary">Verify Again</button>
      </div>
    </div>
  )
}

export const FileUploadBox = ({ label, onFileSelect, error, preview, quality }) => (
  <div className="upload-box">
    <label className="upload-label">{label}</label>
    <div className="upload-area">
      <input
        type="file"
        accept="image/*"
        onChange={onFileSelect}
        className="file-input"
        id={label}
      />
      <label htmlFor={label} className="upload-placeholder">
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt={label} className="preview-image" />
          </div>
        ) : (
          <>
            <span className="upload-icon">📸</span>
            <p>Click or drag image here</p>
            <span className="upload-hint">PNG, JPG, up to 10MB</span>
          </>
        )}
      </label>
    </div>
    {quality && <ImageQualityFeedback {...quality} />}
    {error && <div className="upload-error">{error}</div>}
  </div>
)
