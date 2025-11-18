import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const UniqueSignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [biometricSupported, setBiometricSupported] = useState(false);
  const [authMode, setAuthMode] = useState('traditional'); // traditional, biometric, smart
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('kyc_token');
    if (token) {
      navigate('/dashboard');
    }

    // Check for WebAuthn/Biometric support
    if (window.PublicKeyCredential) {
      setBiometricSupported(true);
    }
  }, [navigate]);

  const handleBiometricAuth = async () => {
    if (!biometricSupported) {
      setError('Biometric authentication not supported on this device');
      return;
    }

    setLoading(true);
    try {
      // Create a mock biometric challenge
      const credential = await navigator.credentials.create({
        publicKey: {
          challenge: new Uint8Array(32),
          rp: { name: "KYC System" },
          user: {
            id: new TextEncoder().encode("demo-user"),
            name: "demo@kyc.com",
            displayName: "Demo User"
          },
          pubKeyCredParams: [{ alg: -7, type: "public-key" }],
          timeout: 60000,
          attestation: "direct"
        }
      });

      // Simulate successful biometric auth
      const user = { 
        name: 'Biometric User', 
        email: 'biometric@kyc.com',
        role: 'user',
        authMethod: 'biometric'
      };
      localStorage.setItem('kyc_user', JSON.stringify(user));
      localStorage.setItem('kyc_token', 'biometric-token-' + Date.now());
      navigate('/dashboard');
      
    } catch (err) {
      setError('Biometric authentication failed. Please try another method.');
    } finally {
      setLoading(false);
    }
  };

  const handleSmartAuth = async () => {
    setLoading(true);
    try {
      // Simulate AI-powered risk-based authentication
      const deviceFingerprint = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        screen: `${screen.width}x${screen.height}`,
        timestamp: Date.now()
      };

      // Mock risk assessment
      const riskScore = Math.random() * 100;
      
      if (riskScore < 30) {
        // Low risk - auto authenticate
        const user = { 
          name: 'Smart Auth User', 
          email: 'smart@kyc.com',
          role: 'user',
          authMethod: 'smart',
          riskScore: riskScore.toFixed(1)
        };
        localStorage.setItem('kyc_user', JSON.stringify(user));
        localStorage.setItem('kyc_token', 'smart-token-' + Date.now());
        navigate('/dashboard');
      } else {
        setError(`Device risk score: ${riskScore.toFixed(1)}. Please use traditional authentication.`);
      }
      
    } catch (err) {
      setError('Smart authentication failed. Please try another method.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSignIn = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('kyc_token', data.access_token);
        localStorage.setItem('kyc_user', JSON.stringify({
          email: email,
          name: email.split('@')[0],
          role: data.role,
          authMethod: 'email'
        }));
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthSignIn = async (provider) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/auth/oauth/${provider}`);
      if (response.ok) {
        const data = await response.json();
        // For demo, simulate immediate OAuth success
        const user = { 
          name: `${provider} User`, 
          email: `${provider}@kyc.com`,
          role: 'user',
          authMethod: provider
        };
        localStorage.setItem('kyc_user', JSON.stringify(user));
        localStorage.setItem('kyc_token', `${provider}-token-` + Date.now());
        navigate('/dashboard');
      } else {
        setError(`${provider} login failed`);
      }
    } catch (err) {
      setError('OAuth initialization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin-container">
      <div className="signin-box modern-signin">
        <div className="signin-header">
          <div className="logo-section">
            <div className="ai-logo">🤖</div>
            <h1>AI-Powered KYC</h1>
          </div>
          <h2>Choose Your Authentication</h2>
          <p className="signin-subtitle">
            Experience next-generation identity verification
          </p>
        </div>

        {error && (
          <div className="error-alert modern-error">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Authentication Mode Selector */}
        <div className="auth-mode-selector">
          <button
            className={`mode-button ${authMode === 'smart' ? 'active' : ''}`}
            onClick={() => setAuthMode('smart')}
          >
            🧠 Smart Auth
          </button>
          <button
            className={`mode-button ${authMode === 'biometric' ? 'active' : ''}`}
            onClick={() => setAuthMode('biometric')}
            disabled={!biometricSupported}
          >
            👆 Biometric
          </button>
          <button
            className={`mode-button ${authMode === 'traditional' ? 'active' : ''}`}
            onClick={() => setAuthMode('traditional')}
          >
            🔐 Traditional
          </button>
        </div>

        {/* Smart Authentication */}
        {authMode === 'smart' && (
          <div className="smart-auth-section">
            <div className="feature-highlight">
              <h3>🎯 AI Risk Assessment</h3>
              <p>Our AI analyzes your device, location, and behavior patterns for instant secure access.</p>
            </div>
            <button
              onClick={handleSmartAuth}
              disabled={loading}
              className="auth-button smart-button"
            >
              {loading ? '🔄 Analyzing...' : '🚀 Smart Login'}
            </button>
          </div>
        )}

        {/* Biometric Authentication */}
        {authMode === 'biometric' && (
          <div className="biometric-auth-section">
            <div className="feature-highlight">
              <h3>👆 Biometric Security</h3>
              <p>Use your fingerprint, face, or device biometric for secure access.</p>
            </div>
            <button
              onClick={handleBiometricAuth}
              disabled={loading || !biometricSupported}
              className="auth-button biometric-button"
            >
              {loading ? '🔄 Scanning...' : '🔐 Biometric Login'}
            </button>
          </div>
        )}

        {/* Traditional Authentication */}
        {authMode === 'traditional' && (
          <div className="traditional-auth-section">
            {/* OAuth Sign In Options */}
            <div className="oauth-section">
              <button
                onClick={() => handleOAuthSignIn('google')}
                disabled={loading}
                className="oauth-button google-button"
              >
                <svg className="oauth-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </button>

              <button
                onClick={() => handleOAuthSignIn('github')}
                disabled={loading}
                className="oauth-button github-button"
              >
                <svg className="oauth-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                Continue with GitHub
              </button>
            </div>

            <div className="divider">
              <span>or</span>
            </div>

            {/* Email/Password Sign In */}
            <form onSubmit={handleEmailSignIn} className="signin-form">
              <div className="input-group">
                <label className="input-label">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="form-input"
                  required
                />
              </div>

              <div className="input-group">
                <label className="input-label">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="form-input"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="signin-button primary-button"
              >
                {loading ? '⏳ Signing In...' : 'Sign In'}
              </button>
            </form>
          </div>
        )}

        <div className="demo-section">
          <p className="demo-text">Experience the full KYC journey</p>
          <button
            onClick={() => {
              const user = { 
                name: 'Aarav Demo', 
                email: 'aarav@kyc.com',
                role: 'user',
                authMethod: 'demo'
              };
              localStorage.setItem('kyc_user', JSON.stringify(user));
              localStorage.setItem('kyc_token', 'demo-token-' + Date.now());
              navigate('/dashboard');
            }}
            className="demo-button modern-demo"
            disabled={loading}
          >
            🎯 Try Aarav's Journey
          </button>
        </div>

        <div className="ai-features-preview">
          <h3>🚀 What Makes Us Unique</h3>
          <div className="features-grid">
            <div className="feature-card">
              <span className="feature-icon">🤖</span>
              <span className="feature-text">AI Document Analysis</span>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🔍</span>
              <span className="feature-text">Forgery Detection</span>
            </div>
            <div className="feature-card">
              <span className="feature-icon">📊</span>
              <span className="feature-text">Explainable AI</span>
            </div>
            <div className="feature-card">
              <span className="feature-icon">⚡</span>
              <span className="feature-text">5-Minute KYC</span>
            </div>
          </div>
        </div>

        <div className="signin-footer">
          <p className="security-note">
            🔒 Enterprise-grade security with AI-powered fraud detection
          </p>
        </div>
      </div>
    </div>
  );
};

export default UniqueSignIn;
