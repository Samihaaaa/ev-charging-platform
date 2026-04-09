import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null); // Could extract user info from token if needed

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      // Ideally fetch user profile here if backend supports it
    } else {
      localStorage.removeItem('token');
      setUser(null);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const data = await api.login(email, password);
      setToken(data.access_token);
    } catch (err) {
      // Always extract string message
      const errorMessage =
        typeof err === "string"
          ? err
          : err?.message
          ? err.message
          : JSON.stringify(err);
      
      throw new Error(errorMessage);
    }
  };

  const register = async (email, password) => {
    await api.register(email, password);
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
