// App.jsx
import React, { useState, useEffect } from 'react';
import './styles/global.css';
import { BrowserRouter as Router, Routes, Route, Navigate, NavLink } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import ChatRoom from './pages/ChatRoom';
import RecipeList from './pages/RecipeList';
import ShoppingList from './pages/ShoppingList';
import UserManagementPage from './pages/UserManagementPage';
import Logout from './pages/Logout';

// Import React Toastify components and styles
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for token in localStorage on initial load
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(token !== null); // Set isLoggedIn based on token presence
  }, []);

  // Listen for changes in localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      const token = localStorage.getItem('token');
      setIsLoggedIn(token !== null);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <Router>
      {/* ToastContainer placed once in the app */}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored" // Optional: choose a theme
      />

      {isLoggedIn ? (
        <div>
          <header>
            <nav>
              <ul className="nav-links">
                <li>
                  <NavLink to="/chat" className={({ isActive }) => (isActive ? 'active' : '')}>
                    Chat
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/recipes" className={({ isActive }) => (isActive ? 'active' : '')}>
                    Recipes
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/shopping" className={({ isActive }) => (isActive ? 'active' : '')}>
                    Shopping List
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/usermanagement" className={({ isActive }) => (isActive ? 'active' : '')}>
                    My account
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/logout" className={({ isActive }) => (isActive ? 'active' : '')}>
                    Logout
                  </NavLink>
                </li>
              </ul>
            </nav>
          </header>

          <main>
            <Routes>
              <Route path="/chat" element={<ChatRoom />} />
              <Route path="/recipes" element={<RecipeList />} />
              <Route path="/shopping" element={<ShoppingList />} />
              <Route path="/usermanagement" element={<UserManagementPage />} />
              <Route path="/logout" element={<Logout setIsLoggedIn={setIsLoggedIn} />} />
              <Route path="/" element={<Navigate to="/recipes" />} /> {/* Default to recipes */}
              <Route path="*" element={<div>Page not found</div>} />
            </Routes>
          </main>
        </div>
      ) : (
        <div>
          <Routes>
            <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Navigate to="/login" />} /> {/* Redirect to login */}
            <Route path="*" element={<Navigate to="/login" />} /> {/* Default to login */}
          </Routes>
        </div>
      )}
    </Router>
  );
}

export default App;
