import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import Dashboard from './pages/Dashboard';
import UserDash from './user/UserDash';
import Assessment from './pages/Assessment';
import LearningPath from './pages/LearningPath';
import AIMentor from './components/AIMentor';
import HackathonPanel from './components/HackathonPanel';
import './styles.css';

function AppRoutes() {
  const { user, loading } = useAuth();
  const isAdmin = user && user.email === 'mavadmin@gmail.com';

  if (loading) return <div>Loading...</div>;

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      {isAdmin ? (
        <>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </>
      ) : (
        <>
          <Route path="/user-dashboard" element={<UserDash />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/learning-path" element={<LearningPath />} />
          <Route path="/hackathons" element={<HackathonPanel />} />
          <Route path="*" element={<Navigate to="/user-dashboard" replace />} />
        </>
      )}
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
          {/* Global AI Mentor - Available on all pages */}
          <AIMentor />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
