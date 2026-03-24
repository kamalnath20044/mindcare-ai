import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { getDashboardStats, getPersonalizedGreeting, getRecommendations } from '../api/client';
import { checkIn, getStreak } from '../api/client';
import FollowUpBanner from '../components/FollowUpBanner';

export default function Dashboard() {
  const { user } = useAuth();
  const userName = user?.name || 'User';
  const userId = user?.user_id || user?.id || 'demo-user';
  const [greeting, setGreeting] = useState('');
  const [stats, setStats] = useState(null);
  const [streak, setStreak] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [checkedIn, setCheckedIn] = useState(false);

  useEffect(() => {
    getPersonalizedGreeting(userId, userName).then(r => setGreeting(r.data.greeting)).catch(() => setGreeting(`Welcome back, ${userName}! 👋`));
    getDashboardStats(userId).then(r => setStats(r.data)).catch(() => {});
    getStreak(userId).then(r => setStreak(r.data)).catch(() => {});
    getRecommendations(userId).then(r => setRecommendations(r.data)).catch(() => {});
  }, [userId, userName]);

  const handleCheckIn = async () => {
    try {
      const res = await checkIn(userId);
      setStreak(res.data.streak);
      setCheckedIn(true);
    } catch (e) { console.error(e); }
  };

  const features = [
    { icon: '🗣️', title: 'AI Therapist', desc: 'Context-aware therapeutic conversations with crisis safety', tag: 'LLM-POWERED', path: '/chat', color: '#3bb89c' },
    { icon: '😊', title: 'Emotion Detection', desc: 'Real-time facial emotion analysis via webcam', tag: 'COMPUTER VISION', path: '/emotion', color: '#f59e0b' },
    { icon: '📊', title: 'Analytics', desc: 'Mood trends, insights, and mental health analytics', tag: 'ANALYTICS', path: '/analytics', color: '#6366f1' },
    { icon: '📝', title: 'Mood Tracker', desc: 'Log and track your emotional patterns over time', tag: 'TRACKING', path: '/mood', color: '#ec4899' },
    { icon: '🧘', title: 'Wellness Tools', desc: 'Breathing exercises, meditation, and relaxation', tag: 'SELF-CARE', path: '/wellness', color: '#3b82f6' },
    { icon: '🆘', title: 'Crisis Support', desc: 'Emergency resources and safety protocols', tag: 'SAFETY', path: '/chat', color: '#ef4444' },
  ];

  return (
    <div>
      <FollowUpBanner />

      <div className="page-header">
        <span className="page-tag">🏠 Dashboard</span>
        <h1>{greeting || `Welcome back, ${userName}! 👋`}</h1>
        <p>Your AI-powered mental health companion is ready to help</p>
      </div>

      {/* ─── Daily Check-In ─── */}
      <div className="card" style={{ marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 4 }}>
            {checkedIn ? '✅ Checked in today!' : '👋 Daily Check-In'}
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {streak ? `🔥 ${streak.current_streak}-day streak • ${streak.total_checkins} total check-ins` : 'Start your wellness streak today'}
          </p>
        </div>
        {!checkedIn && (
          <button className="btn btn-primary" onClick={handleCheckIn}>Check In ✓</button>
        )}
      </div>

      {/* ─── Stats Grid ─── */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-value">{stats?.total_messages || 0}</div>
          <div className="stat-label">Messages</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{stats?.total_mood_logs || 0}</div>
          <div className="stat-label">Mood Logs</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-value">{streak?.current_streak || 0}</div>
          <div className="stat-label">Day Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">😊</div>
          <div className="stat-value">{stats?.total_emotions_detected || 0}</div>
          <div className="stat-label">Emotions</div>
        </div>
      </div>

      {/* ─── Personalized Recommendations ─── */}
      {recommendations?.strategies && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 6 }}>💡 Recommended for You</h3>
          {recommendations.context_message && <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 14 }}>{recommendations.context_message}</p>}
          <div className="grid-2">
            {recommendations.strategies.slice(0, 4).map((s, i) => (
              <div key={i} className="recommendation-card">
                <span style={{ fontSize: '1.5rem' }}>{s.icon}</span>
                <div>
                  <h4 style={{ fontSize: '0.88rem', fontWeight: 600 }}>{s.title}</h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>{s.description}</p>
                  {s.duration && <span style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: 500 }}>⏱️ {s.duration}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Quick Actions ─── */}
      <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 14 }}>⚡ Quick Actions</h2>
      <div className="grid-3">
        {features.map((f, i) => (
          <Link to={f.path} key={i} className="feature-card" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="feature-icon">{f.icon}</div>
            <span className="page-tag" style={{ background: `${f.color}15`, color: f.color }}>{f.tag}</span>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-desc">{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
