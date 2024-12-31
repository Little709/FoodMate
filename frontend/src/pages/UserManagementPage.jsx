import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from "../config";
import '../styles/usermanagement.css';
import { notifySuccess, notifyError } from '../services/notificationService';

function UserManagementPage() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [newCuisine, setNewCuisine] = useState("");
  const [newIngredient, setNewIngredient] = useState("");
  const [newLikedIngredient, setNewLikedIngredient] = useState("");
  const [newAllergy, setNewAllergy] = useState("");

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
      const updatedUser = { ...user };
      delete updatedUser.id; // Remove ID
      const res = await fetch(`${API_BASE_URL}/management/account`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedUser),
      });
      if (!res.ok) throw new Error("Failed to update user information.");
      notifySuccess("User information updated successfully!");
    } catch (err) {
      setError("An error occurred.");
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setUser((prev) => ({
      ...prev,
      [name]: name === "weight" || name === "height" || name === "age" ? parseFloat(value) : value,
    }));
  };

  const addItem = (key, newItem, setNewItem) => {
    if (!newItem.trim()) {
      notifyError("Input cannot be empty.");
      return;
    }
    if (newItem.length > 50) {
      notifyError("Input is too long (max 50 characters).");
      return;
    }
    setUser((prev) => ({
      ...prev,
      [key]: [...(prev[key] || []), newItem.trim()],
    }));
    setNewItem("");
  };

  const removeItem = (key, index) => {
    setUser((prev) => {
      const updatedItems = [...(prev[key] || [])];
      updatedItems.splice(index, 1);
      return { ...prev, [key]: updatedItems };
    });
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("You need to log in to access your account.");
      navigate("/login");
      return;
    }
    fetchUser();
  }, []);

  if (!user) return <div>Loading...</div>;

  return (
    <div>




      <div className="usermanagement-container">
        <div className="section-box">
          <h1>Taste and diet</h1>
          <h2>Dietary Preferences</h2>
          <select
            name="dietary_preference"
            value={user.dietary_preference || ""}
            onChange={handleChange}
            className="input-field"
          >
            <option value="">Select Dietary Preference</option>
            <option value="vegan">Vegan</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="pescatarian">Pescatarian</option>
            <option value="keto">Keto</option>
            <option value="paleo">Paleo</option>
            <option value="gluten_free">Gluten-Free</option>
            <option value="fodmap">FODMAP</option>
            <option value="other">Other, fill in under advanced</option>
          </select>
          <h2>Preferred Cuisines</h2>
          <div>
            {user.preferred_cuisines && user.preferred_cuisines.map((cuisine, index) => (
              <div key={index} className="input-group input-with-button">
                <input
                  type="text"
                  value={cuisine}
                  readOnly
                  className="input-field"
                />
                <button type="button" onClick={() => removeItem("preferred_cuisines", index)} className="inline-button remove-button">-</button>
              </div>
            ))}
          </div>
          <div className="input-group input-with-button">
            <input
              type="text"
              value={newCuisine}
              onChange={(e) => setNewCuisine(e.target.value)}
              placeholder="Add a cuisine"
              className="input-field"
            />
            <button type="button" onClick={() => addItem("preferred_cuisines", newCuisine, setNewCuisine)} className="inline-button add-button">+</button>
          </div>
          <h2>Liked Ingredients</h2>
          <div>
            {user.liked_ingredients && user.liked_ingredients.map((ingredient, index) => (
              <div key={index} className="input-group input-with-button">
                <input
                  type="text"
                  value={ingredient}
                  readOnly
                  className="input-field"
                />
                <button type="button" onClick={() => removeItem("liked_ingredients", index)} className="inline-button remove-button">-</button>
              </div>
            ))}
          </div>
          <div className="input-group input-with-button">
            <input
              type="text"
              value={newLikedIngredient}
              onChange={(e) => setNewLikedIngredient(e.target.value)}
              placeholder="Add a liked ingredient"
              className="input-field"
            />
            <button type="button" onClick={() => addItem("liked_ingredients", newLikedIngredient, setNewLikedIngredient)} className="inline-button add-button">+</button>
          </div>

          <h2>Disliked Ingredients</h2>
          <div>
            {user.disliked_ingredients && user.disliked_ingredients.map((ingredient, index) => (
              <div key={index} className="input-group input-with-button">
                <input
                  type="text"
                  value={ingredient}
                  readOnly
                  className="input-field"
                />
                <button type="button" onClick={() => removeItem("disliked_ingredients", index)} className="inline-button remove-button">-</button>
              </div>
            ))}
          </div>
          <div className="input-group input-with-button">
            <input
              type="text"
              value={newIngredient}
              onChange={(e) => setNewIngredient(e.target.value)}
              placeholder="Add a disliked ingredient"
              className="input-field"
            />
            <button type="button" onClick={() => addItem("disliked_ingredients", newIngredient, setNewIngredient)} className="inline-button add-button">+</button>
          </div>

          <h2>Allergies</h2>
          <div>
            {user.allergies && user.allergies.map((allergy, index) => (
              <div key={index} className="input-group input-with-button">
                <input
                  type="text"
                  value={allergy}
                  readOnly
                  className="input-field"
                />
                <button type="button" onClick={() => removeItem("allergies", index)} className="inline-button remove-button">-</button>
              </div>
            ))}
          </div>
          <div className="input-group input-with-button">
            <input
              type="text"
              value={newAllergy}
              onChange={(e) => setNewAllergy(e.target.value)}
              placeholder="Add an allergy"
              className="input-field"
            />
            <button type="button" onClick={() => addItem("allergies", newAllergy, setNewAllergy)} className="inline-button add-button">+</button>
          </div>
        </div>
      </div>

      <div className="usermanagement-container">
        <div className="section-box">
          <h1>Advanced</h1>

          <h2>Meal Timing Preferences</h2>
          <select
            name="meal_timing"
            value={user.meal_timing || ""}
            onChange={handleChange}
            className="input-field"
          >
            <option value="">Select Meal Timing</option>
            <option value="intermittent_fasting">Intermittent Fasting</option>
            <option value="regular_meals">Regular Meals</option>
            <option value="small_frequent_meals">Small Frequent Meals</option>
          </select>

          <h2>Portion Size</h2>
          <select
            name="portion_size"
            value={user.portion_size || ""}
            onChange={handleChange}
            className="input-field"
          >
            <option value="">Select Portion Size</option>
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>

          <h2>Snack Preferences</h2>
          <select
            name="snack_preference"
            value={user.snack_preference || ""}
            onChange={handleChange}
            className="input-field"
          >
            <option value="">Select Snack Preference</option>
            <option value="healthy">Healthy</option>
            <option value="sweet">Sweet</option>
            <option value="salty">Salty</option>
            <option value="none">None</option>
          </select>

          <h2>Personal Story</h2>
          <textarea
            name="personal_story"
            value={user.personal_story || ""}
            onChange={handleChange}
            placeholder="If we missed something, tell us about your dietary preferences, restrictions, or goals (e.g., vegetarian, gluten-free, or managing specific health conditions)."
            className="textarea-field"
            rows="6"
          />
        </div>
      </div>

      <div className="usermanagement-container">
        <div className="section-box">
          <h1>Physical Information</h1>
          <form onSubmit={(e) => e.preventDefault()}>
            <div className="input-group">
              <input
                type="number"
                name="weight"
                value={user.weight || ""}
                onChange={handleChange}
                placeholder="Weight"
                className="input-field input-with-unit"
              />
              <span className="unit-inline">kg</span>
            </div>
            <select
              name="activity_level"
              value={user.activity_level || ""}
              onChange={handleChange}
              className="input-field"
            >
              <option value="">Select Activity Level</option>
              <option value="sedentary">Sedentary</option>
              <option value="lightly_active">Lightly Active</option>
              <option value="moderately_active">Moderately Active</option>
              <option value="very_active">Very Active</option>
              <option value="extra_active">Extra Active</option>
            </select>
            <select
              name="goal"
              value={user.goal || ""}
              onChange={handleChange}
              className="input-field"
            >
              <option value="">Select Goal</option>
              <option value="lose_weight">Lose Weight</option>
              <option value="maintain_weight">Maintain Weight</option>
              <option value="gain_weight">Gain Weight</option>
            </select>
          </form>
        </div>
      </div>

      <div className="usermanagement-container">
        <div className="section-box" style={{ marginBottom: '20px' }}>
          <h1>User Details</h1>
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
            <div className="input-group">
              <input
                type="number"
                name="height"
                value={user.height || ""}
                onChange={handleChange}
                placeholder="Height"
                className="input-field input-with-unit"
              />
              <span className="unit-inline">cm</span>
            </div>
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
          </form>
        </div>
      </div>


      <div className="usermanagement-container">
        <button onClick={handleUpdate} className="button">Update</button>
      </div>

    </div>
  );
}

export default UserManagementPage;
