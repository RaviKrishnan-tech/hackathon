import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LearningPathTable from "../user/components/LearningPathTable";

export default function LearningPath() {
  const [loading, setLoading] = useState(true);
  const [modules, setModules] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const scores = JSON.parse(localStorage.getItem("userSkillScores") || "{}");

    if (Object.keys(scores).length === 0) {
      alert("No skill scores found. Please complete the assessment first.");
      navigate("/assessment");
      return;
    }

    async function fetchPath() {
      try {
        const res = await fetch("http://localhost:8000/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scores }),
        });

        const data = await res.json();
        setModules(data.modules || []);
      } catch (err) {
        console.error("Error fetching learning path:", err);
        alert("Failed to generate learning path. Try again.");
      } finally {
        setLoading(false);
      }
    }

    fetchPath();
  }, [navigate]);

  return (
    <div className="card">
      <h2 className="text-center">📚 Your Personalized Learning Path</h2>
      {loading ? (
        <div className="text-center" style={{ padding: "2rem" }}>
          <span className="animate-spin h-5 w-5 mr-2 border-4 border-blue-500 border-t-transparent rounded-full inline-block"></span>
          Creating your roadmap...
        </div>
      ) : modules.length === 0 ? (
        <p className="text-center">No modules generated. Please try again later.</p>
      ) : (
        <LearningPathTable modules={modules} />
      )}
    </div>
  );
}
