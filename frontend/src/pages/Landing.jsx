import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <span style={{ fontSize: '1.6rem' }}>🧠</span>
          AI Mental Health
        </div>
        <ul className="navbar-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#about">About</a></li>
          <li><Link to="/login" className="btn btn-primary">Login</Link></li>
        </ul>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <div className="hero-speech-bubble">
              Hi! I'm here to support you 😊
            </div>
            <h1>
              <span className="highlight">AI</span> Mental Health<br />Assistant
            </h1>
            <p>Your safe space to talk and feel better 💚<br />Smart, empathetic conversations powered by machine learning.</p>
            <div style={{ display: 'flex', gap: 12 }}>
              <Link to="/register" className="btn btn-primary btn-lg">Get Started</Link>
              <a href="#features" className="btn btn-outline btn-lg">Learn More</a>
            </div>
          </div>
          <div className="hero-visual">
            <div style={{ position: 'relative' }}>
              {/* Chat Preview */}
              <div className="chat-preview">
                <div className="chat-preview-header">
                  <div className="avatar">🧠</div>
                  <div>
                    <div className="name">AI Mental Health Assistant</div>
                    <div className="status">● online</div>
                  </div>
                </div>
                <div className="chat-preview-body">
                  <div className="preview-msg preview-msg-ai">
                    Hi there! 👋 How are you feeling today?
                    <span className="time">10:30 AM</span>
                  </div>
                  <div className="preview-msg preview-msg-user">
                    I'm feeling a bit stressed
                    <span className="time">10:31 AM</span>
                  </div>
                  <div className="preview-msg preview-msg-ai">
                    I'm sorry to hear that. Want to talk more?
                    <span className="time">10:31 AM</span>
                  </div>
                </div>
                <div className="chat-preview-input">
                  <span>😊</span>
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
        <h2 className="section-title">✨ Key Features</h2>
        <p className="section-subtitle">Powered by cutting-edge AI and machine learning technology</p>
        <div className="features-grid">
          <div className="feature-card">
            <div className="icon">😊</div>
            <h3>Emotion Detection</h3>
            <p>Real-time facial emotion analysis using OpenCV and TensorFlow CNN</p>
          </div>
          <div className="feature-card">
            <div className="icon">💬</div>
            <h3>AI Therapist Chat</h3>
            <p>Context-aware conversations with empathy, validation, and techniques</p>
          </div>
          <div className="feature-card">
            <div className="icon">📊</div>
            <h3>Mood Tracking</h3>
            <p>Log daily moods, track patterns, and get personalized insights</p>
          </div>
          <div className="feature-card">
            <div className="icon">🎙️</div>
            <h3>Voice Assistant</h3>
            <p>Speak your feelings — AI transcribes and responds with care</p>
          </div>
          <div className="feature-card">
            <div className="icon">🔔</div>
            <h3>Smart Alerts</h3>
            <p>Intelligent recommendations based on your emotional patterns</p>
          </div>
          <div className="feature-card">
            <div className="icon">🧘</div>
            <h3>Wellness Tools</h3>
            <p>Guided meditation, breathing exercises, and relaxation techniques</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section" id="about">
        <div className="cta-card">
          <div>
            <h2>💬 Chat with Your AI Assistant</h2>
            <p>Talk to our friendly AI bot anytime, anywhere. Feel better through smart, empathetic support powered by machine learning.</p>
            <Link to="/register" className="btn btn-primary btn-lg">Dashboard →</Link>
          </div>
          <div style={{ textAlign: 'center', fontSize: '6rem' }}>
            🤖
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© 2024 MindCare AI — An AI-Driven Mental Health Support Chatbot Using Machine Learning</p>
        <p style={{ marginTop: 4 }}>Not a substitute for professional medical advice.</p>
      </footer>
    </div>
  );
}
