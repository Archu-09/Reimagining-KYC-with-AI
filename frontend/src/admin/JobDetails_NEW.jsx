import React, { useEffect, useState } from 'react'
import api from './api'

export default function JobDetails({ jobId, onClose }) {
  const [job, setJob] = useState(null)
  const [elaUrl, setElaUrl] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [reviewAction, setReviewAction] = useState('')
  const [reviewComments, setReviewComments] = useState('')

  useEffect(() => {
    if (!jobId) return
    let mounted = true
    
    setLoading(true)
    setError(null)
    
    api.fetchJob(jobId)
      .then((data) => {
        if (!mounted) return
        console.log('📄 Job details loaded:', data)
        setJob(data)
      })
      .catch((err) => {
        console.error('❌ Failed to load job:', err)
        setError(err.message || 'Failed to load job')
      })
      .finally(() => setLoading(false))

    // Load ELA analysis
    api.fetchEla(jobId)
      .then((res) => {
        console.log('🔍 ELA analysis loaded:', res)
        setElaUrl(res)
      })
      .catch((err) => {
        console.log('⚠️ ELA analysis not available:', err.message)
      })

    return () => (mounted = false)
  }, [jobId])

  const handleReview = async (action) => {
    try {
      await api.reviewJob(jobId, action, reviewComments)
      console.log(`✅ Review submitted: ${action}`)
      setReviewAction('')
      setReviewComments('')
      // Refresh job data
      const updatedJob = await api.fetchJob(jobId)
      setJob(updatedJob)
    } catch (err) {
      console.error('❌ Review submission failed:', err)
      alert('Failed to submit review: ' + err.message)
    }
  }

  const getStatusBadge = (status) => {
    const classes = {
      'completed': 'status-completed',
      'pending_review': 'status-pending', 
      'failed': 'status-failed',
      'pending': 'status-pending'
    }
    return `status-badge ${classes[status] || 'status-pending'}`
  }

  const getRiskScoreClass = (score) => {
    if (score >= 80) return 'score-low'
    if (score >= 60) return 'score-medium'
    return 'score-high'
  }

  if (!jobId) {
    return (
      <div className="empty">
        <p>Select a verification job to view details</p>
      </div>
    )
  }
  
  if (loading) {
    return (
      <div className="job-details">
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
          <p>Loading job details...</p>
        </div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="job-details">
        <div className="error" style={{ textAlign: 'center', padding: '2rem', color: '#dc2626' }}>
          <p>❌ {error}</p>
          <button onClick={onClose} className="btn btn-secondary">Close</button>
        </div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="job-details">
        <div className="empty">
          <p>Job not found</p>
        </div>
      </div>
    )
  }

  const result = job.result || {}
  
  return (
    <div className="job-details">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3>Job Details: {job.id}</h3>
        <button onClick={onClose} className="btn btn-secondary">✕ Close</button>
      </div>

      <div className="job-info">
        {/* Basic Information */}
        <div className="info-section">
          <h4>📋 Basic Information</h4>
          <div className="info-grid">
            <span className="info-label">Status:</span>
            <span className={getStatusBadge(job.status)}>{job.status.replace('_', ' ')}</span>
            
            <span className="info-label">Created:</span>
            <span className="info-value">{new Date(job.created_at).toLocaleString()}</span>
            
            <span className="info-label">User Email:</span>
            <span className="info-value">{job.user_email}</span>
            
            <span className="info-label">Document Type:</span>
            <span className="info-value">{job.document_type}</span>
            
            {job.processing_time_ms && (
              <>
                <span className="info-label">Processing Time:</span>
                <span className="info-value">{job.processing_time_ms}ms</span>
              </>
            )}
          </div>
        </div>

        {/* Verification Results */}
        {result.verification_id && (
          <div className="info-section">
            <h4>🎯 Verification Results</h4>
            <div className="info-grid">
              <span className="info-label">Overall Score:</span>
              <div className="score-display">
                <div className={`score-circle ${getRiskScoreClass(result.risk_assessment?.overall_score * 100)}`}>
                  {Math.round(result.risk_assessment?.overall_score * 100)}
                </div>
                <span>{result.risk_assessment?.risk_level} risk</span>
              </div>
              
              <span className="info-label">Face Match:</span>
              <span className="info-value">
                {result.biometric?.face_match?.match ? '✅' : '❌'} 
                {result.biometric?.face_match?.similarity && ` (${Math.round(result.biometric.face_match.similarity * 100)}%)`}
              </span>
              
              <span className="info-label">Liveness:</span>
              <span className="info-value">
                {result.biometric?.liveness?.passed ? '✅' : '❌'} 
                {result.biometric?.liveness?.score && ` (Score: ${Math.round(result.biometric.liveness.score * 100)})`}
              </span>
              
              <span className="info-label">Document Valid:</span>
              <span className="info-value">
                {result.document?.validation?.format_valid ? '✅' : '❌'} Format
              </span>
            </div>
          </div>
        )}

        {/* Extracted Data */}
        {result.document?.extracted_data && (
          <div className="info-section">
            <h4>📄 Extracted Information</h4>
            <div className="info-grid">
              {Object.entries(result.document.extracted_data).map(([key, value]) => (
                <React.Fragment key={key}>
                  <span className="info-label">{key.replace(/_/g, ' ')}:</span>
                  <span className="info-value">{value}</span>
                </React.Fragment>
              ))}
            </div>
          </div>
        )}

        {/* Decision Factors */}
        {result.explainability?.decision_factors && (
          <div className="info-section">
            <h4>💡 AI Decision Factors</h4>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
              {result.explainability.decision_factors.map((factor, idx) => (
                <li key={idx} style={{ marginBottom: '0.25rem' }}>{factor}</li>
              ))}
            </ul>
          </div>
        )}

        {/* ELA Analysis */}
        {elaUrl && (
          <div className="info-section">
            <h4>🔍 Forgery Detection (ELA)</h4>
            <div className="info-grid">
              <span className="info-label">Forgery Risk:</span>
              <span className="info-value">{elaUrl.ela_analysis?.forgery_probability ? 
                `${Math.round(elaUrl.ela_analysis.forgery_probability * 100)}%` : 'N/A'}</span>
              
              <span className="info-label">Assessment:</span>
              <span className="info-value">{elaUrl.ela_analysis?.overall_assessment || 'Processing...'}</span>
            </div>
          </div>
        )}

        {/* Files */}
        {job.files && (
          <div className="info-section">
            <h4>📁 Uploaded Files</h4>
            <div className="info-grid">
              <span className="info-label">ID Document:</span>
              <span className="info-value">{job.files.id_image}</span>
              
              <span className="info-label">Selfie:</span>
              <span className="info-value">{job.files.selfie}</span>
            </div>
          </div>
        )}

        {/* Audit Log */}
        {job.audit_log && (
          <div className="info-section">
            <h4>📝 Audit Trail</h4>
            <div style={{ fontSize: '0.8rem', maxHeight: '150px', overflowY: 'auto' }}>
              {job.audit_log.map((entry, idx) => (
                <div key={idx} style={{ marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid #f1f5f9' }}>
                  <div style={{ fontWeight: '500', color: '#374151' }}>
                    {new Date(entry.timestamp).toLocaleString()}: {entry.action}
                  </div>
                  <div style={{ color: '#6b7280' }}>{entry.details}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Admin Actions */}
      {job.status === 'pending_review' && (
        <div className="admin-actions">
          <div style={{ flex: 1 }}>
            <textarea
              placeholder="Review comments..."
              value={reviewComments}
              onChange={(e) => setReviewComments(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '0.875rem',
                fontFamily: 'inherit',
                resize: 'vertical',
                minHeight: '60px'
              }}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button 
              onClick={() => handleReview('approve')} 
              className="btn btn-primary"
              style={{ minWidth: '80px' }}
            >
              ✅ Approve
            </button>
            <button 
              onClick={() => handleReview('reject')} 
              className="btn btn-danger"
              style={{ minWidth: '80px' }}
            >
              ❌ Reject
            </button>
            <button 
              onClick={() => handleReview('flag')} 
              className="btn btn-secondary"
              style={{ minWidth: '80px' }}
            >
              🚩 Flag
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
