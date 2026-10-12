import 'dotenv/config';
import bcrypt from 'bcryptjs';
import db from './index.js';

const username = process.env.ADMIN_USERNAME || 'admin';
const password = process.env.ADMIN_PASSWORD || 'admin123';
const name = process.env.ADMIN_NAME || 'מנהל מערכת';

const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
if (existing) {
  console.log(`User "${username}" already exists, skipping.`);
} else {
  db.prepare('INSERT INTO users (username, password_hash, role, name) VALUES (?, ?, ?, ?)')
    .run(username, bcrypt.hashSync(password, 10), 'admin', name);
  console.log(`Created admin user "${username}".`);
}
