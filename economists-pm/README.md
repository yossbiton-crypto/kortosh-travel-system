# Economists PM

Project and task management for a team of economists.

- `server/` — Node.js + Express API, SQLite via `better-sqlite3`, JWT auth.
- `client/` — React + Vite, RTL Hebrew UI.

## Run locally

```bash
# API (port 4000)
cd server
cp .env.example .env      # set JWT_SECRET and the admin password
npm install
npm run seed              # creates the admin user from .env
npm run dev

# Client (port 5173, proxies /api to :4000)
cd client
npm install
npm run dev
```

## Schema

Defined in `server/src/db/schema.sql` and applied on every server start
(`CREATE TABLE IF NOT EXISTS`). The database file lives at `server/data/app.db`.

| Table    | Columns |
|----------|---------|
| users    | id, username (unique), password_hash, role (`admin`/`user`), name |
| projects | id, user_id → users, priority (1–3, 1 = high), creation_date, requester_name, subject, summary, status (`open`/`in_progress`/`on_hold`/`done`) |
| contacts | id, project_id → projects (cascade delete), name, email, phone, role |
| tasks    | id, project_id → projects (cascade delete), title, due_date (`YYYY-MM-DD`), due_time (`HH:MM`), is_completed (0/1) |

## API

All routes except login require `Authorization: Bearer <token>`.
Admins see all projects; users see only projects where `user_id` is theirs.

| Method | Path |
|--------|------|
| POST   | /api/auth/login |
| GET    | /api/auth/me |
| GET, POST | /api/users (POST is admin only) |
| GET, POST | /api/projects |
| GET, PUT, DELETE | /api/projects/:id |
| POST, DELETE | /api/projects/:id/contacts[/:contactId] |
| POST, PATCH, DELETE | /api/projects/:id/tasks[/:taskId] |
