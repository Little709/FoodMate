import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from "../config";
import '../styles/usermanagement.css';

function UserManagementPage() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

    const fetchUser = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE_URL}/management/account`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          console.log("Fetched user data:", data); // Debugging line
          setUser(data);
        } else {
          setError("Failed to fetch user information.");
        }
      } catch (err) {
        setError("An error occurred.");
      }
    };


    const handleUpdate = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE_URL}/management/account`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(user),
        });
        if (!res.ok) throw new Error("Failed to update user information.");
        alert("User information updated successfully!");
      } catch (err) {
        setError("An error occurred.");
      }
    };


    useEffect(() => {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("You need to log in to access your account.");
        navigate("/login"); // Redirect to login
        return;
      }
      fetchUser();
    }, []);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setUser((prev) => ({ ...prev, [name]: value }));
  };

  if (!user) return <div>Loading...</div>;

  return (
    <div className="usermanagement-container">
      <h1>Manage Account</h1>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={(e) => e.preventDefault()}>
        <input
          type="text"
          name="username"
          value={user.username}
          onChange={handleChange}
          placeholder="Username"
          className="input-field"
        />
        <input
          type="number"
          name="age"
          value={user.age}
          onChange={handleChange}
          placeholder="Age"
          className="input-field"
        />
        <select
          name="sex"
          value={user.sex}
          onChange={handleChange}
          className="input-field"
        >
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>
        <input
          type="number"
          name="weight"
          value={user.weight}
          onChange={handleChange}
          placeholder="Weight (kg)"
          className="input-field"
        />
        <input
          type="number"
          name="height"
          value={user.height}
          onChange={handleChange}
          placeholder="Height (cm)"
          className="input-field"
        />
        <select
          name="activity_level"
          value={user.activity_level}
          onChange={handleChange}
          className="input-field"
        >
          <option value="sedentary">Sedentary</option>
          <option value="lightly_active">Lightly Active</option>
          <option value="moderately_active">Moderately Active</option>
          <option value="very_active">Very Active</option>
          <option value="extra_active">Extra Active</option>
        </select>
        <select
          name="goal"
          value={user.goal}
          onChange={handleChange}
          className="input-field"
        >
          <option value="lose_weight">Lose Weight</option>
          <option value="maintain_weight">Maintain Weight</option>
          <option value="gain_weight">Gain Weight</option>
        </select>
        <button onClick={handleUpdate} className="button">Update</button>
      </form>
    </div>
  );
}


export default UserManagementPage;
