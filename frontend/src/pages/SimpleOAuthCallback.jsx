import React, { useEffect, useState } from 'react';

const SimpleOAuthCallback = () => {
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        const error = urlParams.get('error');

        if (error) {
          setStatus('error');
          setError(error);
          return;
        }

        if (token) {
          // Store token and redirect to dashboard
          localStorage.setItem('kyc_token', token);
          
          // Get user info from token (optional)
          try {
            const response = await fetch('http://localhost:8000/api/auth/me', {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            
            if (response.ok) {
              const userData = await response.json();
              localStorage.setItem('kyc_user', JSON.stringify(userData));
            }
          } catch (err) {
            console.warn('Could not fetch user data, using default');
            localStorage.setItem('kyc_user', JSON.stringify({
              email: 'oauth@user.com',
              name: 'OAuth User',
              role: 'user'
            }));
          }
          
          setStatus('success');
          setTimeout(() => {
            window.location.pathname = '/dashboard';
          }, 1500);
        } else {
          setStatus('error');
          setError('No authentication token received');
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setStatus('error');
        setError('Authentication failed');
      }
    };

    handleCallback();
  }, []);

  const handleRetry = () => {
    window.location.pathname = '/signin';
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '60px 40px',
        textAlign: 'center',
        maxWidth: '400px',
        width: '100%',
        margin: '20px',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)'
      }}>
        {status === 'processing' && (
          <>
            <div style={{ marginBottom: '30px' }}>
              <div style={{
                width: '50px',
                height: '50px',
                border: '4px solid #e2e8f0',
                borderTop: '4px solid #667eea',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto'
              }}></div>
            </div>
            <h2>🔐 Completing Sign In...</h2>
            <p>Please wait while we verify your credentials</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{ marginBottom: '30px' }}>
              <div style={{
                width: '60px',
                height: '60px',
                background: '#48bb78',
                borderRadius: '50%',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2rem',
                margin: '0 auto'
              }}>
                ✓
              </div>
            </div>
            <h2>🎉 Welcome!</h2>
            <p>Sign in successful. Redirecting to your dashboard...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={{ marginBottom: '30px' }}>
              <div style={{ fontSize: '3rem' }}>⚠️</div>
            </div>
            <h2>❌ Sign In Failed</h2>
            <p style={{ color: '#e53e3e', marginBottom: '20px' }}>
              {error || 'An unexpected error occurred during authentication'}
            </p>
            <button 
              onClick={handleRetry}
              style={{
                padding: '12px 24px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '1rem'
              }}
            >
              Try Again
            </button>
          </>
        )}
      </div>
      
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SimpleOAuthCallback;
