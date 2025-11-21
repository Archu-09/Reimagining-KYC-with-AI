import React, { useState } from 'react';
import LoadingOverlay from '../components/LoadingOverlay';
import { navigateWithLoading } from '../utils/navigation';

const SimpleDashboard = () => {
  const user = JSON.parse(localStorage.getItem('kyc_user') || '{}');
  const [navigating, setNavigating] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Loading...');

  const handleLogout = async () => {
    setNavigating(true);
    setLoadingMessage('Signing out...');
    
    localStorage.removeItem('kyc_token');
    localStorage.removeItem('kyc_user');
    
    await navigateWithLoading('/signin');
  };

  const startKYC = async () => {
    setNavigating(true);
    setLoadingMessage('Starting KYC verification...');
    await navigateWithLoading('/verify');
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '30px',
        padding: '20px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: '8px'
      }}>
        <div>
          <h1>🔐 KYC Dashboard</h1>
          <p>Welcome back, {user.name || 'User'}!</p>
        </div>
        <button 
          onClick={handleLogout}
          style={{
            padding: '10px 20px',
            background: 'rgba(255,255,255,0.2)',
            color: 'white',
            border: '2px solid rgba(255,255,255,0.3)',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        
        {/* Start KYC Verification Card */}
        <div style={{
          background: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '30px',
          textAlign: 'center',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎯</div>
          <h3>Start KYC Verification</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Complete your identity verification with our AI-powered system. 
            Includes document upload, face matching, and liveness detection.
          </p>
          <button
            onClick={startKYC}
            style={{
              padding: '15px 30px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            🚀 Start Verification
          </button>
        </div>

        {/* Features Card */}
        <div style={{
          background: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '30px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3>🌟 System Features</h3>
          <ul style={{ textAlign: 'left', lineHeight: '2' }}>
            <li>🔐 OAuth Authentication (Google, GitHub)</li>
            <li>🎥 Advanced Liveness Detection</li>
            <li>📄 Document Classification & OCR</li>
            <li>🤖 AI-Powered Risk Assessment</li>
            <li>📱 Mobile-Responsive Design</li>
            <li>🛡️ Enterprise Security</li>
          </ul>
        </div>

        {/* Quick Actions Card */}
        <div style={{
          background: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '30px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3>⚡ Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button
              onClick={() => window.location.pathname = '/verify'}
              style={{
                padding: '10px 15px',
                background: '#48bb78',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              📝 New KYC Verification
            </button>
            
            <button
              onClick={() => window.location.pathname = '/admin'}
              style={{
                padding: '10px 15px',
                background: '#ed8936',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              👨‍💼 Admin Panel
            </button>
            
            <button
              onClick={() => window.open('http://localhost:8000/docs', '_blank')}
              style={{
                padding: '10px 15px',
                background: '#4299e1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              📚 API Documentation
            </button>
          </div>
        </div>

        {/* System Status Card */}
        <div style={{
          background: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '30px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3>📊 System Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Frontend:</span>
              <span style={{ color: '#48bb78' }}>✅ Online</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Backend:</span>
              <span style={{ color: '#48bb78' }}>✅ Online</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Authentication:</span>
              <span style={{ color: '#48bb78' }}>✅ Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>AI Services:</span>
              <span style={{ color: '#48bb78' }}>✅ Ready</span>
            </div>
          </div>
        </div>
      </div>

      <footer style={{ 
        textAlign: 'center', 
        marginTop: '40px', 
        padding: '20px',
        color: '#666',
        borderTop: '1px solid #e2e8f0'
      }}>
        <p>🔒 KYC System v2.0 - Secure Identity Verification Platform</p>
        <p>Built with React + FastAPI + AI/ML</p>
      </footer>
      
      <LoadingOverlay 
        show={navigating} 
        message={loadingMessage} 
      />
    </div>
  );
};

export default SimpleDashboard;
