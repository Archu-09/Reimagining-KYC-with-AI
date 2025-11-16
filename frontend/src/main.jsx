import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import Admin from './admin/Admin'
import Dashboard from './pages/Dashboard'
import SignIn from './pages/SignIn'

import './styles.css'

const Root = () => {
  const path = window.location.pathname
  const isAuth = !!window.localStorage.getItem('kyc_user')

  if (path.startsWith('/admin')) return (
    <React.StrictMode>
      <Admin />
    </React.StrictMode>
  )

  if (path === '/signin') {
    return (
      <React.StrictMode>
        <SignIn />
      </React.StrictMode>
    )
  }

  // If not authenticated, redirect to sign-in
  if (!isAuth && path !== '/signin') {
    window.location.pathname = '/signin'
    return null
  }

  if (path === '/' || path === '') return (
    <React.StrictMode>
      <Dashboard />
    </React.StrictMode>
  )

  // /verify route shows the KYC App flow
  if (path.startsWith('/verify')) return (
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )

  // fallback to App
  return (
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
}

createRoot(document.getElementById('root')).render(<Root />)
