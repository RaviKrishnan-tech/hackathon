// src/user/UserDashboard.jsx

import ResumeUploader from "./components/ResumeUploader";
import ProgressStepper from "./components/ProgressStepper";
import LearningPathTable from "./components/LearningPathTable";
import Leaderboard from "./components/Leaderboard";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import "../styles.css"; // adjust path based on your folder structure

export default function UserDash() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-center">Mavericks Coding Platform - User Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>
      {/* Step progress tracker */}
      <ProgressStepper currentStep={2} />
      {/* Resume upload section */}
      <ResumeUploader />
      {/* Personalized learning path table */}
      <LearningPathTable />
      {/* Leaderboard */}
      <Leaderboard />
    </div>
  );
}
