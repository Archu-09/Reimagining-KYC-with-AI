import React from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

// Simple routing function
const SimpleRouter = () => {
  const path = window.location.pathname;
  console.log('Current path:', path);

  // Landing page component
  const LandingPage = () => (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '40px',
        maxWidth: '800px',
        width: '90%',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
        textAlign: 'center'
      }}>
        <h1 style={{ fontSize: '3rem', margin: '0 0 10px 0', color: '#2d3748' }}>
          🔐 KYC System
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '30px' }}>
          Complete AI-Powered Identity Verification Platform
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          marginBottom: '30px'
        }}>
          <div style={{
            background: '#f8f9ff',
            padding: '20px',
            borderRadius: '8px',
            border: '2px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🔐</div>
            <h3>OAuth Authentication</h3>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Google & GitHub integration with secure JWT tokens
            </p>
          </div>
          
          <div style={{
            background: '#f0fff4',
            padding: '20px',
            borderRadius: '8px',
            border: '2px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🎥</div>
            <h3>Liveness Detection</h3>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Advanced 5-modal anti-spoofing verification
            </p>
          </div>
          
          <div style={{
            background: '#fff5f0',
            padding: '20px',
            borderRadius: '8px',
            border: '2px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🤖</div>
            <h3>AI/ML Pipeline</h3>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Document classification, OCR & risk assessment
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', justifyContent: 'center' }}>
          <button 
            onClick={() => window.location.pathname = '/signin'} 
            style={{ 
              padding: '15px 30px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}
          >
            🚀 Get Started
          </button>
          
          <button 
            onClick={() => window.location.pathname = '/verify'} 
            style={{ 
              padding: '15px 30px',
              background: '#48bb78',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}
          >
            📝 Try KYC Demo
          </button>
          
          <button 
            onClick={() => window.open('http://localhost:8000/docs', '_blank')} 
            style={{ 
              padding: '15px 30px',
              background: '#4299e1',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}
          >
            📚 API Docs
          </button>
        </div>

        <div style={{
          marginTop: '30px',
          padding: '20px',
          background: '#f7fafc',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <h4 style={{ margin: '0 0 10px 0' }}>🎯 System Status</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.9rem' }}>
            <div>Frontend: <span style={{ color: '#48bb78' }}>✅ Online</span></div>
            <div>Backend: <span style={{ color: '#48bb78' }}>✅ Online</span></div>
            <div>Authentication: <span style={{ color: '#48bb78' }}>✅ Ready</span></div>
            <div>AI Services: <span style={{ color: '#48bb78' }}>✅ Ready</span></div>
          </div>
        </div>
      </div>
    </div>
  );

  // Import components dynamically to avoid initial load issues
  try {
    // Route: Admin Panel
    if (path.startsWith('/admin') && path !== '/admin-test') {
      const SimpleAdmin = React.lazy(() => import('./admin/SimpleAdmin'));
      return (
        <React.Suspense fallback={<div style={{padding: '20px', textAlign: 'center'}}>🔄 Loading admin...</div>}>
          <SimpleAdmin />
        </React.Suspense>
      );
    }

    // Route: Sign In
    if (path === '/signin' || path === '/login') {
      const SimpleSignIn = React.lazy(() => import('./pages/SimpleSignIn'));
      return (
        <React.Suspense fallback={<div>Loading...</div>}>
          <SimpleSignIn />
        </React.Suspense>
      );
    }

    // Route: OAuth Callback
    if (path.startsWith('/auth/callback')) {
      const SimpleOAuthCallback = React.lazy(() => import('./pages/SimpleOAuthCallback'));
      return (
        <React.Suspense fallback={<div>Loading...</div>}>
          <SimpleOAuthCallback />
        </React.Suspense>
      );
    }

    // Route: Dashboard
    if (path === '/dashboard') {
      const SimpleDashboard = React.lazy(() => import('./pages/SimpleDashboard'));
      return (
        <React.Suspense fallback={<div>Loading dashboard...</div>}>
          <SimpleDashboard />
        </React.Suspense>
      );
    }

    // Route: KYC Verification
    if (path.startsWith('/verify')) {
      const App = React.lazy(() => import('./App'));
      return (
        <React.Suspense fallback={<div>Loading...</div>}>
          <App />
        </React.Suspense>
      );
    }

    // Route: Admin Test (for debugging)
    if (path === '/admin-test') {
      const AdminTest = React.lazy(() => import('./pages/AdminTest'));
      return (
        <React.Suspense fallback={<div>Loading admin test...</div>}>
          <AdminTest />
        </React.Suspense>
      );
    }

    // Default route
    return <LandingPage />;
    
  } catch (error) {
    console.error('Routing error:', error);
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h2>Error loading component</h2>
        <p>{error.message}</p>
        <button onClick={() => window.location.reload()}>Reload</button>
      </div>
    );
  }
};

const rootElement = document.getElementById('root');
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <SimpleRouter />
    </React.StrictMode>
  );
} else {
  console.error('Root element not found!');
}
