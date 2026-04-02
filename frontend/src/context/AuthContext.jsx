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
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('mindcare_token');
        localStorage.removeItem('mindcare_user');
      }

      // Verify token in background — also refreshes is_admin from server
      getMe()
        .then(res => {
          const freshUser = {
            id: res.data.user_id,
            user_id: res.data.user_id,
            email: res.data.email,
            name: res.data.name,
            is_admin: res.data.is_admin || false,
          };
          setUser(freshUser);
          localStorage.setItem('mindcare_user', JSON.stringify(freshUser));
        })
        .catch((err) => {
          if (err.response && err.response.status === 401) {
            localStorage.removeItem('mindcare_token');
            localStorage.removeItem('mindcare_user');
            setUser(null);
          }
          // Network error — keep existing session
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

  // Helper: is the current user an admin/therapist?
  const isAdmin = user?.is_admin === true;

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
