import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api'

export function TicketDetailPage() {
  const { id } = useParams()
  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [events, setEvents] = useState([])
  const [comment, setComment] = useState('')
  const [visibility, setVisibility] = useState('PUBLIC')
  const [reopenReason, setReopenReason] = useState('')
  const [error, setError] = useState('')
  const [userRole, setUserRole] = useState('user')
  const [newPriority, setNewPriority] = useState('P0')

  const load = async () => {
    const [t, c, e] = await Promise.all([
      api.get(`/tickets/${id}`),
      api.get(`/comments/ticket/${id}`),
      api.get(`/tickets/${id}/events`)
    ])
    setTicket(t.data)
    setComments(c.data)
    setEvents(e.data)
  }

  useEffect(() => {
    let cancelled = false
    Promise.all([
      api.get(`/tickets/${id}`),
      api.get(`/comments/ticket/${id}`),
      api.get(`/tickets/${id}/events`),
      api.get('/auth/me').catch(() => ({ data: { role: 'user' } }))
    ]).then(([t, c, e, u]) => {
      if (cancelled) return
      setTicket(t.data)
      setComments(c.data)
      setEvents(e.data)
      setUserRole(u.data.role)
    })
    return () => {
      cancelled = true
    }
  }, [id])

  const updateStatus = async (status) => {
    await api.patch(`/tickets/${id}`, { status })
    load()
  }

  const handlePriorityOverride = async () => {
    try {
      await api.post(`/tickets/${id}/override-priority`, { priority: newPriority })
      load()
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to override priority')
    }
  }

  const submitComment = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/comments/', { ticket_id: Number(id), body: comment, visibility })
      setComment('')
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Comment failed')
    }
  }

  const reopen = async () => {
    if (!reopenReason) return
    await api.post(`/tickets/${id}/reopen`, { reason: reopenReason })
    setReopenReason('')
    load()
  }

  if (!ticket) return <p>Loading...</p>

  return (
    <div className="layout-two-col">
      <section className="card">
        <h2>Ticket #{ticket.id}</h2>
        <p><strong>{ticket.title}</strong></p>
        <p>{ticket.description}</p>
        <p>{ticket.status} | {ticket.priority}</p>
        <div className="filter-row">
          <button onClick={() => updateStatus('IN_PROGRESS')}>In Progress</button>
          <button onClick={() => updateStatus('RESOLVED')}>Resolve</button>
          <button onClick={() => updateStatus('CLOSED')}>Close</button>
        </div>
        <div className="filter-row">
          <input placeholder="Reopen reason" value={reopenReason} onChange={(e) => setReopenReason(e.target.value)} />
          <button onClick={reopen}>Reopen</button>
        </div>
        {userRole === 'admin' && (
          <div className="filter-row" style={{ marginTop: '10px' }}>
            <select value={newPriority} onChange={(e) => setNewPriority(e.target.value)}>
              <option value="P0">P0 (Critical)</option>
              <option value="P1">P1 (High)</option>
              <option value="P2">P2 (Medium)</option>
              <option value="P3">P3 (Low)</option>
            </select>
            <button style={{ backgroundColor: '#ef4444' }} onClick={handlePriorityOverride}>Admin Override Priority</button>
          </div>
        )}
      </section>
      <section className="card">
        <h3>Comments</h3>
        <form onSubmit={submitComment} className="grid-form">
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} required />
          <select value={visibility} onChange={(e) => setVisibility(e.target.value)}>
            <option value="PUBLIC">Public</option>
            <option value="INTERNAL">Internal</option>
          </select>
          <button type="submit">Add Comment</button>
        </form>
        {error && <p className="error">{error}</p>}
        <ul className="ticket-list">
          {comments.map((c) => (
            <li key={c.id}><small>{c.visibility}</small> {c.body}</li>
          ))}
        </ul>
        <h3>History</h3>
        <ul className="ticket-list">
          {events.map((e) => (
            <li key={e.id}><small>{e.event_type}</small> {e.payload || '-'}</li>
          ))}
        </ul>
      </section>
    </div>
  )
}

