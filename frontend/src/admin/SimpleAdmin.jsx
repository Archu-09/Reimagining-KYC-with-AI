import React, { useState, useEffect } from 'react';

const SimpleAdmin = () => {
  const [jobs, setJobs] = useState([]);
  const [records, setRecords] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedView, setSelectedView] = useState('dashboard');
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE = 'http://localhost:8000/api/admin';

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [jobsRes, recordsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/jobs`),
        fetch(`${API_BASE}/records`),
        fetch(`${API_BASE}/stats`)
      ]);

      const jobsData = await jobsRes.json();
      const recordsData = await recordsRes.json();
      const statsData = await statsRes.json();

      setJobs(jobsData);
      setRecords(recordsData.records);
      setStats(statsData);
    } catch (err) {
      setError('Failed to load admin data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString();
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return '#48bb78';
      case 'MEDIUM': return '#ed8936';
      case 'HIGH': return '#f56565';
      default: return '#718096';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#48bb78';
      case 'pending': return '#ed8936';
      case 'failed': return '#f56565';
      case 'approved': return '#38a169';
      case 'rejected': return '#e53e3e';
      case 'processing': return '#3182ce';
      default: return '#718096';
    }
  };

  const approveJob = async (jobId) => {
    try {
      await fetch(`${API_BASE}/jobs/${jobId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approve: true, comments: 'Approved by admin' })
      });
      fetchAllData();
    } catch (err) {
      console.error('Failed to approve job:', err);
    }
  };

  const rejectJob = async (jobId) => {
    try {
      await fetch(`${API_BASE}/jobs/${jobId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approve: false, comments: 'Rejected by admin' })
      });
      fetchAllData();
    } catch (err) {
      console.error('Failed to reject job:', err);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #667eea',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          <h3>Loading Admin Panel...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'red' }}>
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={fetchAllData} style={{
          padding: '10px 20px',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer'
        }}>
          🔄 Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        background: 'white',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #2d3748 0%, #4a5568 100%)',
          color: 'white',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <h1 style={{ margin: 0, fontSize: '2.5rem' }}>🛡️ KYC Admin Panel</h1>
          <p style={{ margin: '0.5rem 0 0', opacity: 0.9 }}>
            Monitor and manage KYC verification processes
          </p>
        </div>

        {/* Navigation */}
        <div style={{
          display: 'flex',
          borderBottom: '2px solid #e2e8f0',
          background: '#f7fafc'
        }}>
          {[
            { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
            { id: 'jobs', label: '📋 Verification Jobs', icon: '📋' },
            { id: 'records', label: '📂 KYC Records', icon: '📂' }
          ].map(view => (
            <button
              key={view.id}
              onClick={() => setSelectedView(view.id)}
              style={{
                padding: '1rem 2rem',
                border: 'none',
                background: selectedView === view.id ? 'white' : 'transparent',
                borderBottom: selectedView === view.id ? '3px solid #667eea' : '3px solid transparent',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: selectedView === view.id ? 'bold' : 'normal',
                color: selectedView === view.id ? '#667eea' : '#4a5568'
              }}
            >
              {view.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{ padding: '2rem' }}>
          {selectedView === 'dashboard' && stats && (
            <div>
              <h2 style={{ marginBottom: '2rem', color: '#2d3748' }}>📊 System Overview</h2>
              
              {/* Stats Cards */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1.5rem',
                marginBottom: '2rem'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 0.5rem', fontSize: '2rem' }}>{stats.jobs.total}</h3>
                  <p style={{ margin: 0, opacity: 0.9 }}>Total Jobs</p>
                </div>
                
                <div style={{
                  background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
                  color: 'white',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 0.5rem', fontSize: '2rem' }}>{stats.jobs.completed}</h3>
                  <p style={{ margin: 0, opacity: 0.9 }}>Completed</p>
                </div>
                
                <div style={{
                  background: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
                  color: 'white',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 0.5rem', fontSize: '2rem' }}>{stats.jobs.pending}</h3>
                  <p style={{ margin: 0, opacity: 0.9 }}>Pending</p>
                </div>
                
                <div style={{
                  background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
                  color: 'white',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 0.5rem', fontSize: '2rem' }}>{stats.jobs.failed}</h3>
                  <p style={{ margin: 0, opacity: 0.9 }}>Failed</p>
                </div>
              </div>

              {/* Records Overview */}
              <div style={{
                background: '#f7fafc',
                padding: '1.5rem',
                borderRadius: '12px'
              }}>
                <h3 style={{ margin: '0 0 1rem', color: '#2d3748' }}>📂 KYC Records Summary</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#48bb78' }}>
                      {stats.records.low_risk}
                    </div>
                    <div style={{ color: '#4a5568' }}>Low Risk</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ed8936' }}>
                      {stats.records.medium_risk}
                    </div>
                    <div style={{ color: '#4a5568' }}>Medium Risk</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f56565' }}>
                      {stats.records.high_risk}
                    </div>
                    <div style={{ color: '#4a5568' }}>High Risk</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#667eea' }}>
                      {stats.records.average_score}
                    </div>
                    <div style={{ color: '#4a5568' }}>Avg Score</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedView === 'jobs' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ margin: 0, color: '#2d3748' }}>📋 Verification Jobs ({jobs.length})</h2>
                <button onClick={fetchAllData} style={{
                  padding: '8px 16px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}>
                  🔄 Refresh
                </button>
              </div>
              
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white' }}>
                  <thead>
                    <tr style={{ background: '#f7fafc' }}>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>ID</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Status</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Created</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Score</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Risk</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map(job => (
                      <tr key={job.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '12px' }}>{job.id}</td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            fontWeight: 'bold',
                            color: 'white',
                            background: getStatusColor(job.status)
                          }}>
                            {job.status}
                          </span>
                        </td>
                        <td style={{ padding: '12px', fontSize: '0.9rem' }}>
                          {formatDate(job.created_at)}
                        </td>
                        <td style={{ padding: '12px' }}>
                          {job.result?.confidence_score?.toFixed(2) || 'N/A'}
                        </td>
                        <td style={{ padding: '12px' }}>
                          {job.result?.risk_assessment && (
                            <span style={{
                              padding: '4px 8px',
                              borderRadius: '8px',
                              fontSize: '0.8rem',
                              fontWeight: 'bold',
                              color: 'white',
                              background: getRiskColor(job.result.risk_assessment)
                            }}>
                              {job.result.risk_assessment}
                            </span>
                          )}
                        </td>
                        <td style={{ padding: '12px' }}>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              onClick={() => setSelectedJob(job)}
                              style={{
                                padding: '4px 8px',
                                background: '#3182ce',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '0.8rem'
                              }}
                            >
                              👁️ View
                            </button>
                            {job.status !== 'approved' && job.status !== 'rejected' && (
                              <>
                                <button
                                  onClick={() => approveJob(job.id)}
                                  style={{
                                    padding: '4px 8px',
                                    background: '#48bb78',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '0.8rem'
                                  }}
                                >
                                  ✅ Approve
                                </button>
                                <button
                                  onClick={() => rejectJob(job.id)}
                                  style={{
                                    padding: '4px 8px',
                                    background: '#f56565',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '0.8rem'
                                  }}
                                >
                                  ❌ Reject
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {selectedView === 'records' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ margin: 0, color: '#2d3748' }}>📂 KYC Records ({records.length})</h2>
                <button onClick={fetchAllData} style={{
                  padding: '8px 16px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}>
                  🔄 Refresh
                </button>
              </div>
              
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white' }}>
                  <thead>
                    <tr style={{ background: '#f7fafc' }}>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>ID</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Name</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Document</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Score</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Risk Level</th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map(record => (
                      <tr key={record.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '12px' }}>{record.id}</td>
                        <td style={{ padding: '12px', fontWeight: 'bold' }}>{record.name}</td>
                        <td style={{ padding: '12px' }}>
                          <div style={{ fontSize: '0.9rem' }}>
                            <div style={{ fontWeight: 'bold' }}>{record.document_type}</div>
                            <div style={{ color: '#718096', fontSize: '0.8rem' }}>{record.document_number}</div>
                          </div>
                        </td>
                        <td style={{ padding: '12px' }}>
                          <div style={{
                            padding: '4px 8px',
                            borderRadius: '8px',
                            background: record.score >= 0.9 ? '#48bb78' : record.score >= 0.8 ? '#ed8936' : '#f56565',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '0.9rem',
                            display: 'inline-block'
                          }}>
                            {record.score?.toFixed(2)}
                          </div>
                        </td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            fontWeight: 'bold',
                            color: 'white',
                            background: getRiskColor(record.risk_level)
                          }}>
                            {record.risk_level}
                          </span>
                        </td>
                        <td style={{ padding: '12px' }}>
                          <button
                            onClick={() => setSelectedRecord(record)}
                            style={{
                              padding: '4px 8px',
                              background: '#3182ce',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              fontSize: '0.8rem'
                            }}
                          >
                            👁️ View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Job Details Modal */}
      {selectedJob && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, color: '#2d3748' }}>📋 Job Details - ID: {selectedJob.id}</h3>
              <button
                onClick={() => setSelectedJob(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#718096'
                }}
              >
                ✕
              </button>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Status:</strong> 
              <span style={{
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '0.8rem',
                fontWeight: 'bold',
                color: 'white',
                background: getStatusColor(selectedJob.status),
                marginLeft: '8px'
              }}>
                {selectedJob.status}
              </span>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Created:</strong> {formatDate(selectedJob.created_at)}
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <strong>Updated:</strong> {formatDate(selectedJob.updated_at)}
            </div>
            
            {selectedJob.result && (
              <div style={{
                background: '#f7fafc',
                padding: '1rem',
                borderRadius: '8px',
                marginTop: '1rem'
              }}>
                <h4 style={{ margin: '0 0 1rem', color: '#2d3748' }}>🔍 Verification Results</h4>
                <div style={{ display: 'grid', gap: '0.5rem' }}>
                  <div><strong>Confidence Score:</strong> {selectedJob.result.confidence_score?.toFixed(2)}</div>
                  <div><strong>Risk Assessment:</strong> 
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '8px',
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      color: 'white',
                      background: getRiskColor(selectedJob.result.risk_assessment),
                      marginLeft: '8px'
                    }}>
                      {selectedJob.result.risk_assessment}
                    </span>
                  </div>
                  <div><strong>Processing Time:</strong> {selectedJob.result.processing_time}s</div>
                  {selectedJob.result.flags && selectedJob.result.flags.length > 0 && (
                    <div>
                      <strong>Flags:</strong>
                      <div style={{ marginTop: '4px' }}>
                        {selectedJob.result.flags.map((flag, idx) => (
                          <span key={idx} style={{
                            padding: '2px 6px',
                            background: '#fed7d7',
                            color: '#c53030',
                            borderRadius: '4px',
                            fontSize: '0.8rem',
                            marginRight: '4px'
                          }}>
                            {flag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Record Details Modal */}
      {selectedRecord && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, color: '#2d3748' }}>📂 Record Details - {selectedRecord.name}</h3>
              <button
                onClick={() => setSelectedRecord(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#718096'
                }}
              >
                ✕
              </button>
            </div>
            
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div><strong>ID:</strong> {selectedRecord.id}</div>
              <div><strong>Name:</strong> {selectedRecord.name}</div>
              <div><strong>Document Type:</strong> {selectedRecord.document_type}</div>
              <div><strong>Document Number:</strong> {selectedRecord.document_number}</div>
              <div>
                <strong>Score:</strong> 
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '8px',
                  background: selectedRecord.score >= 0.9 ? '#48bb78' : selectedRecord.score >= 0.8 ? '#ed8936' : '#f56565',
                  color: 'white',
                  fontWeight: 'bold',
                  marginLeft: '8px'
                }}>
                  {selectedRecord.score?.toFixed(2)}
                </span>
              </div>
              <div>
                <strong>Risk Level:</strong> 
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '0.8rem',
                  fontWeight: 'bold',
                  color: 'white',
                  background: getRiskColor(selectedRecord.risk_level),
                  marginLeft: '8px'
                }}>
                  {selectedRecord.risk_level}
                </span>
              </div>
            </div>
            
            {selectedRecord.meta && (
              <div style={{
                background: '#f7fafc',
                padding: '1rem',
                borderRadius: '8px',
                marginTop: '1rem'
              }}>
                <h4 style={{ margin: '0 0 1rem', color: '#2d3748' }}>📊 Biometric Analysis</h4>
                <div style={{ display: 'grid', gap: '0.5rem' }}>
                  <div><strong>Face Match Score:</strong> {selectedRecord.meta.face_match_score?.toFixed(2)}</div>
                  <div><strong>Document Quality:</strong> {selectedRecord.meta.document_quality}</div>
                  <div><strong>Liveness Check:</strong> 
                    <span style={{
                      color: selectedRecord.meta.liveness_passed ? '#48bb78' : '#f56565',
                      fontWeight: 'bold',
                      marginLeft: '8px'
                    }}>
                      {selectedRecord.meta.liveness_passed ? '✅ Passed' : '❌ Failed'}
                    </span>
                  </div>
                  <div><strong>Biometric Confidence:</strong> {selectedRecord.meta.biometric_confidence?.toFixed(2)}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SimpleAdmin;
