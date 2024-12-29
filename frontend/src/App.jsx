import React, { useEffect, useState } from 'react';
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

// Import Toastify Container
import { ToastContainer } from 'react-toastify';
import './services/styles/ReactToastify.css';

// Import Notification Service
import { notifySuccess, notifyError } from './services/notificationService';

const AuthMiddleware = ({ isLoggedIn, children }) => {
  const location = useLocation();
  const publicRoutes = ['/login', '/register'];

  if (!isLoggedIn && !publicRoutes.includes(location.pathname)) {
    return <Navigate to="/login" />;
  }

  return children;
};

function AppContent({ isLoggedIn, setIsLoggedIn, notifySuccess, notifyError }) {
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
        autoClose={1000}
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
        <AuthMiddleware isLoggedIn={isLoggedIn}>
          <Routes>
            <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/chat"
              element={<ChatRoom notifySuccess={notifySuccess} notifyError={notifyError} />}
            />
            <Route
              path="/recipes"
              element={<RecipeList notifySuccess={notifySuccess} notifyError={notifyError} />}
            />
            <Route
              path="/shopping"
              element={<ShoppingList notifySuccess={notifySuccess} notifyError={notifyError} />}
            />
            <Route
              path="/usermanagement"
              element={<UserManagementPage notifySuccess={notifySuccess} notifyError={notifyError} />}
            />
            <Route path="/logout" element={<Logout setIsLoggedIn={setIsLoggedIn} />} />
            <Route
              path="/"
              element={<Navigate to={isLoggedIn ? localStorage.getItem('lastVisitedPath') || '/recipes' : '/login'} />}
            />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        </AuthMiddleware>
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
      <AppContent
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        notifySuccess={notifySuccess}
        notifyError={notifyError}
      />
    </Router>
  );
}

export default App;
