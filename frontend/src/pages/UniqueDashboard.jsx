import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const UniqueDashboard = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [kycStatus, setKycStatus] = useState('not_started');
  const [aiInsights, setAiInsights] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem('kyc_user');
    if (!userData) {
      navigate('/signin');
      return;
    }
    
    const parsedUser = JSON.parse(userData);
    setUser(parsedUser);
    
    // Simulate AI insights loading
    setTimeout(() => {
      setAiInsights({
        riskProfile: 'Low Risk',
        recommendedActions: [
          'Complete document verification',
          'Enable biometric authentication',
          'Set up monitoring alerts'
        ],
        complianceScore: 85,
        fraudPrevention: 'Active'
      });
    }, 1000);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('kyc_user');
    localStorage.removeItem('kyc_token');
    navigate('/signin');
  };

  const startKycProcess = () => {
    navigate('/verify');
  };

  if (!user) {
    return <div className="loading-spinner">Loading...</div>;
  }

  return (
    <div className="unique-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="user-info">
            <div className="user-avatar">
              {user.name?.charAt(0) || 'U'}
            </div>
            <div>
              <h2>Welcome, {user.name || 'User'}</h2>
              <p className="user-email">{user.email}</p>
              <span className="auth-method">
                🔐 {user.authMethod || 'email'} authentication
              </span>
            </div>
          </div>
          <div className="header-actions">
            <button onClick={() => navigate('/admin')} className="admin-btn">
              👨‍💼 Admin
            </button>
            <button onClick={handleLogout} className="logout-btn">
              🚪 Logout
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="dashboard-nav">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`nav-tab ${activeTab === 'verification' ? 'active' : ''}`}
            onClick={() => setActiveTab('verification')}
          >
            🔍 Verification
          </button>
          <button 
            className={`nav-tab ${activeTab === 'ai-insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai-insights')}
          >
            🤖 AI Insights
          </button>
          <button 
            className={`nav-tab ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            🛡️ Security
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="stats-grid">
              <div className="stat-card primary">
                <div className="stat-icon">⚡</div>
                <div className="stat-info">
                  <h3>KYC Status</h3>
                  <p className="stat-value">{kycStatus === 'not_started' ? 'Not Started' : 'Completed'}</p>
                  <span className="stat-change">Ready to verify</span>
                </div>
              </div>
              
              <div className="stat-card success">
                <div className="stat-icon">🛡️</div>
                <div className="stat-info">
                  <h3>Security Score</h3>
                  <p className="stat-value">{aiInsights?.complianceScore || 0}/100</p>
                  <span className="stat-change">+12 this month</span>
                </div>
              </div>
              
              <div className="stat-card warning">
                <div className="stat-icon">🎯</div>
                <div className="stat-info">
                  <h3>Risk Level</h3>
                  <p className="stat-value">{aiInsights?.riskProfile || 'Calculating...'}</p>
                  <span className="stat-change">AI-powered assessment</span>
                </div>
              </div>
              
              <div className="stat-card info">
                <div className="stat-icon">🔄</div>
                <div className="stat-info">
                  <h3>Verification Time</h3>
                  <p className="stat-value">~5 min</p>
                  <span className="stat-change">80% faster than traditional</span>
                </div>
              </div>
            </div>

            <div className="action-center">
              <div className="action-card main-action">
                <div className="action-content">
                  <h3>🚀 Start Your KYC Journey</h3>
                  <p>Experience Aarav's effortless verification process with our AI-powered system.</p>
                  <div className="journey-steps">
                    <div className="step">
                      <span className="step-icon">📱</span>
                      <span>Upload Document</span>
                    </div>
                    <div className="step">
                      <span className="step-icon">🤖</span>
                      <span>AI Analysis</span>
                    </div>
                    <div className="step">
                      <span className="step-icon">✅</span>
                      <span>Instant Verification</span>
                    </div>
                  </div>
                  <button onClick={startKycProcess} className="start-kyc-btn">
                    Begin Verification Process
                  </button>
                </div>
              </div>

              <div className="features-showcase">
                <h3>🌟 Unique AI Features</h3>
                <div className="features-list">
                  <div className="feature-item">
                    <span className="feature-icon">🧠</span>
                    <div>
                      <strong>Smart Document Classification</strong>
                      <p>CNNs automatically detect document types</p>
                    </div>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">🔍</span>
                    <div>
                      <strong>Forgery Detection</strong>
                      <p>Advanced algorithms detect manipulated documents</p>
                    </div>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">📊</span>
                    <div>
                      <strong>Explainable AI</strong>
                      <p>SHAP values provide decision transparency</p>
                    </div>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">🌐</span>
                    <div>
                      <strong>Global Compliance</strong>
                      <p>PEP & AML screening via OpenSanctions</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'verification' && (
          <div className="verification-section">
            <div className="verification-flow">
              <h3>📋 Verification Process</h3>
              <div className="process-steps">
                <div className="process-step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h4>Document Upload</h4>
                    <p>Upload your Aadhaar, Passport, or Driver's License</p>
                  </div>
                </div>
                <div className="process-step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h4>AI Analysis</h4>
                    <p>Our AI performs multi-layer document verification</p>
                  </div>
                </div>
                <div className="process-step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h4>Liveness Detection</h4>
                    <p>FaceNet model ensures you're a real person</p>
                  </div>
                </div>
                <div className="process-step">
                  <div className="step-number">4</div>
                  <div className="step-content">
                    <h4>Risk Assessment</h4>
                    <p>Comprehensive scoring with explainable results</p>
                  </div>
                </div>
              </div>
              
              <button onClick={startKycProcess} className="verify-now-btn">
                🚀 Start Verification Now
              </button>
            </div>
          </div>
        )}

        {activeTab === 'ai-insights' && (
          <div className="ai-insights-section">
            <h3>🤖 AI-Powered Insights</h3>
            
            {aiInsights ? (
              <div className="insights-grid">
                <div className="insight-card">
                  <h4>🎯 Risk Assessment</h4>
                  <div className="risk-meter">
                    <div className="risk-level low">
                      {aiInsights.riskProfile}
                    </div>
                  </div>
                  <p>Based on device fingerprinting, behavioral patterns, and document analysis</p>
                </div>

                <div className="insight-card">
                  <h4>📊 Compliance Score</h4>
                  <div className="score-display">
                    <div className="score-circle">
                      <span className="score-number">{aiInsights.complianceScore}</span>
                      <span className="score-total">/100</span>
                    </div>
                  </div>
                  <p>Real-time compliance assessment with regulatory standards</p>
                </div>

                <div className="insight-card">
                  <h4>🛡️ Fraud Prevention</h4>
                  <div className="status-indicator active">
                    {aiInsights.fraudPrevention}
                  </div>
                  <p>Multi-layer security with Vision Transformers and ELA analysis</p>
                </div>

                <div className="insight-card full-width">
                  <h4>💡 AI Recommendations</h4>
                  <div className="recommendations-list">
                    {aiInsights.recommendedActions.map((action, index) => (
                      <div key={index} className="recommendation-item">
                        <span className="rec-icon">✨</span>
                        <span>{action}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="loading-insights">
                <div className="ai-loader">🧠</div>
                <p>AI is analyzing your profile...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'security' && (
          <div className="security-section">
            <h3>🛡️ Security & Privacy</h3>
            
            <div className="security-features">
              <div className="security-card">
                <div className="security-icon">🔐</div>
                <h4>AES-256 Encryption</h4>
                <p>All data encrypted with military-grade security</p>
                <div className="security-status enabled">Enabled</div>
              </div>

              <div className="security-card">
                <div className="security-icon">🔍</div>
                <h4>Audit Trails</h4>
                <p>Complete transparency with immutable logs</p>
                <div className="security-status enabled">Active</div>
              </div>

              <div className="security-card">
                <div className="security-icon">👥</div>
                <h4>RBAC Controls</h4>
                <p>Role-based access control for data protection</p>
                <div className="security-status enabled">Configured</div>
              </div>

              <div className="security-card">
                <div className="security-icon">🌐</div>
                <div className="security-header">
                  <h4>Global Compliance</h4>
                  <div className="compliance-badges">
                    <span className="badge gdpr">GDPR</span>
                    <span className="badge kyc">KYC</span>
                    <span className="badge aml">AML</span>
                  </div>
                </div>
                <p>Compliant with international regulations</p>
              </div>
            </div>

            <div className="privacy-controls">
              <h4>🔒 Privacy Controls</h4>
              <div className="controls-list">
                <div className="control-item">
                  <span>Data Retention Period</span>
                  <span className="control-value">7 years (regulatory requirement)</span>
                </div>
                <div className="control-item">
                  <span>Data Processing Purpose</span>
                  <span className="control-value">KYC Compliance Only</span>
                </div>
                <div className="control-item">
                  <span>Third-party Sharing</span>
                  <span className="control-value">Regulatory Bodies Only</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UniqueDashboard;
