import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * AdminRoute — Protects routes that require is_admin=true.
 *
 * Usage in App.jsx:
 *   <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
 *
 * Behavior:
 *   - Not logged in   → redirect to /login
 *   - Logged in, not admin → redirect to /dashboard (with a message)
 *   - Logged in, is_admin  → renders the protected component
 */
export default function AdminRoute({ children }) {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', flexDirection: 'column', gap: 16,
      }}>
        <div style={{ fontSize: '2.5rem' }}>🌿</div>
        <p style={{ color: '#9BAB9B', fontSize: '0.9rem' }}>Verifying access...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin) {
    // Patient tried to access admin — redirect to their dashboard
    return <Navigate to="/dashboard" replace state={{ error: 'Admin access required.' }} />;
  }

  return children;
}
