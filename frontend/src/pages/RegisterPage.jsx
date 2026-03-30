import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../api'

export function RegisterPage() {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/auth/register', {
        email,
        full_name: fullName,
        password
      })
      navigate('/login')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <section className="card">
      <h2>Create Account</h2>
      <form onSubmit={submit} className="grid-form">
        <label>
          Full Name
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        </label>
        <button type="submit">Sign Up</button>
      </form>
      {error && <p className="error">{error}</p>}
      <p className="hint">
        Already have an account? <Link to="/login">Login here</Link>
      </p>
    </section>
  )
}
