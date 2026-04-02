import { useState, useEffect } from 'react';
import { logMood, getMoods } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Line, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler, ArcElement);

const MOODS = [
  { key: 'happy', emoji: '😊', label: 'Happy', value: 5 },
  { key: 'good', emoji: '🙂', label: 'Good', value: 4 },
  { key: 'neutral', emoji: '😐', label: 'Neutral', value: 3 },
  { key: 'sad', emoji: '😢', label: 'Sad', value: 2 },
  { key: 'anxious', emoji: '😰', label: 'Anxious', value: 2 },
  { key: 'angry', emoji: '😠', label: 'Angry', value: 1 },
  { key: 'stressed', emoji: '😤', label: 'Stressed', value: 1 },
];

const VALUES = { happy: 5, good: 4, neutral: 3, sad: 2, anxious: 2, angry: 1, stressed: 1 };

export default function MoodTracker() {
  const { user } = useAuth();
  const userId = user?.user_id || user?.id || 'demo-user';
  const [selectedMood, setSelectedMood] = useState('');
  const [note, setNote] = useState('');
  const [entries, setEntries] = useState([]);
  const [range, setRange] = useState('week');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getMoods(userId, range).then(r => setEntries(r.data.entries || [])).catch(() => {});
  }, [range, userId]);

  const handleSave = async () => {
    if (!selectedMood) return;
    setSaving(true);
    try {
      await logMood(selectedMood, note || null, userId);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
      setSelectedMood('');
      setNote('');
      const r = await getMoods(userId, range);
      setEntries(r.data.entries || []);
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  const recent = [...entries].reverse().slice(-14);
  const lineData = {
    labels: recent.map(e => new Date(e.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })),
    datasets: [{ label: 'Mood', data: recent.map(e => VALUES[e.mood] || 3), borderColor: '#7CAE7A', backgroundColor: 'rgba(124, 174, 122, 0.1)', fill: true, tension: 0.4, pointBackgroundColor: '#7CAE7A', pointRadius: 5 }],
  };
  const chartOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: '#f0f0f0' }, ticks: { color: '#999', font: { size: 11 } } },
      y: { min: 0, max: 6, grid: { color: '#f0f0f0' }, ticks: { color: '#999', font: { size: 11 }, callback: v => ['', 'Bad', 'Low', 'Okay', 'Good', 'Great'][v] || '' } },
    },
  };

  const counts = {};
  entries.forEach(e => { counts[e.mood] = (counts[e.mood] || 0) + 1; });
  const doughnutData = {
    labels: Object.keys(counts),
    datasets: [{ data: Object.values(counts), backgroundColor: ['#7CAE7A', '#5C8A5A', '#9BAB9B', '#D4726A', '#E8C169', '#c0524a', '#E8A86D'], borderWidth: 0 }],
  };

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">🌿 Analytics</span>
        <h1>Mood Tracker</h1>
        <p>Log your mood and discover emotional patterns over time</p>
      </div>

      {saved && <div className="alert-banner alert-low"><span className="alert-icon">✅</span><div className="alert-content"><p>Mood saved!</p></div></div>}

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16, textAlign: 'center' }}>How are you feeling right now?</h3>
        <div className="mood-selector">
          {MOODS.map(m => (
            <button key={m.key} className={`mood-btn ${selectedMood === m.key ? 'selected' : ''}`} onClick={() => setSelectedMood(m.key)}>
              <span className="mood-emoji">{m.emoji}</span>
              <span className="mood-label">{m.label}</span>
            </button>
          ))}
        </div>
        <textarea placeholder="Add a note (optional)..." value={note} onChange={e => setNote(e.target.value)} rows={2} style={{ marginTop: 16 }} />
        <button className="btn btn-primary btn-lg" style={{ marginTop: 12 }} onClick={handleSave} disabled={!selectedMood || saving}>
          {saving ? '⏳ Saving...' : '💾 Save Mood'}
        </button>
      </div>

      <div className="tabs" style={{ maxWidth: 280 }}>
        {['week', 'month', 'all'].map(r => (
          <button key={r} className={`tab-btn ${range === r ? 'active' : ''}`} onClick={() => setRange(r)}>
            {r.charAt(0).toUpperCase() + r.slice(1)}
          </button>
        ))}
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>📈 Mood Trends</h3>
          <div style={{ height: 260 }}>
            {recent.length > 0 ? <Line data={lineData} options={chartOpts} /> : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>No data yet</div>
            )}
          </div>
        </div>
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>🎯 Distribution</h3>
          <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {Object.keys(counts).length > 0 ? <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#636e72' } } } }} /> : <p style={{ color: 'var(--text-muted)' }}>No data</p>}
          </div>
        </div>
      </div>

      {entries.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>Recent Entries</h3>
          {entries.slice(0, 7).map((e, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: i < Math.min(entries.length, 7) - 1 ? '1px solid var(--border-light)' : 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: '1.3rem' }}>{MOODS.find(m => m.key === e.mood)?.emoji || '😐'}</span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', textTransform: 'capitalize' }}>{e.mood}</div>
                  {e.note && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{e.note}</div>}
                </div>
              </div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {new Date(e.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
