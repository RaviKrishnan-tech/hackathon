import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { db } from "../firebaseConfig";
import { setDoc, doc } from "firebase/firestore";

export default function Assessment() {
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user"));
  const skills = JSON.parse(localStorage.getItem("userSkills") || "[]");

  useEffect(() => {
    if (skills.length === 0) {
      alert("No skills found. Please upload your resume again.");
      navigate("/resume");
      return;
    }

    async function fetchAssessment() {
      try {
        const res = await fetch("http://localhost:8000/assessment/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills }),
        });

        const data = await res.json();
        setQuestions(data.questions || []);
      } catch (err) {
        console.error("Error generating assessment:", err);
        alert("Failed to generate assessment.");
      } finally {
        setLoading(false);
      }
    }

    fetchAssessment();
  }, [navigate]);

  const handleSelect = (qIndex, option) => {
    setAnswers((prev) => ({ ...prev, [qIndex]: option }));
  };

  const handleSubmit = async () => {
    if (!questions.length || Object.keys(answers).length !== questions.length) {
      alert("Please answer all questions.");
      return;
    }

    try {
      const assessRes = await fetch("http://localhost:8000/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skills }),
      });
      const assessData = await assessRes.json();
      localStorage.setItem("userScores", JSON.stringify(assessData.scores));

      const recommendRes = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scores: assessData.scores }),
      });
      const recommendData = await recommendRes.json();
      localStorage.setItem("learningPath", JSON.stringify(recommendData.modules));

      // ✅ Save everything to Firebase
      await setDoc(doc(db, "userProgress", user.uid), {
        skills,
        scores: assessData.scores,
        modules: recommendData.modules,
        lastUpdated: new Date().toISOString(),
      }, { merge: true });

      navigate("/learning");
    } catch (err) {
      console.error("Submission failed:", err);
      alert("Something went wrong. Try again.");
    }
  };

  return (
    <div className="card">
      <h2 className="text-center">🧠 Your Skill-Based Assessment</h2>

      {loading ? (
        <div className="text-center" style={{ padding: "2rem" }}>
          <span className="animate-spin h-5 w-5 mr-2 border-4 border-blue-500 border-t-transparent rounded-full inline-block"></span>
          Generating your quiz...
        </div>
      ) : questions.length === 0 ? (
        <p className="text-center">No questions generated. Please try again later.</p>
      ) : (
        <div>
          <ol>
            {questions.map((q, index) => (
              <li key={index} style={{ marginBottom: "1.5rem" }}>
                <strong>Q{index + 1}:</strong> {q.question}
                <ul>
                  {q.options.map((opt, i) => (
                    <li key={i}>
                      <label>
                        <input
                          type="radio"
                          name={`q${index}`}
                          value={opt}
                          checked={answers[index] === opt}
                          onChange={() => handleSelect(index, opt)}
                        />{" "}
                        {opt}
                      </label>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ol>
          <div className="text-center">
            <button onClick={handleSubmit}>Submit Answers</button>
          </div>
        </div>
      )}
    </div>
  );
}
