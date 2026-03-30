## Smart Support Desk

End-to-end support ticketing system with rule-based priority and SLA logic.

### Tech Stack

- Frontend: React (Vite), Recharts
- Backend: FastAPI
- Database: MySQL

### Why This Stack

- FastAPI gives fast API development, validation, and auto Swagger docs.
- React provides a quick UI with reusable pages and state handling.
- MySQL fits relational ticket + history + comment data well.

### Project Structure

- `backend/app` - API, models, services, security
- `backend/tests` - backend tests
- `frontend/src` - React UI
- `ASSUMPTIONS.md` - business rule assumptions
- `API.md` - endpoint documentation
- `DB_SCHEMA.md` - schema reference

### Backend Setup

1. Create and activate virtual environment:
   - `python3 -m venv venv`
   - `source "venv/bin/activate"`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Configure DB env variables:
   - `export DB_USER=root`
   - `export DB_PASSWORD=your_password`
   - `export DB_HOST=127.0.0.1`
   - `export DB_PORT=3306`
   - `export DB_NAME=smart_support_desk`
4. Create DB:
   - `mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS smart_support_desk;"`
5. Create tables:
   - `cd backend`
   - `python -m app.create_db`
6. Start API:
   - `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001`

Swagger: `http://127.0.0.1:8001/docs`

### Frontend Setup

1. `cd frontend`
2. `npm install`
3. `npm run dev`


### Run Tests

- `cd backend`
- `python -m pytest -q`

### Default admin credentials

email id : admin@example.com
password : password

### Implemented Features

- Authentication: register, login, me
- Ticketing: create, list, filter, sort, detail, status transitions, reopen, delete
- Priority engine: impact + urgency + category bump + reopen escalation
- SLA engine: deadline calculation, remaining/overdue status
- Comments: public and internal (internal is admin only)
- Attachments: upload endpoint with file size limit
- Dashboard: total/open/overdue/avg resolution/category chart data
- Event history: ticket events recorded and queryable per ticket

