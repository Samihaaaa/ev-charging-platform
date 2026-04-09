import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout = () => {
  return (
    <div className="auth-layout">
      <div className="auth-card card">
        <div className="auth-header">
          <h1>EV Platform</h1>
          <p>Charge up your journey</p>
        </div>
        <Outlet />
      </div>
    </div>
  );
};

export default AuthLayout;
