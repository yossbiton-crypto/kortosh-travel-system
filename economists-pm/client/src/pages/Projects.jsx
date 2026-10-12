import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client.js';
import { useAuth } from '../auth.jsx';
import { PriorityBadge, StatusBadge } from '../components/Badge.jsx';
import { PRIORITIES } from '../constants.js';

const empty = { subject: '', requester_name: '', priority: 2, summary: '' };

export default function Projects() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState(empty);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const load = () => api('/projects').then(setProjects).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  async function onCreate(e) {
    e.preventDefault();
    try {
      await api('/projects', { method: 'POST', body: { ...form, priority: Number(form.priority) } });
      setForm(empty);
      setShowForm(false);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <>
      <div className="page-head">
        <h1>פרויקטים</h1>
        <button className="btn" onClick={() => setShowForm(!showForm)}>{showForm ? 'ביטול' : 'פרויקט חדש'}</button>
      </div>

      {error && <p className="error">{error}</p>}

      {showForm && (
        <form className="card form-grid" onSubmit={onCreate}>
          <label>נושא<input required value={form.subject} onChange={set('subject')} /></label>
          <label>שם המבקש<input required value={form.requester_name} onChange={set('requester_name')} /></label>
          <label>עדיפות
            <select value={form.priority} onChange={set('priority')}>
              {Object.entries(PRIORITIES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </label>
          <label className="full">תקציר<textarea rows={3} value={form.summary} onChange={set('summary')} /></label>
          <div className="full"><button className="btn">שמירה</button></div>
        </form>
      )}

      <table className="table">
        <thead>
          <tr>
            <th>נושא</th><th>מבקש</th><th>עדיפות</th><th>סטטוס</th><th>משימות פתוחות</th>
            {user.role === 'admin' && <th>אחראי</th>}
            <th>נוצר</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.id}>
              <td><Link to={`/projects/${p.id}`}>{p.subject}</Link></td>
              <td>{p.requester_name}</td>
              <td><PriorityBadge value={p.priority} /></td>
              <td><StatusBadge value={p.status} /></td>
              <td>{p.open_tasks}</td>
              {user.role === 'admin' && <td>{p.owner_name}</td>}
              <td className="muted">{p.creation_date.slice(0, 10)}</td>
            </tr>
          ))}
          {projects.length === 0 && (
            <tr><td colSpan={7} className="muted center-text">אין פרויקטים עדיין</td></tr>
          )}
        </tbody>
      </table>
    </>
  );
}
