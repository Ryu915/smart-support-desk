import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { api, setToken } from './api'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { TicketDetailPage } from './pages/TicketDetailPage'
import { TicketsPage } from './pages/TicketsPage'
import { RegisterPage } from './pages/RegisterPage'

function ProtectedRoute({ isAuthenticated, children }) {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return children
}

export default function App() {
  const [token, setAuthToken] = useState(localStorage.getItem('token') || '')
  const isAuthenticated = useMemo(() => Boolean(token), [token])
  setToken(token)

  const handleLogin = async (email, password) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const { data } = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('token', data.access_token)
    setAuthToken(data.access_token)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setAuthToken('')
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="app-header">
          <h1>Smart Support Desk</h1>
          {isAuthenticated && (
            <nav>
              <Link to="/tickets">Tickets</Link>
              <Link to="/dashboard">Dashboard</Link>
              <button onClick={handleLogout}>Logout</button>
            </nav>
          )}
        </header>
        <main>
          <Routes>
            <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
            <Route
              path="/tickets"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <TicketsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/tickets/:id"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <TicketDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="*" element={<Navigate to={isAuthenticated ? '/tickets' : '/login'} replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
