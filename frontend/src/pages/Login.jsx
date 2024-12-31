import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { API_BASE_URL } from "../config";
import '../styles/register.css';
import { toast } from 'react-toastify';

function Login({ setIsLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isIncorrectPassword, setIsIncorrectPassword] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state && location.state.registrationSuccess) {
      toast.success('Registration successful! Please log in.', {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location, navigate]);

  const handleLogin = async () => {
    setError(null);
    setIsIncorrectPassword(false);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();

      if (res.ok) {
        if (data.access_token && data.expiry) {
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('tokenExpiry', new Date(data.expiry).getTime());
          setIsLoggedIn(true);
          navigate('/recipes');
        } else {
          setError('Login failed: Missing token or expiry information.');
        }
      } else if (data.detail === 'Incorrect credentials') {
        setIsIncorrectPassword(true);
      } else {
        setError(data.detail || 'Login failed.');
      }
    } catch (err) {
      console.error('Error during login:', err);
      setError('Login failed: Something went wrong.');
    }
  };

  const handleRegisterRedirect = () => {
    navigate('/register', { state: { username, password } });
  };

  return (
    <div className="register-container">
      <div className="card">
        {/* Logo */}
        <img src="../assets/logo.png" alt="FoodMate Logo" className="logo" />


        <h2>Login</h2>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          className="input-field"
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="input-field"
        />

        {isIncorrectPassword && <div className="error-message">Incorrect password, please try again.</div>}
        {error && <div className="error-message">{error}</div>}

        <div className="buttons-container">
          <button onClick={handleLogin} className="button">Login</button>
          <button onClick={handleRegisterRedirect} className="button">Register</button>
        </div>
      </div>
    </div>
  );
}

export default Login;
