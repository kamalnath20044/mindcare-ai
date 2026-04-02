import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import AdminRoute from './components/AdminRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import MoodTracker from './pages/MoodTracker';
import WellnessTools from './pages/WellnessTools';
import Analytics from './pages/Analytics';
import Assessment from './pages/Assessment';
import Homework from './pages/Homework';
import AdminDashboard from './pages/AdminDashboard';

// ─── Protected route for patients ───
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', flexDirection: 'column', gap: 16,
      }}>
        <div style={{ fontSize: '2.5rem' }}>🌿</div>
        <p style={{ color: '#9BAB9B', fontSize: '0.9rem' }}>Loading MindCare AI...</p>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

// Layout wrapper — sidebar + main content
function Layout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* ─── Public ─── */}
      <Route path="/" element={user ? <Navigate to={user.is_admin ? '/admin' : '/dashboard'} /> : <Landing />} />
      <Route path="/login" element={user ? <Navigate to={user.is_admin ? '/admin' : '/dashboard'} /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />

      {/* ─── Patient routes (any logged-in user) ─── */}
      <Route path="/dashboard" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
      <Route path="/chat" element={<ProtectedRoute><Layout><Chat /></Layout></ProtectedRoute>} />
      <Route path="/mood" element={<ProtectedRoute><Layout><MoodTracker /></Layout></ProtectedRoute>} />
      <Route path="/wellness" element={<ProtectedRoute><Layout><WellnessTools /></Layout></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><Layout><Analytics /></Layout></ProtectedRoute>} />
      <Route path="/assessment" element={<ProtectedRoute><Layout><Assessment /></Layout></ProtectedRoute>} />
      <Route path="/homework" element={<ProtectedRoute><Layout><Homework /></Layout></ProtectedRoute>} />

      {/* ─── Admin/Therapist routes ─── */}
      <Route path="/admin" element={
        <AdminRoute>
          <Layout><AdminDashboard /></Layout>
        </AdminRoute>
      } />

      {/* ─── Fallback ─── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
