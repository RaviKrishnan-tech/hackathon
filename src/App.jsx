import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard"; // Admin dashboard
import LoginPage from "./pages/LoginPage"; // Login page
import UserDash from "./user/UserDash"; // User dashboard
import Assessment from "./user/Assessment"; // Skill-based quiz
import LearningPathTable from "./user/LearningPathTable"; // Personalized learning path
import "./styles.css"; // Main styles

export default function App() {
  const [user, setUser] = useState(null);

  const isAdmin = user?.email === "mavadmin@gmail.com"; // simple check

  return (
    <Router>
      <Routes>
        {!user ? (
          <Route path="*" element={<LoginPage onLogin={(u) => setUser(u)} />} />
        ) : isAdmin ? (
          <Route path="*" element={<Dashboard />} />
        ) : (
          <>
            <Route path="/" element={<UserDash />} />
            <Route path="/user/assessment" element={<Assessment />} />
            <Route path="/user/learning" element={<LearningPathTable />} />
          </>
        )}
      </Routes>
    </Router>
  );
}
