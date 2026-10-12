PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT    NOT NULL UNIQUE,
  password_hash TEXT    NOT NULL,
  role          TEXT    NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
  name          TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  priority       INTEGER NOT NULL DEFAULT 2 CHECK (priority BETWEEN 1 AND 3),
  creation_date  TEXT    NOT NULL DEFAULT (datetime('now')),
  requester_name TEXT    NOT NULL,
  subject        TEXT    NOT NULL,
  summary        TEXT,
  status         TEXT    NOT NULL DEFAULT 'open'
                 CHECK (status IN ('open', 'in_progress', 'on_hold', 'done'))
);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);

CREATE TABLE IF NOT EXISTS contacts (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name       TEXT    NOT NULL,
  email      TEXT,
  phone      TEXT,
  role       TEXT
);
CREATE INDEX IF NOT EXISTS idx_contacts_project ON contacts(project_id);

CREATE TABLE IF NOT EXISTS tasks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title        TEXT    NOT NULL,
  due_date     TEXT,              -- YYYY-MM-DD
  due_time     TEXT,              -- HH:MM
  is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1))
);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
