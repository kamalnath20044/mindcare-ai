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
        { to: '/chat', icon: '💬', label: 'AI Therapist', badge: 'GPT' },
      ],
    },
    {
      label: 'Assessments',
      items: [
        { to: '/assessment', icon: '📋', label: 'PHQ-9 / GAD-7', badge: 'New' },
        { to: '/homework', icon: '📚', label: 'Homework', badge: 'CBT' },
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
        { to: '/analytics', icon: '📊', label: 'Analytics' },
      ],
    },
    {
      label: 'Admin',
      items: [
        { to: '/admin', icon: '🏥', label: 'Admin Dashboard', badge: '🔒' },
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
          <div className="sidebar-logo">
            <svg width="22" height="22" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
              <path d="M 160 170 Q 160 140, 190 140 L 322 140 Q 352 140, 352 170 L 352 280 Q 352 310, 322 310 L 230 310 L 190 350 L 200 310 L 190 310 Q 160 310, 160 280 Z" fill="white" opacity="0.95"/>
              <path d="M 256 180 C 230 210, 220 260, 256 300 C 292 260, 282 210, 256 180 Z" fill="rgba(255,255,255,0.5)"/>
            </svg>
          </div>
          <div className="sidebar-brand">
            <h1>MindCare AI</h1>
            <span>Calm Sage • CBT + GPT</span>
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
