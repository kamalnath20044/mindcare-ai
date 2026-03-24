import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getDashboardStats, getMoodAnalytics, getEmotionAnalytics, getChatAnalytics } from '../api/client';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler, ArcElement);

const MOOD_COLORS = { happy: '#3bb89c', good: '#6bcab5', neutral: '#b2bec3', sad: '#74b9ff', anxious: '#fbc531', angry: '#ff6b6b', stressed: '#f59e0b' };
const MOOD_VALUES = { happy: 5, good: 4, neutral: 3, sad: 2, anxious: 2, angry: 1, stressed: 1 };

export default function Analytics() {
  const { user } = useAuth();
  const userId = user?.user_id || user?.id || 'demo-user';
  const [stats, setStats] = useState(null);
  const [moodData, setMoodData] = useState(null);
  const [emotionData, setEmotionData] = useState(null);
  const [chatData, setChatData] = useState(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    getDashboardStats(userId).then(r => setStats(r.data)).catch(() => {});
    getMoodAnalytics(userId, days).then(r => setMoodData(r.data)).catch(() => {});
    getEmotionAnalytics(userId, days).then(r => setEmotionData(r.data)).catch(() => {});
    getChatAnalytics(userId).then(r => setChatData(r.data)).catch(() => {});
  }, [userId, days]);

  // ─── Mood Trend Line Chart ───
  const moodLineData = moodData?.daily_moods?.length > 0 ? {
    labels: moodData.daily_moods.map(d => d.date.slice(5)),
    datasets: [{
      label: 'Mood Score',
      data: moodData.daily_moods.map(d => MOOD_VALUES[d.mood] || 3),
      borderColor: '#3bb89c', backgroundColor: 'rgba(59,184,156,0.1)',
      fill: true, tension: 0.4, pointBackgroundColor: '#3bb89c', pointRadius: 4,
    }],
  } : null;

  // ─── Mood Distribution Doughnut ───
  const moodDoughnutData = moodData?.distribution && Object.keys(moodData.distribution).length > 0 ? {
    labels: Object.keys(moodData.distribution),
    datasets: [{
      data: Object.values(moodData.distribution).map(v => v.count),
      backgroundColor: Object.keys(moodData.distribution).map(m => MOOD_COLORS[m] || '#ddd'),
      borderWidth: 2, borderColor: '#fff',
    }],
  } : null;

  // ─── Emotion Distribution ───
  const emotionDoughnutData = emotionData?.distribution && Object.keys(emotionData.distribution).length > 0 ? {
    labels: Object.keys(emotionData.distribution),
    datasets: [{
      data: Object.values(emotionData.distribution).map(v => v.count),
      backgroundColor: ['#3bb89c', '#6bcab5', '#74b9ff', '#fbc531', '#ff6b6b', '#a29bfe', '#fd79a8'],
      borderWidth: 2, borderColor: '#fff',
    }],
  } : null;

  // ─── Chat Activity Bar Chart ───
  const chatBarData = chatData?.daily_activity?.length > 0 ? {
    labels: chatData.daily_activity.map(d => d.date.slice(5)),
    datasets: [{
      label: 'Messages',
      data: chatData.daily_activity.map(d => d.count),
      backgroundColor: 'rgba(59,184,156,0.6)', borderRadius: 6,
    }],
  } : null;

  const chartOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#999', font: { size: 10 } } },
      y: { grid: { color: '#f0f0f0' }, ticks: { color: '#999', font: { size: 10 } } },
    },
  };

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">📊 Analytics</span>
        <h1>Mental Health Analytics</h1>
        <p>Track your emotional patterns, engagement, and progress over time</p>
      </div>

      {/* ─── Stats Cards ─── */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-value">{stats?.total_messages || 0}</div>
          <div className="stat-label">Chat Messages</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{stats?.total_mood_logs || 0}</div>
          <div className="stat-label">Mood Logs</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-value">{stats?.current_streak || 0}</div>
          <div className="stat-label">Day Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">😊</div>
          <div className="stat-value">{stats?.total_emotions_detected || 0}</div>
          <div className="stat-label">Emotions Detected</div>
        </div>
      </div>

      {/* ─── Time Range Selector ─── */}
      <div className="tabs" style={{ maxWidth: 320, marginBottom: 20 }}>
        {[7, 14, 30, 90].map(d => (
          <button key={d} className={`tab-btn ${days === d ? 'active' : ''}`} onClick={() => setDays(d)}>
            {d}d
          </button>
        ))}
      </div>

      {/* ─── Insights ─── */}
      {moodData?.insights?.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          {moodData.insights.map((ins, i) => (
            <div key={i} className={`alert-banner ${ins.type === 'warning' ? 'alert-high' : ins.type === 'alert' ? 'alert-medium' : 'alert-low'}`} style={{ marginBottom: 8 }}>
              <span className="alert-icon">{ins.type === 'positive' ? '✨' : '⚠️'}</span>
              <div className="alert-content"><p>{ins.message}</p></div>
            </div>
          ))}
        </div>
      )}

      {/* ─── Charts Grid ─── */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>📈 Mood Trend</h3>
          <div style={{ height: 260 }}>
            {moodLineData ? <Line data={moodLineData} options={chartOpts} /> : <div className="empty-state">No mood data yet. Start logging!</div>}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>🎯 Mood Distribution</h3>
          <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {moodDoughnutData ? <Doughnut data={moodDoughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#636e72', font: { size: 11 } } } } }} /> : <div className="empty-state">No data</div>}
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>💬 Daily Chat Activity</h3>
          <div style={{ height: 260 }}>
            {chatBarData ? <Bar data={chatBarData} options={chartOpts} /> : <div className="empty-state">No chat activity yet</div>}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>🎭 Emotion Distribution</h3>
          <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {emotionDoughnutData ? <Doughnut data={emotionDoughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#636e72', font: { size: 11 } } } } }} /> : <div className="empty-state">No emotion data yet</div>}
          </div>
        </div>
      </div>

      {/* ─── Detailed Mood Stats ─── */}
      {moodData?.distribution && Object.keys(moodData.distribution).length > 0 && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 14 }}>📊 Mood Breakdown</h3>
          {Object.entries(moodData.distribution).map(([mood, data]) => (
            <div key={mood} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
              <span style={{ width: 80, textTransform: 'capitalize', fontWeight: 500, fontSize: '0.85rem' }}>{mood}</span>
              <div style={{ flex: 1, height: 8, borderRadius: 4, background: '#eee', overflow: 'hidden' }}>
                <div style={{ width: `${data.percentage}%`, height: '100%', background: MOOD_COLORS[mood] || '#3bb89c', borderRadius: 4 }} />
              </div>
              <span style={{ fontSize: '0.75rem', color: '#999', width: 60, textAlign: 'right' }}>{data.percentage}% ({data.count})</span>
            </div>
          ))}
          {moodData.trend && (
            <div style={{ marginTop: 14, padding: '10px 14px', borderRadius: 8, background: moodData.trend === 'improving' ? '#e8f8f3' : moodData.trend === 'declining' ? '#fff5f5' : '#f8f9fa', fontSize: '0.82rem' }}>
              {moodData.trend === 'improving' ? '📈 Trend: Improving' : moodData.trend === 'declining' ? '📉 Trend: Declining' : '➡️ Trend: Stable'}
              {' • '}Variability: {moodData.mood_variability || 'low'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
