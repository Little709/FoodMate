// src/pages/Logout.jsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Remove token from localStorage
    localStorage.removeItem('token');
    // Redirect to login page after logging out
    navigate('/login');
  }, [navigate]);

  return <div>Logging out...</div>; // You can display a loading message here
};

export default Logout;
