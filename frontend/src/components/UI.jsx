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
  const getRiskColor = (level) => {
    switch (level) {
      case 'Low':
        return '#10b981'
      case 'Medium':
        return '#f59e0b'
      case 'High':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  return (
    <div className="result-card">
      <div className="result-header">
        <h2>Verification Complete</h2>
      </div>

      <div className="result-score">
        <div className="score-circle" style={{ borderColor: getRiskColor(result.risk_level) }}>
          <div className="score-value">{result.score}</div>
          <div className="score-label">Score</div>
        </div>
        <div className="risk-badge" style={{ backgroundColor: getRiskColor(result.risk_level) }}>
          {result.risk_level} Risk
        </div>
      </div>

      <div className="result-details">
        <div className="detail-group">
          <h3>Document Information</h3>
          <dl>
            <dt>Type:</dt>
            <dd className="capitalize">{result.document_type}</dd>
            {result.extracted_fields.name && (
              <>
                <dt>Name:</dt>
                <dd>{result.extracted_fields.name}</dd>
              </>
            )}
            {result.extracted_fields.document_number && (
              <>
                <dt>Document No:</dt>
                <dd>{result.extracted_fields.document_number}</dd>
              </>
            )}
            {result.extracted_fields.dob && (
              <>
                <dt>DOB:</dt>
                <dd>{result.extracted_fields.dob}</dd>
              </>
            )}
          </dl>
        </div>

        <div className="detail-group">
          <h3>Verification Results</h3>
          <dl>
            <dt>Face Match:</dt>
            <dd className={result.face_match.match ? 'success' : 'error'}>
              {result.face_match.match ? '✓ Matched' : '✗ No Match'}
              {result.face_match.similarity && (
                <span className="sub-text">
                  {' '}
                  (Similarity: {(result.face_match.similarity * 100).toFixed(1)}%)
                </span>
              )}
            </dd>
            <dt>Liveness:</dt>
            <dd className={result.liveness.passed ? 'success' : 'error'}>
              {result.liveness.passed ? '✓ Passed' : '✗ Failed'}
            </dd>
            {result.validations.aadhaar_format_ok !== undefined && (
              <>
                <dt>Aadhaar Format:</dt>
                <dd className={result.validations.aadhaar_format_ok ? 'success' : 'error'}>
                  {result.validations.aadhaar_format_ok ? '✓ Valid' : '✗ Invalid'}
                </dd>
              </>
            )}
            {result.validations.mrz_ok !== undefined && (
              <>
                <dt>MRZ:</dt>
                <dd className={result.validations.mrz_ok ? 'success' : 'error'}>
                  {result.validations.mrz_ok ? '✓ Valid' : '✗ Invalid'}
                </dd>
              </>
            )}
          </dl>
        </div>

        <div className="detail-group">
          <h3>Score Breakdown (Explainability)</h3>
          <div className="explainability">
            {result.explainability && (
              <>
                <div className="component">
                  <span className="label">Face Match:</span>
                  <div className="bar-container">
                    <div
                      className="bar"
                      style={{
                        width: `${result.explainability.face_component}%`,
                        backgroundColor: '#3b82f6',
                      }}
                    ></div>
                  </div>
                  <span className="value">
                    {result.explainability.face_component.toFixed(1)}%
                  </span>
                </div>
                <div className="component">
                  <span className="label">Liveness:</span>
                  <div className="bar-container">
                    <div
                      className="bar"
                      style={{
                        width: `${result.explainability.liveness_component}%`,
                        backgroundColor: '#8b5cf6',
                      }}
                    ></div>
                  </div>
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
