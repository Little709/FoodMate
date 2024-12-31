// Login.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { API_BASE_URL } from "../config";
import '../styles/register.css';
import { toast } from 'react-toastify'; // Import toast from react-toastify

function Login({ setIsLoggedIn }) { // Include setIsLoggedIn prop
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isIncorrectPassword, setIsIncorrectPassword] = useState(false); // Tracks if the password is incorrect
  const navigate = useNavigate();
  const location = useLocation(); // Access location state

    useEffect(() => {
      if (location.state && location.state.registrationSuccess) {
        // Trigger toast notification
        toast.success('Registration successful! Please log in.', {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });

        // Clear the state to prevent the message from showing again
        navigate(location.pathname, { replace: true, state: {} });
      }
    }, [location, navigate]);


    const handleLogin = async () => {
      setError(null); // Reset error before each attempt
      setIsIncorrectPassword(false); // Reset incorrect password state

      try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (res.ok) {
          if (data.access_token && data.expiry) {
            localStorage.setItem('token', data.access_token); // Save the token
            localStorage.setItem('tokenExpiry', new Date(data.expiry).getTime()); // Save the token expiry
            setIsLoggedIn(true); // Update the login state
            navigate('/recipes'); // Redirect to /recipes
          } else {
            setError('Login failed: Missing token or expiry information.');
          }
        } else if (data.detail === 'Incorrect credentials') {
          setIsIncorrectPassword(true); // Show incorrect password message
        } else {
          setError(data.detail || 'Login failed.');
        }
      } catch (err) {
        console.error('Error during login:', err);
        setError('Login failed: Something went wrong.');
      }
    };


  const handleRegisterRedirect = () => {
    // Pass username and password to the Register page
    navigate('/register', { state: { username, password } });
  };

  return (
    <div className="register-container">
      <div className="card">
        <h2>Login</h2>

        {/* Display toast notification if registration was successful */}
        {/* No need for additional JSX as toast is handled by ToastContainer */}

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

        {/* Show error messages if login failed */}
        {isIncorrectPassword && <div className="error-message">Incorrect password, please try again.</div>}
        {error && <div className="error-message">{error}</div>}

        {/* Buttons container */}
        <div className="buttons-container">
          <button onClick={handleLogin} className="button">Login</button>
          <button onClick={handleRegisterRedirect} className="button">Register</button>
        </div>
      </div>
    </div>
  );
}

export default Login;
