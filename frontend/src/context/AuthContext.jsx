import { createContext, useContext, useState, useEffect } from 'react';
import { getMe } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('mindcare_token');
    const savedUser = localStorage.getItem('mindcare_user');

    if (token && savedUser) {
      // Restore user from localStorage immediately (instant login, no network needed)
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        // Corrupted data — clear and force re-login
        localStorage.removeItem('mindcare_token');
        localStorage.removeItem('mindcare_user');
      }

      // Verify token is still valid in the background (non-blocking)
      getMe()
        .then(res => {
          // Token is valid — update user data if needed
          const freshUser = {
            id: res.data.user_id,
            user_id: res.data.user_id,
            email: res.data.email,
            name: res.data.name,
          };
          setUser(freshUser);
          localStorage.setItem('mindcare_user', JSON.stringify(freshUser));
        })
        .catch((err) => {
          // Only clear token if it's actually expired/invalid (401)
          // Do NOT clear on network errors (backend not running yet)
          if (err.response && err.response.status === 401) {
            console.log('[Auth] Token expired — logging out');
            localStorage.removeItem('mindcare_token');
            localStorage.removeItem('mindcare_user');
            setUser(null);
          } else {
            // Network error or backend not running — keep the user logged in
            console.log('[Auth] Backend unreachable — keeping session from localStorage');
          }
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('mindcare_token', token);
    localStorage.setItem('mindcare_user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('mindcare_token');
    localStorage.removeItem('mindcare_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
