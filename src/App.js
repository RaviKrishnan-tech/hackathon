import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard"; // Admin
import LoginPage from "./pages/LoginPage"; // Login
import UserDash from "./user/UserDash";    // User
import { getDoc, doc } from "firebase/firestore";
import { db } from "./firebaseConfig";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import ResumeUploader from "./user/components/ResumeUploader";
import Assessment from "./pages/Assessment"; // Add this page
import LearningPathTable from "./user/components/LearningPathTable";

function AppWrapper() {
  const [user, setUser] = useState(null);
  const [initialRoute, setInitialRoute] = useState("/resume");

  useEffect(() => {
    const checkProgress = async () => {
      const storedUser = JSON.parse(localStorage.getItem("user"));
      if (storedUser) {
        setUser(storedUser);

        const snap = await getDoc(doc(db, "userProgress", storedUser.uid));
        if (snap.exists()) {
          const progress = snap.data();
          if (progress.modules?.length > 0) {
            setInitialRoute("/learning");
          } else if (progress.scores) {
            setInitialRoute("/recommend");
          } else if (progress.skills?.length > 0) {
            setInitialRoute("/assessment");
          }
        }
      }
    };
    checkProgress();
  }, []);

  if (!user) {
    return <LoginPage onLogin={(loggedInUser) => {
      setUser(loggedInUser);
      localStorage.setItem("user", JSON.stringify(loggedInUser));
    }} />;
  }

  const isAdmin = user.email === "mavadmin@gmail.com";

  return (
    <BrowserRouter>
      <Routes>
        {isAdmin ? (
          <Route path="/*" element={<Dashboard />} />
        ) : (
          <>
            <Route path="/resume" element={<ResumeUploader />} />
            <Route path="/assessment" element={<Assessment />} />
            <Route path="/learning" element={<LearningPathTable />} />
            <Route path="/" element={<Navigate to={initialRoute} />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  );
}

export default AppWrapper;
