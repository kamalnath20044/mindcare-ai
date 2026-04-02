import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getHomework, completeHomework, skipHomework, getHomeworkStats } from '../api/client';

const CATEGORY_ICONS = {
  thought_record: '💭', behavioral_activation: '🏃', grounding: '🌍',
  journaling: '📝', breathing: '🫁', gratitude: '🙏',
  social: '💬', physical: '💪', mindfulness: '🧘',
};

const STATUS_STYLES = {
  assigned: { bg: '#e3f2fd', color: '#1565c0', label: 'Assigned' },
  in_progress: { bg: '#fff3e0', color: '#e65100', label: 'In Progress' },
  completed: { bg: '#e8f5e9', color: '#2e7d32', label: 'Completed ✓' },
  skipped: { bg: '#fce4ec', color: '#c62828', label: 'Skipped' },
};

export default function Homework() {
  const { user } = useAuth();
  const userId = user?.user_id || user?.id || 'demo-user';
  const [homework, setHomework] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState('');
  const [completingId, setCompletingId] = useState(null);
  const [note, setNote] = useState('');
  const [rating, setRating] = useState(3);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [userId, filter]);

  const loadData = async () => {
    try {
      const [hwRes, statsRes] = await Promise.all([
        getHomework(userId, filter),
        getHomeworkStats(userId),
      ]);
      setHomework(hwRes.data?.homework || []);
      setStats(statsRes.data);
    } catch { /* ignore */ }
  };

  const handleComplete = async (id) => {
    setLoading(true);
    try {
      await completeHomework(id, note, rating);
      setCompletingId(null);
      setNote('');
      setRating(3);
      loadData();
    } catch { /* ignore */ }
    setLoading(false);
  };

  const handleSkip = async (id) => {
    try {
      await skipHomework(id);
      loadData();
    } catch { /* ignore */ }
  };

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">📚 CBT Homework</span>
        <h1>Homework Assignments</h1>
        <p>CBT exercises assigned after your therapy sessions to reinforce learning</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="stats-grid" style={{ marginBottom: 20 }}>
          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Assigned</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{stats.completed}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-value">{stats.completion_rate}%</div>
            <div className="stat-label">Completion Rate</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-value">{stats.avg_rating || '—'}</div>
            <div className="stat-label">Avg Rating</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {['', 'assigned', 'completed', 'skipped'].map((f) => (
          <button
            key={f}
            className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setFilter(f)}
          >
            {f ? f.charAt(0).toUpperCase() + f.slice(1) : 'All'}
          </button>
        ))}
      </div>

      {/* Homework List */}
      {homework.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
          <p style={{ fontSize: '2rem', marginBottom: 8 }}>📚</p>
          <p>No homework assignments yet. Assignments are created after meaningful chat sessions.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {homework.map((hw) => {
            const statusStyle = STATUS_STYLES[hw.status] || STATUS_STYLES.assigned;
            return (
              <div key={hw.id} className="card" style={{ position: 'relative' }}>
                <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                  <span style={{ fontSize: '2rem' }}>{CATEGORY_ICONS[hw.category] || '📄'}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>{hw.title}</h4>
                      <span style={{
                        padding: '2px 10px', borderRadius: 20, fontSize: '0.68rem', fontWeight: 600,
                        background: statusStyle.bg, color: statusStyle.color,
                      }}>
                        {statusStyle.label}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 8 }}>
                      {hw.description}
                    </p>
                    <div style={{ display: 'flex', gap: 12, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      <span>📁 {hw.category?.replace('_', ' ')}</span>
                      <span>⚡ {hw.difficulty}</span>
                      {hw.due_at && <span>📅 Due: {new Date(hw.due_at).toLocaleDateString()}</span>}
                      {hw.rating && <span>⭐ {hw.rating}/5</span>}
                    </div>

                    {hw.completion_note && (
                      <div style={{ marginTop: 8, padding: 8, background: '#f0fff4', borderRadius: 6, fontSize: '0.8rem' }}>
                        💬 <em>{hw.completion_note}</em>
                      </div>
                    )}

                    {/* Action Buttons */}
                    {hw.status === 'assigned' && (
                      <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                        <button className="btn btn-primary btn-sm" onClick={() => setCompletingId(hw.id)}>
                          ✅ Complete
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={() => handleSkip(hw.id)}>
                          ⏭️ Skip
                        </button>
                      </div>
                    )}

                    {/* Completion Form */}
                    {completingId === hw.id && (
                      <div style={{ marginTop: 12, padding: 14, background: 'var(--bg)', borderRadius: 8 }}>
                        <div className="form-group">
                          <label>How did it go? (optional)</label>
                          <textarea
                            className="form-input"
                            rows={2}
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            placeholder="Share your experience..."
                            style={{ resize: 'vertical' }}
                          />
                        </div>
                        <div className="form-group">
                          <label>Rate this exercise (1-5)</label>
                          <div style={{ display: 'flex', gap: 6 }}>
                            {[1, 2, 3, 4, 5].map((v) => (
                              <button
                                key={v}
                                className={`btn btn-sm ${rating === v ? 'btn-primary' : 'btn-outline'}`}
                                onClick={() => setRating(v)}
                              >
                                {'⭐'.repeat(v)}
                              </button>
                            ))}
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <button className="btn btn-primary btn-sm" onClick={() => handleComplete(hw.id)} disabled={loading}>
                            {loading ? 'Saving...' : 'Submit'}
                          </button>
                          <button className="btn btn-ghost btn-sm" onClick={() => setCompletingId(null)}>Cancel</button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
