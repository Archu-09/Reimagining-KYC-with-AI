import React, { useState, useEffect } from 'react';

const SimpleAdmin = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);

  // Load jobs on component mount
  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      console.log('🔄 Fetching admin jobs...');
      const response = await fetch('http://localhost:8000/api/admin/jobs');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Jobs loaded:', data.length);
      setJobs(data);
    } catch (err) {
      console.error('❌ Error fetching jobs:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchJobDetails = async (jobId) => {
    try {
      console.log('🔍 Fetching job details for:', jobId);
      const response = await fetch(`http://localhost:8000/api/admin/jobs/${jobId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch job details: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Job details loaded:', data);
      setSelectedJob(data);
    } catch (err) {
      console.error('❌ Error fetching job details:', err);
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>🔄 Loading Admin Panel...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={fetchJobs} style={{ padding: '10px 20px' }}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ marginBottom: '30px' }}>
        <h1>👨‍💼 KYC Admin Panel</h1>
        <p style={{ color: '#666' }}>Manage and review verification jobs</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Jobs List */}
        <div>
          <h2>📋 Verification Jobs ({jobs.length})</h2>
          <div style={{ border: '1px solid #ddd', borderRadius: '8px', overflow: 'hidden' }}>
            {jobs.map((job, index) => (
              <div 
                key={job.id}
                onClick={() => fetchJobDetails(job.id)}
                style={{
                  padding: '15px',
                  borderBottom: index < jobs.length - 1 ? '1px solid #eee' : 'none',
                  cursor: 'pointer',
                  backgroundColor: selectedJob?.id === job.id ? '#f0f8ff' : 'white',
                  '&:hover': { backgroundColor: '#f9f9f9' }
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#f9f9f9'}
                onMouseLeave={(e) => e.target.style.backgroundColor = selectedJob?.id === job.id ? '#f0f8ff' : 'white'}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {job.id}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ 
                    backgroundColor: job.status === 'completed' ? '#28a745' : job.status === 'pending_review' ? '#ffc107' : '#6c757d',
                    color: 'white',
                    padding: '2px 8px',
                    borderRadius: '4px'
                  }}>
                    {job.status}
                  </span>
                  <span>{job.document_type}</span>
                  <span>Score: {job.result?.score || 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Job Details */}
        <div>
          <h2>📄 Job Details</h2>
          {selectedJob ? (
            <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
              <h3>🆔 {selectedJob.id}</h3>
              
              <div style={{ marginBottom: '15px' }}>
                <strong>Status:</strong> 
                <span style={{
                  marginLeft: '10px',
                  backgroundColor: selectedJob.status === 'completed' ? '#28a745' : '#ffc107',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '4px'
                }}>
                  {selectedJob.status}
                </span>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>Created:</strong> {new Date(selectedJob.created_at).toLocaleString()}
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>Document Type:</strong> {selectedJob.document_type}
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>User:</strong> {selectedJob.user_email}
              </div>

              {selectedJob.result && (
                <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                  <h4>📊 Verification Results</h4>
                  <div><strong>Overall Score:</strong> {selectedJob.result.risk_assessment?.overall_score ? Math.round(selectedJob.result.risk_assessment.overall_score * 100) : selectedJob.result.score}</div>
                  <div><strong>Risk Level:</strong> {selectedJob.result.risk_assessment?.risk_level || 'N/A'}</div>
                  <div><strong>Face Match:</strong> {selectedJob.result.biometric?.face_match?.match ? '✅ Yes' : '❌ No'} 
                    {selectedJob.result.biometric?.face_match?.similarity && ` (${Math.round(selectedJob.result.biometric.face_match.similarity * 100)}%)`}
                  </div>
                  <div><strong>Liveness:</strong> {selectedJob.result.biometric?.liveness?.passed ? '✅ Passed' : '❌ Failed'}</div>
                </div>
              )}

              {selectedJob.audit_log && (
                <div style={{ marginTop: '20px' }}>
                  <h4>📝 Audit Log</h4>
                  {selectedJob.audit_log.map((entry, i) => (
                    <div key={i} style={{ 
                      fontSize: '0.9rem', 
                      padding: '5px 0', 
                      borderBottom: '1px solid #eee' 
                    }}>
                      <strong>{entry.timestamp}:</strong> {entry.action} - {entry.details}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div style={{ 
              border: '1px solid #ddd', 
              borderRadius: '8px', 
              padding: '40px', 
              textAlign: 'center', 
              color: '#666' 
            }}>
              Select a job from the list to view details
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h3>🛠️ Admin Actions</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={fetchJobs}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🔄 Refresh Jobs
          </button>
          <button 
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
            onClick={() => alert('Export functionality would be implemented here')}
          >
            📤 Export Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default SimpleAdmin;
