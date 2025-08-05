import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { setDoc, doc } from 'firebase/firestore';
import { db } from '../firebaseConfig';

export default function Assessment() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeStarted, setTimeStarted] = useState(null);
  const [results, setResults] = useState(null);
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user"));
  const userSkills = JSON.parse(localStorage.getItem("userSkills") || "[]");

  useEffect(() => {
    if (!user || !user.uid) {
      alert("Please log in to take the assessment");
      navigate("/login");
      return;
    }

    if (!userSkills || userSkills.length === 0) {
      alert("Please upload your resume first to get skills for assessment");
      navigate("/dashboard");
      return;
    }

    generateAssessment();
    setTimeStarted(Date.now());
  }, []);

  const generateAssessment = async () => {
    try {
      console.log("🎯 Generating assessment for skills:", userSkills);
      
      const response = await fetch("http://localhost:8000/assessment/generate", {
          method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          skills: userSkills,
          user_id: user.uid
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ Assessment generated:", data);
      
        setQuestions(data.questions || []);
      setLoading(false);
    } catch (error) {
      console.error("❌ Failed to generate assessment:", error);
      alert("Failed to generate assessment. Please try again.");
        setLoading(false);
      }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      alert("Please answer all questions before submitting.");
      return;
    }

    setSubmitting(true);
    const timeTaken = Math.floor((Date.now() - timeStarted) / 1000); // Convert to seconds

    try {
      const response = await fetch("http://localhost:8000/assessment/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: user.uid,
          answers: answers,
          time_taken: timeTaken
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("✅ Assessment results:", result);
      
      // Save results to Firebase
      await setDoc(
        doc(db, "userProgress", user.uid),
        { 
          assessmentResults: result,
          lastAssessment: new Date().toISOString()
        },
        { merge: true }
      );

      // Save to localStorage
      localStorage.setItem("assessmentResults", JSON.stringify(result));
      
      setResults(result);
    } catch (error) {
      console.error("❌ Failed to submit assessment:", error);
      alert("Failed to submit assessment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const getProgressPercentage = () => {
    return (Object.keys(answers).length / questions.length) * 100;
  };

  const getTimeElapsed = () => {
    if (!timeStarted) return "0:00";
    const elapsed = Math.floor((Date.now() - timeStarted) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Generating your assessment...</h2>
          <p className="text-gray-500 mt-2">Creating personalized questions for your skills</p>
        </div>
      </div>
    );
  }

  if (results) {
    return <AssessmentResults results={results} navigate={navigate} />;
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-700">No questions generated</h2>
          <p className="text-gray-500 mt-2">Please try again or contact support</p>
          <button 
            onClick={() => navigate("/dashboard")}
            className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-gray-800">Skill Assessment</h1>
            <div className="text-right">
              <div className="text-sm text-gray-600">Time Elapsed</div>
              <div className="text-lg font-semibold text-blue-600">{getTimeElapsed()}</div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{Object.keys(answers).length} / {questions.length} questions</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
          </div>

          {/* Question Counter */}
          <div className="text-center">
            <span className="text-sm text-gray-500">
              Question {currentQuestion + 1} of {questions.length}
            </span>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="mb-6">
            <div className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium mb-4">
              {currentQ.skill}
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              {currentQ.question}
            </h2>
          </div>

          {/* Answer Options */}
          <div className="space-y-3">
            {currentQ.options.map((option, index) => (
              <label
                key={index}
                className={`block p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                  answers[currentQ.id] === String.fromCharCode(65 + index)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                        <input
                          type="radio"
                  name={currentQ.id}
                  value={String.fromCharCode(65 + index)}
                  checked={answers[currentQ.id] === String.fromCharCode(65 + index)}
                  onChange={(e) => handleAnswerSelect(currentQ.id, e.target.value)}
                  className="sr-only"
                />
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center mr-3 ${
                    answers[currentQ.id] === String.fromCharCode(65 + index)
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}>
                    {answers[currentQ.id] === String.fromCharCode(65 + index) && (
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    )}
                  </div>
                  <span className="font-medium text-gray-700">
                    {String.fromCharCode(65 + index)}. {option}
                  </span>
                </div>
                      </label>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              currentQuestion === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-500 text-white hover:bg-gray-600'
            }`}
          >
            Previous
          </button>

          <div className="flex space-x-4">
            {currentQuestion < questions.length - 1 ? (
              <button
                onClick={handleNext}
                disabled={!answers[currentQ.id]}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  !answers[currentQ.id]
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting || Object.keys(answers).length < questions.length}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  submitting || Object.keys(answers).length < questions.length
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-500 text-white hover:bg-green-600'
                }`}
              >
                {submitting ? (
                  <>
                    <span className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full inline-block"></span>
                    Submitting...
                  </>
                ) : (
                  'Submit Assessment'
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function AssessmentResults({ results, navigate }) {
  const [showDetails, setShowDetails] = useState(false);

  const getSkillLevelColor = (skill) => {
    if (results.strong_skills.includes(skill)) return "text-green-600 bg-green-100";
    if (results.medium_skills.includes(skill)) return "text-yellow-600 bg-yellow-100";
    return "text-red-600 bg-red-100";
  };

  const getSkillLevelText = (skill) => {
    if (results.strong_skills.includes(skill)) return "Strong";
    if (results.medium_skills.includes(skill)) return "Average";
    return "Weak";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Assessment Complete! 🎉</h1>
          <p className="text-gray-600">Here's your personalized skill analysis and learning recommendations</p>
        </div>

        {/* Overall Analysis */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Overall Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{results.strong_skills.length}</div>
              <div className="text-sm text-green-600">Strong Skills</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{results.medium_skills.length}</div>
              <div className="text-sm text-yellow-600">Average Skills</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{results.weak_skills.length}</div>
              <div className="text-sm text-red-600">Weak Skills</div>
            </div>
          </div>
        </div>

        {/* Skill Breakdown */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Skill Breakdown</h2>
          <div className="space-y-4">
            {Object.entries(results.skill_scores).map(([skill, score]) => (
              <div key={skill} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="font-medium text-gray-800">{skill}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSkillLevelColor(skill)}`}>
                    {getSkillLevelText(skill)}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-800">{score}/10</div>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${score * 10}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Learning Recommendations */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Learning Recommendations</h2>
          <div className="space-y-4">
            {results.learning_recommendations?.weak_skills_focus?.map((rec, index) => (
              <div key={index} className="p-4 bg-red-50 rounded-lg">
                <h3 className="font-semibold text-red-800 mb-2">Focus on: {rec.skill}</h3>
                <p className="text-red-700 mb-2">Priority: {rec.priority}</p>
                <div className="text-sm text-red-600">
                  <p>Learning Path: {rec.learning_path.join(" → ")}</p>
                  <p>Estimated Time: {rec.estimated_time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Mentor Suggestions */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">AI Mentor Suggestions</h2>
          <div className="space-y-3">
            {results.ai_mentor_suggestions?.map((suggestion, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="text-blue-500 mt-1">💡</div>
                <p className="text-blue-800">{suggestion}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => navigate("/learning-path")}
            className="flex-1 px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
          >
            View Learning Path
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="flex-1 px-6 py-3 bg-gray-500 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
