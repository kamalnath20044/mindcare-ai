import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { getDashboardStats, getPersonalizedGreeting, getRecommendations } from '../api/client';
import { checkIn, getStreak, getAssessmentTrends, getHomeworkStats } from '../api/client';
import FollowUpBanner from '../components/FollowUpBanner';

const SEVERITY_COLORS = {
  none: '#4caf50', mild: '#ff9800', moderate: '#ff5722',
  moderately_severe: '#f44336', severe: '#d32f2f',
};

export default function Dashboard() {
  const { user } = useAuth();
  const userName = user?.name || 'User';
  const userId = user?.user_id || user?.id || 'demo-user';
  const [greeting, setGreeting] = useState('');
  const [stats, setStats] = useState(null);
  const [streak, setStreak] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [checkedIn, setCheckedIn] = useState(false);
  const [assessments, setAssessments] = useState(null);
  const [hwStats, setHwStats] = useState(null);

  useEffect(() => {
    getPersonalizedGreeting(userId, userName).then(r => setGreeting(r.data.greeting)).catch(() => setGreeting(`Welcome back, ${userName}! 👋`));
    getDashboardStats(userId).then(r => setStats(r.data)).catch(() => {});
    getStreak(userId).then(r => setStreak(r.data)).catch(() => {});
    getRecommendations(userId).then(r => setRecommendations(r.data)).catch(() => {});
    getAssessmentTrends(userId).then(r => setAssessments(r.data)).catch(() => {});
    getHomeworkStats(userId).then(r => setHwStats(r.data)).catch(() => {});
  }, [userId, userName]);

  const handleCheckIn = async () => {
    try {
      const res = await checkIn(userId);
      setStreak(res.data.streak);
      setCheckedIn(true);
    } catch (e) { console.error(e); }
  };

  const features = [
    { icon: '🌿', title: 'AI Companion', desc: 'Peaceful, CBT-powered conversations', tag: 'SUPPORT', path: '/chat', color: '#7CAE7A' },
    { icon: '📋', title: 'Assessments', desc: 'PHQ-9 depression & GAD-7 anxiety screening', tag: 'CLINICAL', path: '/assessment', color: '#5C8A5A' },
    { icon: '📚', title: 'Homework', desc: 'CBT exercises with tracking & follow-up', tag: 'CBT LOOP', path: '/homework', color: '#E8C169' },
    { icon: '📝', title: 'Mood Tracker', desc: 'Log and track your emotional patterns', tag: 'TRACKING', path: '/mood', color: '#D4726A' },
    { icon: '📊', title: 'Analytics', desc: 'Mood trends, insights, and progress', tag: 'INSIGHTS', path: '/analytics', color: '#6BA3BE' },
    { icon: '🧘', title: 'Wellness Tools', desc: 'Breathing, meditation, and relaxation', tag: 'SELF-CARE', path: '/wellness', color: '#E8A86D' },
  ];

  return (
    <div>
      <FollowUpBanner />

      <div className="page-header">
        <span className="page-tag">🌿 Dashboard</span>
        <h1>{greeting || `Welcome back, ${userName}! 👋`}</h1>
        <p>Your AI-powered mental health companion — CBT + GPT-3.5</p>
      </div>

      {/* Daily Check-In */}
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

      {/* Stats Grid */}
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
          <div className="stat-icon">✅</div>
          <div className="stat-value">{hwStats?.completed || 0}</div>
          <div className="stat-label">Homework Done</div>
        </div>
      </div>

      {/* Assessment Status */}
      {assessments && (assessments.phq9?.latest_score !== null || assessments.gad7?.latest_score !== null) && (
        <div className="card" style={{ marginTop: 20, marginBottom: 20 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 14 }}>📋 Latest Assessments</h3>
          <div className="grid-2">
            {assessments.phq9?.latest_score !== null && (
              <div style={{
                padding: 14, borderRadius: 10,
                borderLeft: `4px solid ${SEVERITY_COLORS[assessments.phq9.latest_severity] || '#ccc'}`,
                background: 'var(--bg)',
              }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>PHQ-9 (Depression)</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: SEVERITY_COLORS[assessments.phq9.latest_severity] || '#333' }}>
                  {assessments.phq9.latest_score}/27
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {assessments.phq9.latest_severity?.replace('_', ' ')} • Trend: {assessments.phq9.trend}
                </div>
              </div>
            )}
            {assessments.gad7?.latest_score !== null && (
              <div style={{
                padding: 14, borderRadius: 10,
                borderLeft: `4px solid ${SEVERITY_COLORS[assessments.gad7.latest_severity] || '#ccc'}`,
                background: 'var(--bg)',
              }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>GAD-7 (Anxiety)</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: SEVERITY_COLORS[assessments.gad7.latest_severity] || '#333' }}>
                  {assessments.gad7.latest_score}/21
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {assessments.gad7.latest_severity} • Trend: {assessments.gad7.trend}
                </div>
              </div>
            )}
          </div>
          <Link to="/assessment" style={{ fontSize: '0.78rem', fontWeight: 600, marginTop: 10, display: 'inline-block' }}>
            Take new assessment →
          </Link>
        </div>
      )}

      {/* Personalized Recommendations */}
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

      {/* Quick Actions */}
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
