// Register.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from "../config";
import '../styles/register.css';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [activityLevel, setActivityLevel] = useState('');
  const [goal, setGoal] = useState('');
  const [error, setError] = useState(null);

  const location = useLocation();  // Access the state passed from Login page
  const navigate = useNavigate();  // To redirect after successful registration

  // If the state from Login page is available, populate the form with the data
  useEffect(() => {
    if (location.state) {
      setUsername(location.state.username || '');
      setPassword(location.state.password || '');
    }
  }, [location]);

  const handleRegister = async (e) => {
    e.preventDefault(); // Prevent form submission from reloading the page
    setError(null);  // Reset error before each attempt

    // Basic Frontend Validation
    if (!username || !password || !age || !sex || !weight || !height || !activityLevel || !goal) {
      setError('Please fill in all required fields.');
      return;
    }

    const userData = {
      username,
      password,
      age: Number(age),
      sex,
      weight: Number(weight),
      height: Number(height),
      activity_level: activityLevel,
      goal,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      const data = await res.json();

      if (res.ok) {
        // Registration successful
        // Instead of alert, navigate to login with state
        navigate('/login', { state: { registrationSuccess: true } });
      } else {
        // Show registration error
        setError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again later.');
      console.error(err);
    }
  };

  return (
    <div className="register-container">
      <div className="card">
        <h2>Register</h2>
        <form onSubmit={handleRegister}>
          <input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="input-field"
            required
          />
          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="input-field"
            required
          />
          <input
            placeholder="Age"
            type="number"
            value={age}
            onChange={e => setAge(e.target.value)}
            className="input-field"
            min="0"
            required
          />
          <select
            value={sex}
            onChange={e => setSex(e.target.value)}
            className="input-field"
            required
          >
            <option value="" disabled>Select Sex</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
          <input
            placeholder="Weight (kg)"
            type="number"
            value={weight}
            onChange={e => setWeight(e.target.value)}
            className="input-field"
            min="0"
            step="0.1"
            required
          />
          <input
            placeholder="Height (cm)"
            type="number"
            value={height}
            onChange={e => setHeight(e.target.value)}
            className="input-field"
            min="0"
            step="0.1"
            required
          />
          <select
            value={activityLevel}
            onChange={e => setActivityLevel(e.target.value)}
            className="input-field"
            required
          >
            <option value="" disabled>Select Activity Level</option>
            <option value="sedentary">Sedentary (little or no exercise)</option>
            <option value="lightly_active">Lightly Active (light exercise/sports 1-3 days/week)</option>
            <option value="moderately_active">Moderately Active (moderate exercise/sports 3-5 days/week)</option>
            <option value="very_active">Very Active (hard exercise/sports 6-7 days a week)</option>
            <option value="extra_active">Extra Active (very hard exercise/sports & physical job or training)</option>
          </select>
          <select
            value={goal}
            onChange={e => setGoal(e.target.value)}
            className="input-field"
            required
          >
            <option value="" disabled>Select Your Goal</option>
            <option value="lose_weight">Lose Weight</option>
            <option value="maintain_weight">Maintain Weight</option>
            <option value="gain_weight">Gain Weight</option>
          </select>
          <button type="submit" className="button">
            Register
          </button>
        </form>

        {/* Show error message if registration failed */}
        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}

export default Register;
