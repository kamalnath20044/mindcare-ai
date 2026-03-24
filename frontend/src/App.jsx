import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import EmotionDetection from './pages/EmotionDetection';
import MoodTracker from './pages/MoodTracker';
import WellnessTools from './pages/WellnessTools';
import Analytics from './pages/Analytics';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', fontSize: '1.2rem', color: '#999' }}>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={user ? <Navigate to="/dashboard" /> : <Landing />} />
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />

      {/* Protected routes */}
      <Route path="/dashboard" element={<ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-content"><Dashboard /></main></div></ProtectedRoute>} />
      <Route path="/chat" element={<ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-content"><Chat /></main></div></ProtectedRoute>} />
      <Route path="/emotion" element={<ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-content"><EmotionDetection /></main></div></ProtectedRoute>} />
      <Route path="/mood" element={<ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-content"><MoodTracker /></main></div></ProtectedRoute>} />
      <Route path="/wellness" element={<ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-content"><WellnessTools /></main></div></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-content"><Analytics /></main></div></ProtectedRoute>} />
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
