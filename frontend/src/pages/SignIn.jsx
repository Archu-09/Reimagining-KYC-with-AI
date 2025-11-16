import React, { useState } from 'react'

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    // Mock sign-in: accept any non-empty email
    if (!email) {
      setError('Please enter your email')
      return
    }

    const user = { name: email.split('@')[0] || 'User', email }
    localStorage.setItem('kyc_user', JSON.stringify(user))
    // navigate to dashboard
    window.location.pathname = '/'
  }

  const signInDemo = () => {
    const user = { name: 'DemoUser', email: 'demo@example.com' }
    localStorage.setItem('kyc_user', JSON.stringify(user))
    window.location.pathname = '/'
  }

  return (
    <div className="signin-container">
      <div className="signin-box">
        <h2>Sign In</h2>
        <p className="signin-sub">Access the KYC dashboard</p>

        <form onSubmit={handleSubmit} className="signin-form">
          <label className="upload-label">Email</label>
          <input
            className="input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />

          <label className="upload-label">Password</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
          />

          {error && <div className="upload-error">{error}</div>}

          <div style={{ marginTop: '1rem', display: 'flex', gap: '8px' }}>
            <button className="btn btn-primary" type="submit">Sign In</button>
            <button type="button" className="btn btn-secondary" onClick={signInDemo}>Demo</button>
          </div>
        </form>

        <p className="sub-text" style={{ marginTop: '1rem' }}>
          This is a demo sign-in (no backend auth). Use a real auth provider for production.
        </p>
      </div>
    </div>
  )
}
