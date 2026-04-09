import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Zap, Map as MapIcon, History, LogOut, Sun, Moon, Settings } from 'lucide-react';

const DashboardLayout = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(
    window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  useEffect(() => {
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Chargers', path: '/chargers', icon: Zap },
    { name: 'Map View', path: '/map', icon: MapIcon },
    { name: 'Bookings', path: '/bookings', icon: History },
  ];

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <Zap size={24} />
          <span>ChargeFlow</span>
        </div>
        
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink 
              key={item.path} 
              to={item.path} 
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <item.icon size={20} />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item" onClick={handleLogout} style={{ width: '100%', textAlign: 'left', border: 'none', background: 'transparent', cursor: 'pointer' }}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-header">
          <div style={{ fontWeight: 600 }}>Welcome back!</div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button onClick={toggleTheme} className="btn-outline" style={{ padding: '0.4rem' }}>
              {isDark ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <div style={{ padding: '0.5rem', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary)' }}>
              <Settings size={20} />
            </div>
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
