import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const sections = [
    {
      label: 'Overview',
      items: [{ to: '/dashboard', icon: '🏠', label: 'Dashboard' }],
    },
    {
      label: 'AI Features',
      items: [
        { to: '/chat', icon: '💬', label: 'AI Therapist', badge: 'AI' },
        { to: '/emotion', icon: '😊', label: 'Emotion Detection', badge: 'Live' },
      ],
    },
    {
      label: 'Wellness',
      items: [
        { to: '/mood', icon: '📝', label: 'Mood Tracker' },
        { to: '/wellness', icon: '🧘', label: 'Wellness Tools' },
      ],
    },
    {
      label: 'Insights',
      items: [
        { to: '/analytics', icon: '📊', label: 'Analytics', badge: 'New' },
      ],
    },
  ];

  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').toUpperCase()
    : '?';

  return (
    <>
      <button className="mobile-toggle" onClick={() => setOpen(!open)}>
        {open ? '✕' : '☰'}
      </button>

      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">🧠</div>
          <div className="sidebar-brand">
            <h1>MindCare AI</h1>
            <span>Mental Health Support</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {sections.map(sec => (
            <div key={sec.label}>
              <div className="sidebar-section-label">{sec.label}</div>
              {sec.items.map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                  onClick={() => setOpen(false)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {item.label}
                  {item.badge && <span className="nav-badge">{item.badge}</span>}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user" onClick={handleLogout} title="Click to logout">
            <div className="user-avatar">{initials}</div>
            <div className="user-info">
              <div className="user-name">{user?.name || 'Guest'}</div>
              <div className="user-email">{user?.email || ''}</div>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>🚪</span>
          </div>
        </div>
      </aside>
    </>
  );
}
