import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

const initialForm = {
  title: '',
  description: '',
  category: 'Bug',
  impact: 'Low',
  urgency: 'Low',
}

export function TicketsPage() {
  const [tickets, setTickets] = useState([])
  const [filters, setFilters] = useState({ sort_by: 'latest', overdue_only: false, status: '', category: '', priority: '' })
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState('')

  const loadTickets = async () => {
    const { data } = await api.get('/tickets/', { params: filters })
    setTickets(data)
  }

  useEffect(() => {
    let cancelled = false
    api.get('/tickets/', { params: filters }).then(({ data }) => {
      if (!cancelled) setTickets(data)
    })
    return () => {
      cancelled = true
    }
  }, [filters])

  const createTicket = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/tickets/', form)
      setForm(initialForm)
      loadTickets()
    } catch (err) {
      let errorData = err?.response?.data?.detail
      if (Array.isArray(errorData)) {
        errorData = errorData.map(e => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join(', ')
      } else if (typeof errorData === 'object' && errorData !== null) {
        errorData = JSON.stringify(errorData)
      }
      setError(errorData || 'Failed to create ticket')
    }
  }

  return (
    <div className="layout-two-col">
      <section className="card">
        <h2>Create Ticket</h2>
        <form className="grid-form" onSubmit={createTicket}>
          <label>Title<input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required minLength={5} /></label>
          <label>Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required minLength={10} /></label>
          <label>Category<select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}><option>Bug</option><option>Feature</option><option>Billing</option><option>Other</option></select></label>
          <label>Impact<select value={form.impact} onChange={(e) => setForm({ ...form, impact: e.target.value })}><option>Low</option><option>Medium</option><option>High</option></select></label>
          <label>Urgency<select value={form.urgency} onChange={(e) => setForm({ ...form, urgency: e.target.value })}><option>Low</option><option>Medium</option><option>High</option></select></label>
          <button type="submit">Create</button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>
      <section className="card">
        <h2>Tickets</h2>
        <div className="filter-row">
          <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>
          <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
            <option value="">All Categories</option>
            <option value="Bug">Bug</option>
            <option value="Feature">Feature</option>
            <option value="Billing">Billing</option>
            <option value="Other">Other</option>
          </select>
          <select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
            <option value="">All Priorities</option>
            <option value="P0">P0</option>
            <option value="P1">P1</option>
            <option value="P2">P2</option>
            <option value="P3">P3</option>
          </select>
          <select value={filters.sort_by} onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}>
            <option value="latest">Latest</option>
            <option value="oldest">Oldest</option>
            <option value="priority">Highest priority</option>
          </select>
          <label><input type="checkbox" checked={filters.overdue_only} onChange={(e) => setFilters({ ...filters, overdue_only: e.target.checked })} />Overdue only</label>
        </div>
        <ul className="ticket-list">
          {tickets.map((t) => (
            <li key={t.id}>
              <Link to={`/tickets/${t.id}`}>#{t.id} {t.title}</Link>
              <small>{t.status} | {t.priority} | SLA {new Date(t.sla_deadline).toLocaleString()}</small>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

