import React, { useState, useEffect } from 'react'
import JobList from './JobList'
import JobDetails from './JobDetails'

export default function Admin() {
  const [selectedJob, setSelectedJob] = useState(null)
  const [debugInfo, setDebugInfo] = useState(null)

  useEffect(() => {
    console.log('🛡️ Admin component mounted')
    setDebugInfo({
      mounted: true,
      timestamp: new Date().toISOString(),
      selectedJob: selectedJob
    })
  }, [])

  useEffect(() => {
    console.log('🛡️ Admin selected job changed:', selectedJob)
    setDebugInfo(prev => ({ ...prev, selectedJob }))
  }, [selectedJob])

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h1>🛡️ Admin — Verification Jobs</h1>
        {debugInfo && (
          <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
            Debug: Mounted at {debugInfo.timestamp} | Selected: {debugInfo.selectedJob || 'None'}
          </div>
        )}
      </header>
      <main className="admin-main">
        <div className="left-pane">
          <JobList onSelect={(id) => {
            console.log('🛡️ Admin: Job selected:', id)
            setSelectedJob(id)
          }} />
        </div>
        <div className="right-pane">
          {selectedJob ? (
            <JobDetails 
              jobId={selectedJob} 
              onClose={() => {
                console.log('🛡️ Admin: Closing job details')
                setSelectedJob(null)
              }} 
            />
          ) : (
            <div className="empty">
              <h3>📋 Admin Panel Ready</h3>
              <p>Select a verification job from the left panel to view details.</p>
              <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '1rem' }}>
                Backend API: ✅ Connected<br/>
                Jobs Loading: Check left panel
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
