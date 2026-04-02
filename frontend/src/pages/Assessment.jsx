import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getAssessmentQuestions, submitPHQ9, submitGAD7, getPHQ9History, getGAD7History } from '../api/client';

const SEVERITY_COLORS = {
  none: '#4caf50', mild: '#ff9800', moderate: '#ff5722',
  moderately_severe: '#f44336', severe: '#d32f2f',
};

export default function Assessment() {
  const { user } = useAuth();
  const userId = user?.user_id || user?.id || 'demo-user';
  const [activeTab, setActiveTab] = useState('phq9');
  const [questions, setQuestions] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [activeTab, userId]);

  const loadHistory = async () => {
    try {
      const res = activeTab === 'phq9'
        ? await getPHQ9History(userId)
        : await getGAD7History(userId);
      setHistory(res.data?.entries || []);
    } catch { setHistory([]); }
  };

  const startAssessment = async () => {
    try {
      const res = await getAssessmentQuestions(activeTab);
      setQuestions(res.data);
      setAnswers(new Array(res.data.questions.length).fill(-1));
      setResult(null);
      setShowForm(true);
    } catch { /* ignore */ }
  };

  const handleSubmit = async () => {
    if (answers.includes(-1)) return alert('Please answer all questions.');
    setLoading(true);
    try {
      const res = activeTab === 'phq9'
        ? await submitPHQ9(userId, answers)
        : await submitGAD7(userId, answers);
      setResult(res.data.result);
      setShowForm(false);
      loadHistory();
    } catch (e) {
      alert('Failed to submit assessment.');
    } finally { setLoading(false); }
  };

  const allAnswered = answers.length > 0 && !answers.includes(-1);

  return (
    <div>
      <div className="page-header">
        <span className="page-tag">📋 Clinical Assessments</span>
        <h1>Mental Health Screening</h1>
        <p>Validated clinical questionnaires to track your mental health over time</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        <button
          className={`btn ${activeTab === 'phq9' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setActiveTab('phq9'); setShowForm(false); setResult(null); }}
        >
          PHQ-9 (Depression)
        </button>
        <button
          className={`btn ${activeTab === 'gad7' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => { setActiveTab('gad7'); setShowForm(false); setResult(null); }}
        >
          GAD-7 (Anxiety)
        </button>
      </div>

      {/* Result Display */}
      {result && (
        <div className="card" style={{ marginBottom: 20, borderLeft: `4px solid ${result.color}` }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8 }}>
            📊 Assessment Result
          </h3>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: 12 }}>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: result.color }}>
                {result.total_score}/{result.max_score}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Total Score</div>
            </div>
            <div>
              <div style={{
                padding: '4px 14px', borderRadius: 20, fontSize: '0.82rem', fontWeight: 600,
                background: `${result.color}15`, color: result.color, display: 'inline-block',
              }}>
                {result.severity.replace('_', ' ').toUpperCase()}
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                {result.interpretation}
              </div>
            </div>
          </div>
          <div style={{ padding: 12, background: 'var(--bg)', borderRadius: 8, fontSize: '0.85rem' }}>
            💡 <strong>Recommendation:</strong> {result.recommendation}
          </div>
          {result.suicidal_ideation && (
            <div style={{
              marginTop: 12, padding: 12, background: '#fff5f5', borderRadius: 8,
              border: '1px solid #feb2b2', fontSize: '0.85rem', color: '#c53030',
            }}>
              🆘 <strong>Important:</strong> Your response to question 9 indicates you may be having thoughts of self-harm.
              Please reach out to a crisis helpline: <strong>988</strong> (US) or <strong>1860-2662-345</strong> (India, 24/7).
            </div>
          )}
        </div>
      )}

      {/* Assessment Form */}
      {showForm && questions && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: 4 }}>{questions.title}</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 20 }}>{questions.description}</p>

          {questions.questions.map((q, qi) => (
            <div key={qi} style={{ marginBottom: 20, padding: 14, background: qi % 2 === 0 ? 'var(--bg)' : 'transparent', borderRadius: 8 }}>
              <p style={{ fontSize: '0.88rem', fontWeight: 500, marginBottom: 10 }}>
                <span style={{ color: 'var(--primary)', fontWeight: 700 }}>{qi + 1}.</span> {q}
              </p>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {questions.options.map((opt) => (
                  <button
                    key={opt.value}
                    className={`btn btn-sm ${answers[qi] === opt.value ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => {
                      const newAnswers = [...answers];
                      newAnswers[qi] = opt.value;
                      setAnswers(newAnswers);
                    }}
                    style={{ fontSize: '0.78rem' }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          ))}

          <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading || !allAnswered}>
              {loading ? 'Submitting...' : 'Submit Assessment'}
            </button>
            <button className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Start Assessment Button */}
      {!showForm && (
        <button className="btn btn-primary" onClick={startAssessment} style={{ marginBottom: 20 }}>
          📝 Take {activeTab === 'phq9' ? 'PHQ-9' : 'GAD-7'} Assessment
        </button>
      )}

      {/* History */}
      <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>📈 Assessment History</h3>
      {history.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
          No assessments taken yet. Take your first assessment to start tracking your progress.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {history.map((entry, i) => (
            <div key={i} className="card" style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              borderLeft: `4px solid ${SEVERITY_COLORS[entry.severity] || '#ccc'}`,
            }}>
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 600 }}>
                  Score: {entry.total_score}/{activeTab === 'phq9' ? 27 : 21}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {new Date(entry.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </div>
              </div>
              <span style={{
                padding: '3px 12px', borderRadius: 20, fontSize: '0.72rem', fontWeight: 600,
                background: `${SEVERITY_COLORS[entry.severity] || '#ccc'}15`,
                color: SEVERITY_COLORS[entry.severity] || '#999',
              }}>
                {entry.severity?.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
