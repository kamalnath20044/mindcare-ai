import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <svg width="32" height="32" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
            <circle cx="256" cy="256" r="240" fill="url(#navG)"/>
            <defs><linearGradient id="navG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style={{stopColor:'#7CAE7A'}}/><stop offset="100%" style={{stopColor:'#5C8A5A'}}/></linearGradient></defs>
            <path d="M 160 170 Q 160 140, 190 140 L 322 140 Q 352 140, 352 170 L 352 280 Q 352 310, 322 310 L 230 310 L 190 350 L 200 310 L 190 310 Q 160 310, 160 280 Z" fill="white" opacity="0.95"/>
            <path d="M 256 180 C 230 210, 220 260, 256 300 C 292 260, 282 210, 256 180 Z" fill="#7CAE7A" opacity="0.85"/>
          </svg>
          MindCare AI
        </div>
        <ul className="navbar-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#architecture">Architecture</a></li>
          <li><a href="#about">About</a></li>
          <li><Link to="/login" className="btn btn-primary">Sign In</Link></li>
        </ul>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <div className="hero-speech-bubble">
              🌿 Your calm space for mental wellness
            </div>
            <h1>
              <span className="highlight">AI-Powered</span> Mental<br />Health Support
            </h1>
            <p>
              Experience evidence-based CBT therapy powered by GPT-3.5.<br />
              Clinical assessments, mood tracking, and 24/7 compassionate support.
            </p>
            <div style={{ display: 'flex', gap: 12 }}>
              <Link to="/register" className="btn btn-primary btn-lg">Get Started Free</Link>
              <a href="#features" className="btn btn-outline btn-lg">Learn More</a>
            </div>
          </div>
          <div className="hero-visual">
            <div style={{ position: 'relative' }}>
              <div className="chat-preview">
                <div className="chat-preview-header">
                  <div className="avatar">🌿</div>
                  <div>
                    <div className="name">MindCare AI Therapist</div>
                    <div className="status">● CBT + GPT-3.5 Engine</div>
                  </div>
                </div>
                <div className="chat-preview-body">
                  <div className="preview-msg preview-msg-ai">
                    Hi there! I'm your AI companion 🌿 How are you feeling today?
                    <span className="time">10:30 AM</span>
                  </div>
                  <div className="preview-msg preview-msg-user">
                    I've been feeling really stressed about work
                    <span className="time">10:31 AM</span>
                  </div>
                  <div className="preview-msg preview-msg-ai">
                    I hear you. Let's try a grounding technique — can you name 5 things you see right now?
                    <span className="time">10:31 AM</span>
                  </div>
                </div>
                <div className="chat-preview-input">
                  <span>🌿</span>
                  <input type="text" placeholder="Type a message..." readOnly />
                  <button className="send-btn">➤</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section" id="features">
        <h2 className="section-title">Core Features</h2>
        <p className="section-subtitle">Built with production-grade AI, clinical tools, and evidence-based therapy techniques</p>
        <div className="features-grid">
          <div className="feature-card">
            <div className="icon">🧠</div>
            <h3>GPT-3.5 + CBT Therapy</h3>
            <p>AI companion using Cognitive Behavioral Therapy with thought reframing, behavioral activation, and grounding techniques</p>
          </div>
          <div className="feature-card">
            <div className="icon">📋</div>
            <h3>PHQ-9 & GAD-7 Assessments</h3>
            <p>Validated clinical screening tools for depression and anxiety with severity tracking and recommendations</p>
          </div>
          <div className="feature-card">
            <div className="icon">🔍</div>
            <h3>Composite Risk Scoring</h3>
            <p>Multi-factor risk assessment combining mood trends, sentiment, assessments, inactivity, and crisis history</p>
          </div>
          <div className="feature-card">
            <div className="icon">📚</div>
            <h3>CBT Homework Loop</h3>
            <p>Personalized therapy exercises assigned after sessions, with completion tracking and follow-up</p>
          </div>
          <div className="feature-card">
            <div className="icon">🏥</div>
            <h3>Therapist Dashboard</h3>
            <p>Admin monitoring with at-risk users, crisis event logs, real-time alerts, and weekly summaries</p>
          </div>
          <div className="feature-card">
            <div className="icon">🛡️</div>
            <h3>Crisis Detection</h3>
            <p>Real-time safety monitoring with immediate helpline resources and automated therapist email alerts</p>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section style={{ padding: '60px 48px', maxWidth: 1200, margin: '0 auto' }} id="architecture">
        <h2 className="section-title" style={{ textAlign: 'center' }}>System Architecture</h2>
        <p className="section-subtitle" style={{ textAlign: 'center', margin: '0 auto 32px' }}>5-layer production stack for scalable mental health support</p>
        <div className="grid-3">
          <div className="card" style={{ textAlign: 'center', padding: 28 }}>
            <div style={{ fontSize: '1.8rem', marginBottom: 10 }}>⚛️</div>
            <h4 style={{ fontWeight: 650, marginBottom: 4 }}>Frontend</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>React 19 + Vite + Tailwind CSS</p>
          </div>
          <div className="card" style={{ textAlign: 'center', padding: 28 }}>
            <div style={{ fontSize: '1.8rem', marginBottom: 10 }}>⚡</div>
            <h4 style={{ fontWeight: 650, marginBottom: 4 }}>Backend</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>FastAPI + JWT + APScheduler</p>
          </div>
          <div className="card" style={{ textAlign: 'center', padding: 28 }}>
            <div style={{ fontSize: '1.8rem', marginBottom: 10 }}>🧠</div>
            <h4 style={{ fontWeight: 650, marginBottom: 4 }}>AI/ML Layer</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>LangChain + GPT-3.5 + DistilBERT</p>
          </div>
        </div>
        <div className="grid-2" style={{ marginTop: 16 }}>
          <div className="card" style={{ textAlign: 'center', padding: 28 }}>
            <div style={{ fontSize: '1.8rem', marginBottom: 10 }}>🔄</div>
            <h4 style={{ fontWeight: 650, marginBottom: 4 }}>Background Jobs</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>APScheduler — follow-ups, alerts, reminders</p>
          </div>
          <div className="card" style={{ textAlign: 'center', padding: 28 }}>
            <div style={{ fontSize: '1.8rem', marginBottom: 10 }}>💾</div>
            <h4 style={{ fontWeight: 650, marginBottom: 4 }}>Data Layer</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Supabase PostgreSQL + Vector DB</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section" id="about">
        <div className="cta-card">
          <div>
            <h2>🌿 Your AI Mental Health Companion</h2>
            <p>
              Experience CBT-powered conversations, clinical assessments, and personalized mental health support — all in a peaceful, private, and secure environment.
            </p>
            <Link to="/register" className="btn btn-primary btn-lg">Start Your Journey →</Link>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '5rem', lineHeight: 1.1, marginBottom: 12 }}>🌿</div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Calm • Compassionate • Confidential</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© 2026 MindCare AI — AI-Driven Mental Health Support Platform</p>
        <p style={{ marginTop: 4 }}>Not a substitute for professional medical advice. GDPR compliant. 🛡️</p>
      </footer>
    </div>
  );
}
