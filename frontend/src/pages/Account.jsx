// frontend/src/pages/RecipeList.jsx
import React, { useEffect, useState } from 'react';

function Account() {
  const [recipes, setRecipes] = useState([]);
  const [rating, setRating] = useState(0);
  const userId = 1; // In reality, store/fetch from localStorage or global auth state

  useEffect(() => {
    fetch('/auth/account')
      .then(res => res.json())
      .then(data => setRecipes(data));
  }, []);

  const handleRate = async (recipeId) => {
    await fetch('/auth/account?user_id=' + userId, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipe_id: recipeId, rating: rating }),
    });
    alert('Recipe rated!');
  };

  return (
    <div>
{/*       <h2>All Recipes</h2> */}
{/*       {recipes.map(r => ( */}
{/*         <div key={r.id}> */}
{/*           <h3>{r.title}</h3> */}
{/*           <p>{r.instructions}</p> */}
{/*           <input */}
{/*             type="number" */}
{/*             min="1" */}
{/*             max="5" */}
{/*             value={rating} */}
{/*             onChange={e => setRating(e.target.value)} */}
{/*           /> */}
{/*           <button onClick={() => handleRate(r.id)}>Rate</button> */}
{/*         </div> */}
{/*       ))} */}
    </div>
  );
}

export default RecipeList;
