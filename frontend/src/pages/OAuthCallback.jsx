import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const OAuthCallback = () => {
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check for success token
        const token = searchParams.get('token');
        const error = searchParams.get('error');

        if (error) {
          setStatus('error');
          setError(error);
          return;
        }

        if (token) {
          // Store token and redirect to dashboard
          localStorage.setItem('kyc_token', token);
          
          // Get user info from token
          try {
            const response = await fetch('http://localhost:8000/api/auth/me', {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            
            if (response.ok) {
              const userData = await response.json();
              localStorage.setItem('kyc_user', JSON.stringify(userData));
              
              setStatus('success');
              setTimeout(() => {
                navigate('/dashboard');
              }, 1500);
            } else {
              throw new Error('Failed to get user data');
            }
          } catch (err) {
            console.error('Error getting user data:', err);
            // Still proceed with basic user data
            localStorage.setItem('kyc_user', JSON.stringify({
              email: 'user@oauth.com',
              name: 'OAuth User'
            }));
            navigate('/dashboard');
          }
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
  }, [searchParams, navigate]);

  const handleRetry = () => {
    navigate('/signin');
  };

  return (
    <div className="oauth-callback-container">
      <div className="oauth-callback-box">
        {status === 'processing' && (
          <>
            <div className="loading-animation">
              <div className="spinner"></div>
            </div>
            <h2>🔐 Completing Sign In...</h2>
            <p>Please wait while we verify your credentials</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="success-animation">
              <div className="checkmark">✓</div>
            </div>
            <h2>🎉 Welcome!</h2>
            <p>Sign in successful. Redirecting to your dashboard...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="error-animation">
              <div className="error-icon">⚠️</div>
            </div>
            <h2>❌ Sign In Failed</h2>
            <p className="error-message">
              {error || 'An unexpected error occurred during authentication'}
            </p>
            <button onClick={handleRetry} className="retry-button">
              Try Again
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;
