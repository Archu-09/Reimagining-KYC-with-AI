import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import UniqueSignIn from './pages/UniqueSignIn';
import OAuthCallback from './pages/OAuthCallback';
import UniqueDashboard from './pages/UniqueDashboard';
import SmartKycFlow from './pages/SmartKycFlow';
import Dashboard from './pages/Dashboard';
import Admin from './admin/Admin';
import './styles.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('kyc_token');
  return token ? children : <Navigate to="/signin" />;
};

// Main App Component
const App = () => {
  return (
    <Router>
      <div className="app">
        <Routes>
          {/* Public Routes */}
          <Route path="/signin" element={<UniqueSignIn />} />
          <Route path="/auth/callback/:provider" element={<OAuthCallback />} />
          <Route path="/auth/success" element={<OAuthCallback />} />
          <Route path="/auth/error" element={<OAuthCallback />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <UniqueDashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/verify" 
            element={
              <ProtectedRoute>
                <SmartKycFlow />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/kyc-classic" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute>
                <Admin />
              </ProtectedRoute>
            } 
          />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="*" element={<Navigate to="/signin" />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
