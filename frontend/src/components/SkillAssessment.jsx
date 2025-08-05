import { useState } from "react";

export default function SkillAssessment({ skills, userId }) {
  const [assessments, setAssessments] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentAssessment, setCurrentAssessment] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const generateAssessments = async () => {
    if (!skills?.length) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/assessment/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skills: skills, user_id: userId || "default-user" }),
      });
      if (!response.ok) throw new Error(`Failed to generate assessments: ${response.status}`);
      const data = await response.json();
      setAssessments(data.questions);
    } catch (err) {
      setError(err.message || "Failed to generate assessments");
    } finally {
      setLoading(false);
    }
  };

  const startAssessment = (skill) => {
    const skillQuestions = assessments.filter(q => q.skill === skill);
    setCurrentAssessment({ skill, questions: skillQuestions, currentQuestion: 0 });
    setAnswers({});
  };

  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const submitAssessment = async () => {
    if (!currentAssessment || !userId) return;
    setSubmitting(true);
    try {
      const response = await fetch("http://localhost:8000/assessment/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, answers: answers, time_taken: 300 }),
      });
      if (!response.ok) throw new Error(`Failed to submit assessment: ${response.status}`);
      await response.json();
      alert(`Assessment completed! Check your skill analysis.`);
      setCurrentAssessment(null);
      setAnswers({});
    } catch (err) {
      setError(err.message || "Failed to submit assessment");
    } finally {
      setSubmitting(false);
    }
  };

  const nextQuestion = () => {
    if (currentAssessment.currentQuestion < currentAssessment.questions.length - 1) {
      setCurrentAssessment(prev => ({ ...prev, currentQuestion: prev.currentQuestion + 1 }));
    }
  };
  const prevQuestion = () => {
    if (currentAssessment.currentQuestion > 0) {
      setCurrentAssessment(prev => ({ ...prev, currentQuestion: prev.currentQuestion - 1 }));
    }
  };

  if (!skills?.length) return null;

  return (
    <div className="space-y-6">
      {!assessments && (
        <div className="text-center">
          <button
            onClick={generateAssessments}
            disabled={loading}
            className={`px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl'}`}
          >
            {loading ? 'Generating Assessments...' : 'Generate AI-Powered Assessments'}
          </button>
        </div>
      )}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <span className="text-red-800">{error}</span>
        </div>
      )}
      {assessments && !currentAssessment && (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Available Assessments</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {skills.map((skill) => {
              const skillQuestions = assessments.filter(q => q.skill === skill);
              return (
                <div key={skill} className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-800">{skill}</h4>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">{skillQuestions.length} questions</span>
                  </div>
                  <p className="text-gray-600 mb-4">Test your knowledge in {skill} with AI-generated questions</p>
                  <button
                    onClick={() => startAssessment(skill)}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                  >Start Assessment</button>
                </div>
              );
            })}
          </div>
        </div>
      )}
      {currentAssessment && (
        <div className="bg-white p-8 rounded-xl shadow-xl border border-gray-200">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-bold text-gray-800">{currentAssessment.skill} Assessment</h3>
              <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">Question {currentAssessment.currentQuestion + 1} of {currentAssessment.questions.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
              <div className="bg-blue-600 h-2 rounded-full transition-all duration-300" style={{ width: `${((currentAssessment.currentQuestion + 1) / currentAssessment.questions.length) * 100}%` }}></div>
            </div>
          </div>
          {currentAssessment.questions[currentAssessment.currentQuestion] && (
            <div className="space-y-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="text-lg font-semibold text-gray-800 mb-4">{currentAssessment.questions[currentAssessment.currentQuestion].question}</h4>
                <div className="space-y-3">
                  {currentAssessment.questions[currentAssessment.currentQuestion].options.map((option, index) => (
                    <label key={index} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                      <input
                        type="radio"
                        name={`question-${currentAssessment.questions[currentAssessment.currentQuestion].id}`}
                        value={option}
                        checked={answers[currentAssessment.questions[currentAssessment.currentQuestion].id] === option}
                        onChange={() => handleAnswerSelect(currentAssessment.questions[currentAssessment.currentQuestion].id, option)}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex justify-between items-center">
                <button
                  onClick={prevQuestion}
                  disabled={currentAssessment.currentQuestion === 0}
                  className={`px-4 py-2 rounded-lg transition-colors ${currentAssessment.currentQuestion === 0 ? 'bg-gray-300 cursor-not-allowed' : 'bg-gray-600 hover:bg-gray-700 text-white'}`}
                >Previous</button>
                {currentAssessment.currentQuestion === currentAssessment.questions.length - 1 ? (
                  <button
                    onClick={submitAssessment}
                    disabled={submitting || Object.keys(answers).length < currentAssessment.questions.length}
                    className={`px-6 py-2 rounded-lg font-semibold transition-colors ${submitting || Object.keys(answers).length < currentAssessment.questions.length ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 text-white'}`}
                  >{submitting ? 'Submitting...' : 'Submit Assessment'}</button>
                ) : (
                  <button
                    onClick={nextQuestion}
                    disabled={!answers[currentAssessment.questions[currentAssessment.currentQuestion].id]}
                    className={`px-4 py-2 rounded-lg transition-colors ${!answers[currentAssessment.questions[currentAssessment.currentQuestion].id] ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
                  >Next</button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}