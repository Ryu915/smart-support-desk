import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'

export function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  const loadDashboard = () => {
    api.get('/dashboard/')
       .then((res) => setStats(res.data))
       .catch((err) => setError(err?.response?.data?.detail || 'Dashboard failed (admin only)'))
    
    api.get('/auth/users')
       .then((res) => setUsers(res.data))
       .catch(console.error)
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const toggleRole = async (user) => {
    try {
      const newRole = user.role === 'admin' ? 'user' : 'admin'
      await api.patch(`/auth/users/${user.id}/role`, { role: newRole })
      loadDashboard()
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to update role')
    }
  }

  if (error) return <p className="error">{error}</p>
  if (!stats) return <p>Loading...</p>

  const chartData = Object.entries(stats.category_counts).map(([name, value]) => ({ name, value }))

  return (
    <div style={{ display: 'grid', gap: '20px' }}>
      <section className="card">
        <h2>Dashboard</h2>
        <div className="metric-grid">
          <div><h3>{stats.total_tickets}</h3><p>Total tickets</p></div>
          <div><h3>{stats.open_tickets}</h3><p>Open tickets</p></div>
          <div><h3>{stats.overdue_tickets}</h3><p>Overdue tickets</p></div>
          <div><h3>{stats.avg_resolution_time_hours ?? '-'}</h3><p>Avg resolution hrs (7 days)</p></div>
        </div>
        <div style={{ width: '100%', height: 280, marginTop: '20px' }}>
          <ResponsiveContainer>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#4f46e5" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card">
        <h2>User Management</h2>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #ccc' }}>
              <th style={{ padding: '8px 0' }}>ID</th>
              <th>Email</th>
              <th>Role</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '8px 0' }}>{u.id}</td>
                <td>{u.email}</td>
                <td><strong>{u.role.toUpperCase()}</strong></td>
                <td>
                  <button 
                    onClick={() => toggleRole(u)} 
                    style={{ padding: '4px 8px', fontSize: '12px', background: u.role === 'admin' ? '#ef4444' : '#10b981', width: 'auto' }}
                  >
                    {u.role === 'admin' ? 'Revoke Admin' : 'Make Admin'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

