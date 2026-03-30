import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await onLogin(email, password)
      navigate('/tickets')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <section className="card">
      <h2>Login</h2>
      <form onSubmit={submit} className="grid-form">
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit">Sign In</button>
      </form>
      {error && <p className="error">{error}</p>}
      <p className="hint">
        Don't have an account? <Link to="/register">Register here</Link>.
      </p>
    </section>
  )
}

