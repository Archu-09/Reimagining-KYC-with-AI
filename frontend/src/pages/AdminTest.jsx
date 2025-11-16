import React, { useState, useEffect } from 'react'

const AdminTest = () => {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [testResults, setTestResults] = useState({})

  useEffect(() => {
    console.log('🧪 AdminTest: Component mounted, starting tests...')
    runTests()
  }, [])

  const runTests = async () => {
    const results = {}
    
    // Test 1: API Connectivity
    try {
      console.log('📡 Testing API connectivity...')
      const response = await fetch('http://localhost:8000/api/admin/jobs')
      results.apiConnectivity = {
        success: response.ok,
        status: response.status,
        statusText: response.statusText
      }
      
      if (response.ok) {
        const data = await response.json()
        results.dataFetch = {
          success: true,
          jobCount: data.length,
          firstJob: data[0] || null
        }
        setJobs(data)
      }
    } catch (err) {
      console.error('❌ API test failed:', err)
      results.apiConnectivity = { success: false, error: err.message }
      setError(err.message)
    }
    
    // Test 2: OAuth API
    try {
      console.log('🔑 Testing OAuth API...')
      const oauthResponse = await fetch('http://localhost:8000/api/auth/oauth/google/mock-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      results.oauth = {
        success: oauthResponse.ok,
        status: oauthResponse.status
      }
      
      if (oauthResponse.ok) {
        const oauthData = await oauthResponse.json()
        results.oauth.user = oauthData.user
      }
    } catch (err) {
      console.error('❌ OAuth test failed:', err)
      results.oauth = { success: false, error: err.message }
    }
    
    setTestResults(results)
    setLoading(false)
    console.log('🧪 Tests complete:', results)
  }

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>🧪 Admin Panel & OAuth Test</h2>
        <p>⏳ Running tests...</p>
      </div>
    )
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h2>🧪 Admin Panel & OAuth Test Results</h2>
      
      <div style={{ marginBottom: '2rem' }}>
        <h3>📊 Admin API Test</h3>
        <div style={{ 
          padding: '1rem', 
          border: `2px solid ${testResults.apiConnectivity?.success ? 'green' : 'red'}`,
          borderRadius: '8px',
          background: testResults.apiConnectivity?.success ? '#d4edda' : '#f8d7da'
        }}>
          <p><strong>Status:</strong> {testResults.apiConnectivity?.success ? '✅ Success' : '❌ Failed'}</p>
          {testResults.apiConnectivity?.status && (
            <p><strong>HTTP Status:</strong> {testResults.apiConnectivity.status} {testResults.apiConnectivity.statusText}</p>
          )}
          {testResults.dataFetch?.success && (
            <p><strong>Jobs Found:</strong> {testResults.dataFetch.jobCount}</p>
          )}
          {testResults.apiConnectivity?.error && (
            <p><strong>Error:</strong> {testResults.apiConnectivity.error}</p>
          )}
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3>🔑 OAuth API Test</h3>
        <div style={{ 
          padding: '1rem', 
          border: `2px solid ${testResults.oauth?.success ? 'green' : 'red'}`,
          borderRadius: '8px',
          background: testResults.oauth?.success ? '#d4edda' : '#f8d7da'
        }}>
          <p><strong>Status:</strong> {testResults.oauth?.success ? '✅ Success' : '❌ Failed'}</p>
          {testResults.oauth?.status && (
            <p><strong>HTTP Status:</strong> {testResults.oauth.status}</p>
          )}
          {testResults.oauth?.user && (
            <div>
              <p><strong>Test User:</strong> {testResults.oauth.user.name} ({testResults.oauth.user.email})</p>
            </div>
          )}
          {testResults.oauth?.error && (
            <p><strong>Error:</strong> {testResults.oauth.error}</p>
          )}
        </div>
      </div>

      {jobs.length > 0 && (
        <div>
          <h3>📋 Sample Admin Jobs</h3>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse',
            border: '1px solid #ddd'
          }}>
            <thead>
              <tr style={{ background: '#f8f9fa' }}>
                <th style={{ padding: '0.75rem', border: '1px solid #ddd' }}>Job ID</th>
                <th style={{ padding: '0.75rem', border: '1px solid #ddd' }}>Status</th>
                <th style={{ padding: '0.75rem', border: '1px solid #ddd' }}>Document Type</th>
                <th style={{ padding: '0.75rem', border: '1px solid #ddd' }}>Score</th>
                <th style={{ padding: '0.75rem', border: '1px solid #ddd' }}>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {jobs.slice(0, 5).map((job) => (
                <tr key={job.id}>
                  <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{job.id}</td>
                  <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{job.status}</td>
                  <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{job.document_type}</td>
                  <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{job.result?.score || 'N/A'}</td>
                  <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{job.result?.risk_level || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <h3>🔗 Navigation Links</h3>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            onClick={() => window.location.href = '/admin'}
            style={{ padding: '0.5rem 1rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
          >
            Go to Real Admin Panel
          </button>
          <button 
            onClick={() => window.location.href = '/signin'}
            style={{ padding: '0.5rem 1rem', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}
          >
            Go to Sign In Page
          </button>
          <button 
            onClick={() => window.location.href = '/'}
            style={{ padding: '0.5rem 1rem', background: '#6c757d', color: 'white', border: 'none', borderRadius: '4px' }}
          >
            Go to Main KYC
          </button>
        </div>
      </div>

      {error && (
        <div style={{ 
          marginTop: '2rem',
          padding: '1rem',
          background: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          color: '#721c24'
        }}>
          <h4>Error Details:</h4>
          <p>{error}</p>
        </div>
      )}
    </div>
  )
}

export default AdminTest
