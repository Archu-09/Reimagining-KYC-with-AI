import React, { useEffect, useState } from 'react'
import api from './api'

export default function JobList({ onSelect }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    console.log('📊 JobList: Fetching jobs from API...')
    
    api.fetchJobs()
      .then((data) => {
        console.log('📊 JobList: API response:', data)
        if (!mounted) return
        setJobs(data || [])
      })
      .catch((err) => {
        console.error('❌ JobList: API error:', err)
        setError(err.message || 'Failed to load')
      })
      .finally(() => {
        console.log('📊 JobList: Loading complete')
        setLoading(false)
      })
    return () => (mounted = false)
  }, [])

  if (loading) return <div>Loading jobs...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="admin-job-list">
      <h2>Verification Jobs</h2>
      <table className="job-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Created</th>
            <th>Risk</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td>{job.id}</td>
              <td>{job.status}</td>
              <td>{job.created_at}</td>
              <td>{job.result?.score ?? '-'}</td>
              <td>
                <button onClick={() => onSelect(job.id)} className="btn btn-small">
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
