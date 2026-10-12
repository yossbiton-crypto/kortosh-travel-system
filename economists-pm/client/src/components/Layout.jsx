import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../auth.jsx';

export default function Layout() {
  const { user, logout } = useAuth();
  return (
    <>
      <header className="topbar">
        <Link to="/" className="brand">ניהול פרויקטים</Link>
        <div className="topbar-user">
          <span>{user.name}{user.role === 'admin' && ' · מנהל'}</span>
          <button className="btn-link" onClick={logout}>יציאה</button>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}
