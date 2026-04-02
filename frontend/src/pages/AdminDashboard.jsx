import { useState, useEffect } from 'react';
import {
  getAdminOverview, getHighRiskUsers, getCrisisEvents, getAdminAlerts,
  acknowledgeAlert, resolveAlert, getRetentionStats, getPHQ9Distribution,
  getWeeklySummary,
} from '../api/client';

const RISK_COLORS = { critical: '#d32f2f', high: '#f44336', medium: '#ff9800', low: '#4caf50' };
const SEVERITY_COLORS = { none: '#4caf50', mild: '#ff9800', moderate: '#ff5722', moderately_severe: '#f44336', severe: '#d32f2f' };

export default function AdminDashboard() {
  const [tab, setTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [highRisk, setHighRisk] = useState([]);
  const [crises, setCrises] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [retention, setRetention] = useState(null);
  const [phq9Dist, setPhq9Dist] = useState(null);
  const [weekly, setWeekly] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, [tab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (tab === 'overview' || !overview) {
        const [ovRes, retRes, phqRes] = await Promise.all([
          getAdminOverview(), getRetentionStats(), getPHQ9Distribution(),
        ]);
        setOverview(ovRes.data);
        setRetention(retRes.data);
        setPhq9Dist(phqRes.data);
      }
      if (tab === 'risk') {
        const res = await getHighRiskUsers();
        setHighRisk(res.data?.users || []);
      }
      if (tab === 'crises') {
        const res = await getCrisisEvents();
        setCrises(res.data?.events || []);
      }
      if (tab === 'alerts') {
        const res = await getAdminAlerts();
        setAlerts(res.data?.alerts || []);
      }
      if (tab === 'weekly') {
        const res = await getWeeklySummary();
        setWeekly(res.data);
      }
    } catch { /* ignore */ }
    setLoading(false);
  };

  const handleAck = async (id) => {
    await acknowledgeAlert(id);
    loadData();
  };

  const handleResolve = async (id) => {
    await resolveAlert(id);
    loadData();
  };

  const tabs = [
    { key: 'overview', label: '📊 Overview' },
    { key: 'risk', label: '🚨 At-Risk Users' },
    { key: 'crises', label: '🆘 Crisis Events' },
    { key: 'alerts', label: '🔔 Alerts' },
    { key: 'weekly', label: '📋 Weekly Summary' },
  ];

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">🏥 Therapist Dashboard</span>
        <h1>Admin Dashboard</h1>
        <p>Monitor users, review alerts, and manage crisis events</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 20, flexWrap: 'wrap' }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            className={`btn btn-sm ${tab === t.key ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Loading...</div>}

      {/* ─── OVERVIEW TAB ─── */}
      {tab === 'overview' && overview && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-value">{overview.total_users}</div>
              <div className="stat-label">Total Users</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📱</div>
              <div className="stat-value">{overview.active_users_7d}</div>
              <div className="stat-label">Active (7d)</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">💬</div>
              <div className="stat-value">{overview.total_messages}</div>
              <div className="stat-label">Total Messages</div>
            </div>
            <div className="stat-card" style={{ borderLeft: overview.high_risk_users > 0 ? '3px solid #f44336' : 'none' }}>
              <div className="stat-icon">🚨</div>
              <div className="stat-value" style={{ color: overview.high_risk_users > 0 ? '#f44336' : 'inherit' }}>
                {overview.high_risk_users}
              </div>
              <div className="stat-label">High Risk</div>
            </div>
          </div>

          {/* Retention Stats */}
          {retention && (
            <div className="card" style={{ marginTop: 20 }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 14 }}>📈 User Retention</h3>
              <div className="grid-4">
                {[
                  { label: '1-Day', value: retention.day_1 },
                  { label: '7-Day', value: retention.day_7 },
                  { label: '14-Day', value: retention.day_14 },
                  { label: '30-Day', value: retention.day_30 },
                ].map((r) => (
                  <div key={r.label} style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: r.value > 50 ? '#4caf50' : '#ff5722' }}>
                      {r.value}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{r.label} Retention</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PHQ-9 Distribution */}
          {phq9Dist && (
            <div className="card" style={{ marginTop: 16 }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 14 }}>
                📊 PHQ-9 Severity Distribution ({phq9Dist.total_assessed} assessed)
              </h3>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                {Object.entries(phq9Dist.distribution || {}).map(([sev, count]) => (
                  <div key={sev} style={{
                    padding: '10px 18px', borderRadius: 10, textAlign: 'center',
                    background: `${SEVERITY_COLORS[sev] || '#ccc'}12`, border: `1px solid ${SEVERITY_COLORS[sev] || '#ccc'}30`,
                    minWidth: 80,
                  }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: SEVERITY_COLORS[sev] }}>{count}</div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                      {sev.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card" style={{ marginTop: 16 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 8 }}>📊 More Stats</h3>
            <div className="grid-3">
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{overview.total_crisis_events}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Crisis Events (30d)</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{overview.pending_alerts}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pending Alerts</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{overview.active_users_30d}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Active (30d)</div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ─── AT-RISK TAB ─── */}
      {tab === 'risk' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {highRisk.length === 0 && !loading && (
            <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
              ✅ No high-risk users at this time.
            </div>
          )}
          {highRisk.map((u, i) => (
            <div key={i} className="card" style={{ borderLeft: `4px solid ${RISK_COLORS[u.risk_level]}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>{u.name || 'Unknown'}</h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{u.email}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    padding: '3px 12px', borderRadius: 20, fontSize: '0.72rem', fontWeight: 700,
                    background: `${RISK_COLORS[u.risk_level]}15`, color: RISK_COLORS[u.risk_level],
                  }}>
                    {u.risk_level?.toUpperCase()} — Score: {u.risk_score}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    Last active: {u.last_active ? new Date(u.last_active).toLocaleDateString() : 'Unknown'}
                  </div>
                </div>
              </div>
              {u.factors && (
                <div style={{ marginTop: 10, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {Object.entries(u.factors).map(([key, val]) => (
                    <span key={key} style={{
                      padding: '2px 8px', borderRadius: 6, fontSize: '0.65rem',
                      background: val.score > 60 ? '#fff5f5' : '#f7fbfa',
                      color: val.score > 60 ? '#c53030' : 'var(--text-muted)',
                    }}>
                      {key.replace('_', ' ')}: {Math.round(val.score)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ─── CRISIS EVENTS TAB ─── */}
      {tab === 'crises' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {crises.length === 0 && !loading && (
            <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
              No crisis events recorded.
            </div>
          )}
          {crises.map((c, i) => (
            <div key={i} className="card" style={{ borderLeft: `4px solid ${RISK_COLORS[c.risk_level] || '#ccc'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <span style={{
                    padding: '2px 10px', borderRadius: 20, fontSize: '0.68rem', fontWeight: 600,
                    background: `${RISK_COLORS[c.risk_level] || '#ccc'}15`, color: RISK_COLORS[c.risk_level],
                  }}>
                    {c.risk_level?.toUpperCase()}
                  </span>
                  <p style={{ fontSize: '0.82rem', marginTop: 6, lineHeight: 1.5 }}>
                    {c.trigger_message?.substring(0, 200)}
                    {(c.trigger_message?.length || 0) > 200 ? '...' : ''}
                  </p>
                  {c.keywords_matched && (
                    <div style={{ display: 'flex', gap: 4, marginTop: 6, flexWrap: 'wrap' }}>
                      {(Array.isArray(c.keywords_matched) ? c.keywords_matched : []).map((kw, j) => (
                        <span key={j} style={{
                          padding: '1px 6px', borderRadius: 4, fontSize: '0.62rem',
                          background: '#fee2e2', color: '#991b1b',
                        }}>
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', marginLeft: 14 }}>
                  {c.created_at ? new Date(c.created_at).toLocaleString() : ''}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ─── ALERTS TAB ─── */}
      {tab === 'alerts' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {alerts.length === 0 && !loading && (
            <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
              ✅ No pending alerts.
            </div>
          )}
          {alerts.map((a, i) => (
            <div key={i} className="card" style={{ borderLeft: `4px solid ${RISK_COLORS[a.risk_level] || '#ccc'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
                    <span style={{
                      padding: '2px 10px', borderRadius: 20, fontSize: '0.68rem', fontWeight: 600,
                      background: `${RISK_COLORS[a.risk_level] || '#ccc'}15`, color: RISK_COLORS[a.risk_level],
                    }}>
                      {a.risk_level?.toUpperCase()}
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>{a.alert_type}</span>
                    <span style={{
                      padding: '1px 8px', borderRadius: 10, fontSize: '0.62rem',
                      background: a.status === 'pending' ? '#fff3e0' : a.status === 'acknowledged' ? '#e3f2fd' : '#e8f5e9',
                      color: a.status === 'pending' ? '#e65100' : a.status === 'acknowledged' ? '#1565c0' : '#2e7d32',
                    }}>
                      {a.status}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{a.context}</p>
                  <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    {a.created_at ? new Date(a.created_at).toLocaleString() : ''}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: 6 }}>
                  {a.status === 'pending' && (
                    <button className="btn btn-sm btn-outline" onClick={() => handleAck(a.id)}>Acknowledge</button>
                  )}
                  {a.status !== 'resolved' && (
                    <button className="btn btn-sm btn-primary" onClick={() => handleResolve(a.id)}>Resolve</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ─── WEEKLY SUMMARY TAB ─── */}
      {tab === 'weekly' && weekly && (
        <div>
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 4 }}>📋 Weekly Summary</h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 14 }}>{weekly.period}</p>
            <div className="grid-4">
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--primary)' }}>{weekly.new_users}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>New Users</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{weekly.active_users}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Active Users</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{weekly.total_messages}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Messages</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color: weekly.crisis_events > 0 ? '#f44336' : 'inherit' }}>
                  {weekly.crisis_events}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Crisis Events</div>
              </div>
            </div>
          </div>

          {weekly.high_risk_users?.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>🚨 Top At-Risk Users This Week</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {weekly.high_risk_users.map((u, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '8px 12px', background: 'var(--bg)', borderRadius: 8,
                  }}>
                    <div>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{u.name || 'Unknown'}</span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: 8 }}>{u.email}</span>
                    </div>
                    <span style={{
                      padding: '2px 10px', borderRadius: 20, fontSize: '0.68rem', fontWeight: 700,
                      background: `${RISK_COLORS[u.risk_level]}15`, color: RISK_COLORS[u.risk_level],
                    }}>
                      Score: {u.risk_score}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
