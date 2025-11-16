import React, { useEffect, useState } from 'react'
import api from './api'

export default function JobDetails({ jobId, onClose }) {
  const [job, setJob] = useState(null)
  const [elaUrl, setElaUrl] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!jobId) return
    let mounted = true
    api.fetchJob(jobId)
      .then((data) => {
        if (!mounted) return
        setJob(data)
      })
      .catch((err) => setError(err.message || 'Failed to load job'))
      .finally(() => setLoading(false))

    api.fetchEla(jobId)
      .then((res) => setElaUrl(res))
      .catch(() => {})

    return () => (mounted = false)
  }, [jobId])

  if (!jobId) return null
  if (loading) return <div>Loading job...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="job-details">
      <button className="btn btn-close" onClick={onClose}>
        Close
      </button>
      <h3>Job #{job.id}</h3>
      <div className="job-section">
        <div className="images">
          <div>
            <h4>ID Image</h4>
            <img src={job.meta?.id_uri || job.meta?.id_path} alt="id" style={{ maxWidth: 300 }} />
          </div>
          <div>
            <h4>Selfie</h4>
            <img src={job.meta?.selfie_uri || job.meta?.selfie_path} alt="selfie" style={{ maxWidth: 200 }} />
          </div>
        </div>

        <div className="fields">
          <h4>Extracted Fields</h4>
          <pre>{JSON.stringify(job.result?.extracted_fields || job.result?.fields || {}, null, 2)}</pre>
        </div>

        <div className="forensics">
          <h4>Forensics</h4>
          <pre>{JSON.stringify(job.result?.forgery || job.result?.forgery_report || {}, null, 2)}</pre>
          {elaUrl && (
            <div>
              <h5>ELA Image</h5>
              <img src={elaUrl} alt="ela" style={{ maxWidth: 400 }} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
