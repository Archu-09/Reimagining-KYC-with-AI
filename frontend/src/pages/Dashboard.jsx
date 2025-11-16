import React from 'react'

export default function Dashboard() {
  const startVerify = () => {
    // navigate to verification flow
    window.location.pathname = '/verify'
  }

  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem('kyc_user'))
    } catch (e) {
      return null
    }
  })()

  const signOut = () => {
    localStorage.removeItem('kyc_user')
    window.location.pathname = '/signin'
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-hero">
        <div className="hero-content">
          <h1>Welcome{user && user.name ? `, ${user.name}` : ''}</h1>
          <h2 className="hero-sub">Start a new verification</h2>
          <p className="hero-desc">Secure, fast and compliant KYC verification for users and customers.</p>
          <div className="hero-ctas">
            <button className="btn btn-primary btn-lg" onClick={startVerify}>
              Start Verify KYC
            </button>
            <a className="btn btn-secondary" href="/admin" style={{marginLeft: '8px'}}>Admin</a>
            {user ? (
              <button className="btn btn-secondary" onClick={signOut} style={{marginLeft: '8px'}}>Sign out</button>
            ) : null}
          </div>
          <div style={{ marginTop: '1rem' }} className="sub-text">Quick actions: Recent verifications and templates will appear here.</div>
        </div>
        <div className="hero-illustration">
          <img src="/assets/kyc-illustration.svg" alt="KYC illustration" style={{maxWidth: '320px'}} />
        </div>
      </header>

      <section className="how-it-works">
        <h3>How it works</h3>
        <div className="how-grid">
          <div className="how-step">
            <div className="how-number">1</div>
            <h4>Upload Document</h4>
            <p>Take a photo of the ID document or upload a file. We accept Aadhaar, Passport, PAN and Driver's License.</p>
          </div>

          <div className="how-step">
            <div className="how-number">2</div>
            <h4>Take a Live Selfie</h4>
            <p>Use your device camera to capture a live selfie for liveness checks and face matching.</p>
          </div>

          <div className="how-step">
            <div className="how-number">3</div>
            <h4>Automated Checks</h4>
            <p>OCR, forgery detection, face matching and risk scoring run automatically in the background.</p>
          </div>

          <div className="how-step">
            <div className="how-number">4</div>
            <h4>Result & Review</h4>
            <p>Get a clear verification result. Optionally route to manual review if risk is high.</p>
          </div>
        </div>
      </section>

      <footer className="dashboard-footer">
        <div className="footer-inner">
          <div>
            <strong>Reimagining KYC with AI</strong>
            <div className="sub-text">Secure identity verification • Privacy-first • Audit logs</div>
          </div>

          <div className="footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Help</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
