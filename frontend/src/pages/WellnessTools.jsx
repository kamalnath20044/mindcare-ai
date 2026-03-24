import { useState, useEffect } from 'react';
import { getWellnessTips, getMotivation, getEmergency } from '../api/client';

export default function WellnessTools() {
  const [tab, setTab] = useState('meditation');
  const [tips, setTips] = useState({});
  const [quote, setQuote] = useState('');
  const [emergency, setEmergency] = useState([]);
  const [breathActive, setBreathActive] = useState(false);
  const [breathPhase, setBreathPhase] = useState('');

  useEffect(() => {
    getWellnessTips().then(r => setTips(r.data)).catch(() => {});
    getMotivation().then(r => setQuote(r.data.message)).catch(() => {});
    getEmergency().then(r => setEmergency(r.data.resources || [])).catch(() => {});
  }, []);

  const startBreathing = () => {
    setBreathActive(true);
    const phases = ['Breathe In...', 'Hold...', 'Breathe Out...'];
    const durations = [4000, 7000, 8000];
    let i = 0;
    const run = () => {
      setBreathPhase(phases[i % 3]);
      setTimeout(() => { i++; if (i < 12) run(); else { setBreathActive(false); setBreathPhase(''); } }, durations[i % 3]);
    };
    run();
  };

  const tabs = [
    { key: 'meditation', icon: '🧘', label: 'Meditation' },
    { key: 'breathing', icon: '🌬️', label: 'Breathing' },
    { key: 'relaxation', icon: '☕', label: 'Relaxation' },
    { key: 'motivation', icon: '✨', label: 'Motivation' },
  ];

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">🧘 Self-Care</span>
        <h1>Wellness Tools</h1>
        <p>Guided exercises and techniques for emotional balance</p>
      </div>

      <div className="tabs">
        {tabs.map(t => (
          <button key={t.key} className={`tab-btn ${tab === t.key ? 'active' : ''}`} onClick={() => setTab(t.key)}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {tab === 'meditation' && (
        <div className="grid-3">
          {(tips.meditation || []).map((m, i) => (
            <div key={i} className="wellness-card">
              <span className="page-tag">Meditation</span>
              <h3>{m.title}</h3>
              <p>{m.description}</p>
              <span className="duration">⏱️ {m.duration}</span>
            </div>
          ))}
        </div>
      )}

      {tab === 'breathing' && (
        <div>
          <div className="card" style={{ textAlign: 'center', marginBottom: 20 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 6 }}>4-7-8 Breathing Exercise</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 20 }}>Inhale 4s → Hold 7s → Exhale 8s</p>
            <div className={`breathing-circle ${breathPhase.includes('In') ? 'inhale' : breathPhase.includes('Out') ? 'exhale' : ''}`}>
              {breathPhase || 'Ready'}
            </div>
            <button className={`btn ${breathActive ? 'btn-danger' : 'btn-primary'} btn-lg`} onClick={breathActive ? () => setBreathActive(false) : startBreathing} style={{ marginTop: 20 }}>
              {breathActive ? '⏹️ Stop' : '▶️ Start Breathing'}
            </button>
          </div>
          <div className="grid-3">
            {(tips.breathing || []).map((b, i) => (
              <div key={i} className="wellness-card"><span className="page-tag">Breathing</span><h3>{b.title}</h3><p>{b.description}</p></div>
            ))}
          </div>
        </div>
      )}

      {tab === 'relaxation' && (
        <div className="grid-3">
          {(tips.relaxation || []).map((r, i) => (
            <div key={i} className="wellness-card"><span className="page-tag">Relaxation</span><h3>{r.title}</h3><p>{r.description}</p></div>
          ))}
        </div>
      )}

      {tab === 'motivation' && (
        <div className="card" style={{ textAlign: 'center', padding: '40px 28px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 14 }}>✨</div>
          <p style={{ fontSize: '1.1rem', fontStyle: 'italic', color: 'var(--text-secondary)', maxWidth: 480, margin: '0 auto', lineHeight: 1.7 }}>
            "{quote || 'Loading...'}"
          </p>
          <button className="btn btn-outline" onClick={() => getMotivation().then(r => setQuote(r.data.message)).catch(() => {})} style={{ marginTop: 20 }}>
            🔄 New Quote
          </button>
        </div>
      )}

      <hr style={{ border: 'none', height: 1, background: 'var(--border)', margin: '32px 0' }} />

      <div className="emergency-card">
        <h3>🆘 Emergency Resources</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 14, fontSize: '0.82rem' }}>If you're in crisis, reach out immediately:</p>
        <div className="grid-2">
          {emergency.map((r, i) => (
            <div key={i} className="emergency-contact">
              <span>📞</span>
              <div>
                <div className="contact-name">{r.name}</div>
                <div className="contact-number">{r.number}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
