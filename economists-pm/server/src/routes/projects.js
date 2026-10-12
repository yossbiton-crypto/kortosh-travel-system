import { Router } from 'express';
import db from '../db/index.js';

const router = Router();

// Admins see every project; users see only their own.
function loadProject(req, res, next) {
  const project = db.prepare('SELECT * FROM projects WHERE id = ?').get(req.params.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });
  if (req.user.role !== 'admin' && project.user_id !== req.user.id) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  req.project = project;
  next();
}

router.get('/', (req, res) => {
  const base = `SELECT p.*, u.name AS owner_name,
      (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id AND t.is_completed = 0) AS open_tasks
    FROM projects p JOIN users u ON u.id = p.user_id`;
  const order = ' ORDER BY p.priority ASC, p.creation_date DESC';
  const rows = req.user.role === 'admin'
    ? db.prepare(base + order).all()
    : db.prepare(base + ' WHERE p.user_id = ?' + order).all(req.user.id);
  res.json(rows);
});

router.post('/', (req, res) => {
  const { priority = 2, requester_name, subject, summary = null, status = 'open' } = req.body || {};
  if (!requester_name || !subject) return res.status(400).json({ error: 'requester_name and subject required' });
  // Admins may assign a project to another user.
  const userId = req.user.role === 'admin' && req.body.user_id ? req.body.user_id : req.user.id;
  try {
    const info = db.prepare(`INSERT INTO projects (user_id, priority, requester_name, subject, summary, status)
      VALUES (?, ?, ?, ?, ?, ?)`).run(userId, priority, requester_name, subject, summary, status);
    res.status(201).json(db.prepare('SELECT * FROM projects WHERE id = ?').get(info.lastInsertRowid));
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

router.get('/:id', loadProject, (req, res) => {
  const contacts = db.prepare('SELECT * FROM contacts WHERE project_id = ? ORDER BY name').all(req.project.id);
  const tasks = db.prepare(`SELECT * FROM tasks WHERE project_id = ?
    ORDER BY is_completed, due_date IS NULL, due_date, due_time`).all(req.project.id);
  res.json({ ...req.project, contacts, tasks });
});

router.put('/:id', loadProject, (req, res) => {
  const fields = ['priority', 'requester_name', 'subject', 'summary', 'status'];
  if (req.user.role === 'admin') fields.push('user_id');
  const next = { ...req.project };
  for (const f of fields) if (f in (req.body || {})) next[f] = req.body[f];
  try {
    db.prepare(`UPDATE projects SET user_id = ?, priority = ?, requester_name = ?, subject = ?, summary = ?, status = ?
      WHERE id = ?`).run(next.user_id, next.priority, next.requester_name, next.subject, next.summary, next.status, next.id);
    res.json(db.prepare('SELECT * FROM projects WHERE id = ?').get(next.id));
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

router.delete('/:id', loadProject, (req, res) => {
  db.prepare('DELETE FROM projects WHERE id = ?').run(req.project.id);
  res.status(204).end();
});

// Contacts
router.post('/:id/contacts', loadProject, (req, res) => {
  const { name, email = null, phone = null, role = null } = req.body || {};
  if (!name) return res.status(400).json({ error: 'name required' });
  const info = db.prepare('INSERT INTO contacts (project_id, name, email, phone, role) VALUES (?, ?, ?, ?, ?)')
    .run(req.project.id, name, email, phone, role);
  res.status(201).json(db.prepare('SELECT * FROM contacts WHERE id = ?').get(info.lastInsertRowid));
});

router.delete('/:id/contacts/:contactId', loadProject, (req, res) => {
  db.prepare('DELETE FROM contacts WHERE id = ? AND project_id = ?').run(req.params.contactId, req.project.id);
  res.status(204).end();
});

// Tasks
router.post('/:id/tasks', loadProject, (req, res) => {
  const { title, due_date = null, due_time = null } = req.body || {};
  if (!title) return res.status(400).json({ error: 'title required' });
  const info = db.prepare('INSERT INTO tasks (project_id, title, due_date, due_time) VALUES (?, ?, ?, ?)')
    .run(req.project.id, title, due_date, due_time);
  res.status(201).json(db.prepare('SELECT * FROM tasks WHERE id = ?').get(info.lastInsertRowid));
});

router.patch('/:id/tasks/:taskId', loadProject, (req, res) => {
  const task = db.prepare('SELECT * FROM tasks WHERE id = ? AND project_id = ?').get(req.params.taskId, req.project.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  const next = { ...task };
  for (const f of ['title', 'due_date', 'due_time']) if (f in (req.body || {})) next[f] = req.body[f];
  if ('is_completed' in (req.body || {})) next.is_completed = req.body.is_completed ? 1 : 0;
  db.prepare('UPDATE tasks SET title = ?, due_date = ?, due_time = ?, is_completed = ? WHERE id = ?')
    .run(next.title, next.due_date, next.due_time, next.is_completed, task.id);
  res.json(next);
});

router.delete('/:id/tasks/:taskId', loadProject, (req, res) => {
  db.prepare('DELETE FROM tasks WHERE id = ? AND project_id = ?').run(req.params.taskId, req.project.id);
  res.status(204).end();
});

export default router;
