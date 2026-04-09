import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, LogIn } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    console.log("Login attempt:");
    console.log("Email:", email);
    console.log("Password:", password);
    console.log("Password length:", password.length);
    
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      console.log("FINAL ERROR:", err);
      console.log("Error type:", typeof err);
      console.log("Error message:", err.message);
      
      setError(
        typeof err === "string"
          ? err
          : err?.message
          ? err.message
          : JSON.stringify(err)
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', textAlign: 'center' }}>Sign in to your account</h2>
      {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>{String(error)}</div>}
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label className="input-label" htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            className="input-control"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="input-group">
          <label className="input-label" htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            className="input-control"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn-primary" style={{ width: '100%', marginBottom: '1.5rem' }} disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'} <ArrowRight size={18} />
        </button>
      </form>
      <div style={{ textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Don't have an account? <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>Create account</Link>
      </div>
    </div>
  );
};

export default Login;
