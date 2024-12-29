import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = ({ setIsLoggedIn }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // Remove token from localStorage
    localStorage.removeItem('token');
    // Update the App state
    setIsLoggedIn(false);
    // Redirect to login page
    navigate('/login');
  }, [navigate, setIsLoggedIn]);

  return <div>Logging out...</div>;
};

export default Logout;
