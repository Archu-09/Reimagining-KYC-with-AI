import React, { useState } from 'react'
import JobList from './JobList'
import JobDetails from './JobDetails'

export default function Admin() {
  const [selectedJob, setSelectedJob] = useState(null)

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h1>Admin — Verification Jobs</h1>
      </header>
      <main className="admin-main">
        <div className="left-pane">
          <JobList onSelect={(id) => setSelectedJob(id)} />
        </div>
        <div className="right-pane">
          {selectedJob ? (
            <JobDetails jobId={selectedJob} onClose={() => setSelectedJob(null)} />
          ) : (
            <div className="empty">Select a job to view details</div>
          )}
        </div>
      </main>
    </div>
  )
}
