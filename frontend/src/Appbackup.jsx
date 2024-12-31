import React, { useState, useEffect } from 'react';
import './styles/global.css';
import './styles/dark-mode.css'; // Dark mode overrides
import { BrowserRouter as Router, Routes, Route, Navigate, NavLink, useLocation } from 'react-router-dom';
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

// ProtectedRoute Component
const ProtectedRoute = ({ isLoggedIn, children }) => {
  return isLoggedIn ? children : <Navigate to="/login" />;
};

function AppContent({ isLoggedIn, setIsLoggedIn }) {
    const [isDarkMode, setIsDarkMode] = useState(false);

    useEffect(() => {
        const root = document.documentElement;
        if (!isDarkMode) {
            root.classList.add('dark-mode');
        } else {
            root.classList.remove('dark-mode');
        }
    }, [isDarkMode]);
  const location = useLocation();

  useEffect(() => {
    if (isLoggedIn) {
      localStorage.setItem('lastVisitedPath', location.pathname);
    }
  }, [location, isLoggedIn]);

  return (
    <>
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
        theme="colored"
      />

      {isLoggedIn && (
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
                  My Account
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
      )}

      <main>
        <Routes>
          <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/chat"
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <ChatRoom />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recipes"
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <RecipeList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/shopping"
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <ShoppingList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/usermanagement"
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <UserManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logout"
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <Logout setIsLoggedIn={setIsLoggedIn} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={<Navigate to={isLoggedIn ? localStorage.getItem('lastVisitedPath') || '/recipes' : '/login'} />}
          />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </main>
    </>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
    setLoading(false);
  }, []);

  useEffect(() => {
    const handleStorageChange = () => {
      const token = localStorage.getItem('token');
      setIsLoggedIn(!!token);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <AppContent isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />
    </Router>
  );
}

export default App;
