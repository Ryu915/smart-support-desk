## Assumptions

### Roles

- `user` can create and view only own tickets.
- `admin` can view all tickets, add internal comments, override priority, and access dashboard.

### Priority Rules

Base mapping:

- High + High -> `P0`
- High + Medium -> `P1`
- Medium + High -> `P1`
- Medium + Medium -> `P2`
- everything else -> `P3`

Adjustments:

- Category bump: `Bug` bumps one level (unless already `P0`).
- Reopen escalation: each reopen bumps one level up (capped at `P0`).

### SLA Rules

- `P0`: 4 hours
- `P1`: 12 hours
- `P2`: 24 hours
- `P3`: 72 hours

Behavior:

- SLA starts at ticket creation.
- On reopen, SLA is recalculated from reopen time with new priority.
- Weekends are not excluded.
- SLA is not paused on `Resolved` in this implementation.

### Status Workflow

- `OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED`
- Reopen allowed only when status is `RESOLVED` or `CLOSED`.
- Reopen sets status back to `OPEN`.

### Comments

- Public comments are visible to ticket owner and admins.
- Internal comments are admin-only for creation and visibility.

### Attachments

- Single file upload API is supported.
- File metadata is stored in DB and files are stored in local `uploads/`.
- Max upload size is 5 MB.

### Analytics

- Average resolution time uses closed tickets updated in the last 7 days.
- Resolution time approximation uses `updated_at - created_at`.

