// frontend/src/pages/ShoppingList.jsx
import React, { useState } from 'react';

function ShoppingList() {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState('');

  const addItem = () => {
    setItems([...items, newItem]);
    setNewItem('');
  };

  return (
    <div>
      <h2>Shopping List</h2>
      <ul>
        {items.map((i, idx) => (
          <li key={idx}>{i}</li>
        ))}
      </ul>
      <input
        placeholder="New item..."
        value={newItem}
        onChange={e => setNewItem(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && addItem()}
      />
      <button onClick={addItem}>Add</button>
    </div>
  );
}

export default ShoppingList;
