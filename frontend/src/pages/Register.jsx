import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from "../config";
import '../styles/register.css';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    age: '',
    sex: '',
    weight: '',
    height: '',
    activity_level: '',
    goal: '',
  });

  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (res.ok) {
        navigate('/login', { state: { registrationSuccess: true } });
      } else {
        setError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again later.');
    }
  };

  return (
    <div className="register-container">
      <div className="card">
        <h2>Register</h2>
        <form onSubmit={handleRegister}>
          <input
            placeholder="Username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="input-field"
            required
          />
          <input
            placeholder="Password"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="input-field"
            required
          />
          <input
            placeholder="Age"
            type="number"
            name="age"
            value={formData.age}
            onChange={handleChange}
            className="input-field"
            min="0"
            required
          />
          <select
            name="sex"
            value={formData.sex}
            onChange={handleChange}
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
            name="weight"
            value={formData.weight}
            onChange={handleChange}
            className="input-field"
            min="0"
            step="0.1"
            required
          />
          <input
            placeholder="Height (cm)"
            type="number"
            name="height"
            value={formData.height}
            onChange={handleChange}
            className="input-field"
            min="0"
            step="0.1"
            required
          />
          <select
            name="activity_level"
            value={formData.activity_level}
            onChange={handleChange}
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
            name="goal"
            value={formData.goal}
            onChange={handleChange}
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

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}

export default Register;
