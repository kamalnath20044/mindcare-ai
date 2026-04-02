import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser, API_BASE } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return setError('Please fill in all fields');

    setLoading(true);
    setError('');
    try {
      const res = await loginUser(email, password);
      const { token, user, redirect } = res.data;

      // Store user with is_admin flag
      login(token, user);

      // Role-based redirect:
      // is_admin=true  → /admin (Therapist Dashboard)
      // is_admin=false → /dashboard (Patient Dashboard)
      if (redirect) {
        navigate(redirect);
      } else {
        navigate(user?.is_admin ? '/admin' : '/dashboard');
      }
    } catch (err) {
      if (!err.response) {
        setError(`Cannot connect to API (${API_BASE}). Check VITE_API_URL in your deployment settings.`);
      } else if (err.response.status === 404) {
        setError(`Auth endpoint not found at ${API_BASE}/auth/login.`);
      } else {
        setError(err.response?.data?.detail || 'Login failed. Please try again.');
      }
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Logo */}
        <div className="logo">
          <svg width="56" height="56" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="loginG" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#7CAE7A' }} />
                <stop offset="100%" style={{ stopColor: '#5C8A5A' }} />
              </linearGradient>
            </defs>
            <circle cx="256" cy="256" r="240" fill="url(#loginG)" />
            <path d="M 160 170 Q 160 140, 190 140 L 322 140 Q 352 140, 352 170 L 352 280 Q 352 310, 322 310 L 230 310 L 190 350 L 200 310 L 190 310 Q 160 310, 160 280 Z" fill="white" opacity="0.95" />
            <path d="M 256 180 C 230 210, 220 260, 256 300 C 292 260, 282 210, 256 180 Z" fill="#7CAE7A" opacity="0.75" />
          </svg>
        </div>
        <h1>Welcome Back</h1>
        <p className="subtitle">Sign in as a Patient or Therapist</p>

        {/* Role hint */}
        <div style={{
          display: 'flex', gap: 8, marginBottom: 20, justifyContent: 'center',
        }}>
          <span style={{
            padding: '4px 14px', borderRadius: 20, fontSize: '0.72rem', fontWeight: 600,
            background: '#EAF3E9', color: '#5C8A5A', border: '1px solid #D8E4D8',
          }}>
            🧑‍💻 Patient → Dashboard
          </span>
          <span style={{
            padding: '4px 14px', borderRadius: 20, fontSize: '0.72rem', fontWeight: 600,
            background: '#F4F9F4', color: '#4A7148', border: '1px solid #D8E4D8',
          }}>
            🏥 Therapist → Admin Panel
          </span>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              className="form-input"
              type="email"
              id="login-email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <div className="password-input-wrapper">
              <input
                className="form-input"
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>
          <button
            className="btn btn-primary btn-lg"
            type="submit"
            id="login-submit"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}
          >
            {loading ? '⏳ Signing in...' : '🌿 Sign In'}
          </button>
        </form>

        <p className="auth-link">
          Don't have an account? <Link to="/register">Sign up as Patient</Link>
        </p>
      </div>
    </div>
  );
}
