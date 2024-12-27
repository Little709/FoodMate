import React, { useEffect, useState } from 'react';

function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [rating, setRating] = useState(0);

  // Get token from localStorage
  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('user_id');  // Get user_id from localStorage

  useEffect(() => {
    // Check if the user is logged in (i.e., token exists)
    if (!token) {
//       alert('You must be logged in to view recipes!');
      return;  // Prevent fetching recipes if no token is found
    }

    // Fetch the list of recipes, passing the token in the Authorization header
    fetch('/recipes/list', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,  // Pass token in Authorization header
        'Content-Type': 'application/json',
      },
    })
      .then(res => res.json())
      .then(data => setRecipes(data))  // Set recipes in the state
      .catch(err => {
        console.error('Error fetching recipes:', err);
//         alert('Failed to fetch recipes');
      });
  }, [token]);  // Re-run this useEffect if the token changes

  const handleRate = async (recipeId) => {
    if (!token || !userId) {
//       alert('You must be logged in to rate recipes');
      return;  // Prevent rating if token or user_id is missing
    }

    // Send a rating for the recipe, passing token and user_id in the Authorization header
    await fetch('/recipes/rate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,  // Pass token in Authorization header
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ recipe_id: recipeId, rating: rating, user_id: userId }), // Pass rating and user_id
    })
      .then(res => res.json())
      .then(() => alert('Recipe rated!'))  // Alert after successfully rating the recipe
      .catch(err => {
        console.error('Error rating recipe:', err);
//         alert('Failed to rate recipe');
      });
  };

  return (
    <div>
      <h2>All Recipes</h2>
      {recipes.map(r => (
        <div key={r.id}>
          <h3>{r.title}</h3>
          <p>{r.instructions}</p>
          <input
            type="number"
            min="1"
            max="5"
            value={rating}
            onChange={e => setRating(e.target.value)}  // Update the rating state
          />
          <button onClick={() => handleRate(r.id)}>Rate</button>
        </div>
      ))}
    </div>
  );
}

export default RecipeList;
