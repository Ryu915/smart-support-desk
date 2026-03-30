## API Reference

Base URL: `http://127.0.0.1:8001`

Auth: Bearer token required for all endpoints except register/login.

### Auth

- `POST /auth/register`
  - body: `{ "email", "full_name", "password" }`
- `POST /auth/login`
  - form-data: `username`, `password`
  - response: `{ "access_token", "token_type" }`
- `GET /auth/me`

### Tickets

- `POST /tickets/` create ticket
- `GET /tickets/` list tickets
  - query: `status_filter`, `category`, `priority`, `overdue_only`, `sort_by`
- `GET /tickets/{ticket_id}` ticket detail
- `PATCH /tickets/{ticket_id}` status update
  - body: `{ "status": "IN_PROGRESS|RESOLVED|CLOSED|OPEN" }`
- `POST /tickets/{ticket_id}/reopen`
  - body: `{ "reason": "..." }`
- `GET /tickets/{ticket_id}/sla`
- `POST /tickets/{ticket_id}/override-priority` (admin)
  - body: `{ "priority": "P0|P1|P2|P3" }`
- `GET /tickets/{ticket_id}/events`
- `DELETE /tickets/{ticket_id}`

### Comments

- `POST /comments/`
  - body: `{ "ticket_id", "body", "visibility": "PUBLIC|INTERNAL" }`
- `GET /comments/ticket/{ticket_id}`

### Files

- `POST /files/upload`
  - query: `ticket_id`
  - multipart form-data: `file`

### Dashboard

- `GET /dashboard/` (admin)
  - response:
    - `total_tickets`
    - `open_tickets`
    - `overdue_tickets`
    - `avg_resolution_time_hours`
    - `category_counts`

