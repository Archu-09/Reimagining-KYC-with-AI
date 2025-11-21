import React from 'react';

const LoadingOverlay = ({ message = "Signing in...", show = false }) => {
  if (!show) return null;

  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <h3 className="loading-message">{message}</h3>
        <p className="loading-submessage">Please wait while we redirect you...</p>
      </div>
    </div>
  );
};

export default LoadingOverlay;
