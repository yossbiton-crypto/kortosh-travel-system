import { Router } from 'express';
import bcrypt from 'bcryptjs';
import db from '../db/index.js';
import { requireAdmin } from '../middleware/auth.js';

const router = Router();

router.get('/', (req, res) => {
  res.json(db.prepare('SELECT id, username, role, name FROM users ORDER BY name').all());
});

router.post('/', requireAdmin, (req, res) => {
  const { username, password, role = 'user', name } = req.body || {};
  if (!username || !password || !name) return res.status(400).json({ error: 'username, password, name required' });
  try {
    const info = db.prepare('INSERT INTO users (username, password_hash, role, name) VALUES (?, ?, ?, ?)')
      .run(username, bcrypt.hashSync(password, 10), role, name);
    res.status(201).json({ id: info.lastInsertRowid, username, role, name });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

export default router;
