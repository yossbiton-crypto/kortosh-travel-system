import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client.js';
import { PriorityBadge } from '../components/Badge.jsx';
import { STATUSES } from '../constants.js';

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [error, setError] = useState('');
  const [task, setTask] = useState({ title: '', due_date: '', due_time: '' });
  const [contact, setContact] = useState({ name: '', email: '', phone: '', role: '' });

  const load = () => api(`/projects/${id}`).then(setProject).catch((e) => setError(e.message));
  useEffect(() => { load(); }, [id]);

  const run = (fn) => async (e) => {
    e?.preventDefault?.();
    try { await fn(); load(); } catch (err) { setError(err.message); }
  };

  if (error && !project) return <p className="error">{error}</p>;
  if (!project) return <p className="muted">טוען…</p>;

  const base = `/projects/${id}`;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>{project.subject}</h1>
          <p className="muted">מבקש: {project.requester_name} · נוצר {project.creation_date.slice(0, 10)}</p>
        </div>
        <div className="row">
          <PriorityBadge value={project.priority} />
          <select value={project.status}
            onChange={(e) => run(() => api(base, { method: 'PUT', body: { status: e.target.value } }))()}>
            {Object.entries(STATUSES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <button className="btn-link danger"
            onClick={run(async () => {
              if (!confirm('למחוק את הפרויקט?')) return;
              await api(base, { method: 'DELETE' });
              navigate('/');
            })}>מחיקה</button>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {project.summary && <p className="card">{project.summary}</p>}

      <div className="columns">
        <section className="card">
          <h2>משימות</h2>
          <ul className="list">
            {project.tasks.map((t) => (
              <li key={t.id} className={t.is_completed ? 'done' : ''}>
                <label className="row">
                  <input type="checkbox" checked={!!t.is_completed}
                    onChange={run(() => api(`${base}/tasks/${t.id}`, { method: 'PATCH', body: { is_completed: !t.is_completed } }))} />
                  <span>{t.title}</span>
                </label>
                <span className="muted">{[t.due_date, t.due_time].filter(Boolean).join(' ')}</span>
                <button className="btn-link danger" onClick={run(() => api(`${base}/tasks/${t.id}`, { method: 'DELETE' }))}>×</button>
              </li>
            ))}
          </ul>
          <form className="row inline-form" onSubmit={run(async () => {
            await api(`${base}/tasks`, { method: 'POST', body: { ...task, due_date: task.due_date || null, due_time: task.due_time || null } });
            setTask({ title: '', due_date: '', due_time: '' });
          })}>
            <input required placeholder="משימה חדשה" value={task.title} onChange={(e) => setTask({ ...task, title: e.target.value })} />
            <input type="date" value={task.due_date} onChange={(e) => setTask({ ...task, due_date: e.target.value })} />
            <input type="time" value={task.due_time} onChange={(e) => setTask({ ...task, due_time: e.target.value })} />
            <button className="btn">הוספה</button>
          </form>
        </section>

        <section className="card">
          <h2>אנשי קשר</h2>
          <ul className="list">
            {project.contacts.map((c) => (
              <li key={c.id}>
                <div>
                  <strong>{c.name}</strong>{c.role && <span className="muted"> · {c.role}</span>}
                  <div className="muted small">{[c.email, c.phone].filter(Boolean).join(' · ')}</div>
                </div>
                <button className="btn-link danger" onClick={run(() => api(`${base}/contacts/${c.id}`, { method: 'DELETE' }))}>×</button>
              </li>
            ))}
          </ul>
          <form className="form-grid" onSubmit={run(async () => {
            await api(`${base}/contacts`, { method: 'POST', body: contact });
            setContact({ name: '', email: '', phone: '', role: '' });
          })}>
            <input required placeholder="שם" value={contact.name} onChange={(e) => setContact({ ...contact, name: e.target.value })} />
            <input placeholder="תפקיד" value={contact.role} onChange={(e) => setContact({ ...contact, role: e.target.value })} />
            <input type="email" placeholder="אימייל" value={contact.email} onChange={(e) => setContact({ ...contact, email: e.target.value })} />
            <input placeholder="טלפון" value={contact.phone} onChange={(e) => setContact({ ...contact, phone: e.target.value })} />
            <div className="full"><button className="btn">הוספת איש קשר</button></div>
          </form>
        </section>
      </div>
    </>
  );
}
