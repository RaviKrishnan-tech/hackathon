import { useState, useEffect } from "react";

export default function LearningPathTable({ weakSkills, userId }) {
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (weakSkills && weakSkills.length > 0 && userId) {
      generateLearningPath();
    }
    // eslint-disable-next-line
  }, [weakSkills, userId]);

  const generateLearningPath = async () => {
    if (!weakSkills?.length || !userId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/recommend/learning-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          scores: Object.fromEntries(weakSkills.map(skill => [skill, 5.0])),
          learning_goals: ["Improve technical skills", "Career advancement"],
          preferred_learning_style: "mixed"
        }),
      });
      if (!response.ok) throw new Error(`Failed to generate learning path: ${response.status}`);
      const data = await response.json();
      setLearningPath(data);
    } catch (err) {
      setError(err.message || "Failed to generate learning path");
    } finally {
      setLoading(false);
    }
  };

  const markModuleComplete = async (moduleId) => {
    if (!userId || !moduleId) return;
    try {
      const response = await fetch(`http://localhost:8000/recommend/${userId}/complete-module`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module_id: moduleId,
          completion_data: {
            completed_at: new Date().toISOString(),
            score: 100
          }
        }),
      });
      if (response.ok) {
        setLearningPath(prev => ({
          ...prev,
          learning_path: prev.learning_path.map(module =>
            module.id === moduleId ? { ...module, completed: true } : module
          )
        }));
      }
    } catch (err) {
      // ignore
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="flex items-center justify-center mb-4">
          <svg className="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <p className="text-gray-600">Generating your personalized learning path...</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <span className="text-red-800">{error}</span>
      </div>
    );
  }
  if (!learningPath || !learningPath.learning_path || learningPath.learning_path.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <p className="text-gray-600">No learning modules available yet.</p>
        <button
          onClick={generateLearningPath}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >Generate Learning Path</button>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-bold text-gray-800">Your Learning Journey</h3>
          <div className="text-right">
            <p className="text-sm text-gray-600">Estimated Duration</p>
            <p className="text-lg font-semibold text-blue-600">{learningPath.total_estimated_weeks} weeks</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Total Modules</p>
            <p className="text-2xl font-bold text-gray-800">{learningPath.learning_path.length}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Focus Areas</p>
            <p className="text-lg font-semibold text-gray-800">{learningPath.focus_areas.length}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Completed</p>
            <p className="text-2xl font-bold text-green-600">{learningPath.learning_path.filter(m => m.completed).length}</p>
          </div>
        </div>
        {learningPath.focus_areas.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">Focus Areas:</p>
            <div className="flex flex-wrap gap-2">
              {learningPath.focus_areas.map((area, index) => (
                <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">{area}</span>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="space-y-4">
        <h4 className="text-xl font-bold text-gray-800">Learning Modules</h4>
        {learningPath.learning_path.map((module, index) => (
          <div key={module.id} className={`bg-white p-6 rounded-xl shadow-lg border-2 transition-all duration-200 ${module.completed ? 'border-green-200 bg-green-50' : 'border-gray-200 hover:border-blue-300'}`}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h5 className="text-lg font-semibold text-gray-800">{module.title}</h5>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${module.level === 'high' ? 'bg-red-100 text-red-800' : module.level === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>{module.level} priority</span>
                  {module.completed && (<span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">✓ Completed</span>)}
                </div>
                <p className="text-gray-600 mb-3">Estimated time: {module.estimated_hours} hours</p>
                {module.learning_objectives && module.learning_objectives.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-semibold text-gray-700 mb-1">Learning Objectives:</p>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                      {module.learning_objectives.slice(0, 3).map((objective, idx) => (<li key={idx}>{objective}</li>))}
                    </ul>
                  </div>
                )}
                {module.resources && module.resources.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-semibold text-gray-700 mb-1">Resources:</p>
                    <div className="flex flex-wrap gap-2">
                      {module.resources.slice(0, 3).map((resource, idx) => (<span key={idx} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">{resource}</span>))}
                    </div>
                  </div>
                )}
              </div>
              <div className="ml-4">
                {!module.completed ? (
                  <button onClick={() => markModuleComplete(module.id)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">Mark Complete</button>
                ) : (
                  <div className="text-green-600">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className={`h-2 rounded-full transition-all duration-300 ${module.completed ? 'bg-green-500' : 'bg-blue-500'}`} style={{ width: module.completed ? '100%' : '0%' }}></div>
            </div>
          </div>
        ))}
      </div>
      {learningPath.success_metrics && learningPath.success_metrics.length > 0 && (
        <div className="bg-gray-50 p-6 rounded-xl">
          <h4 className="text-lg font-bold text-gray-800 mb-3">Success Metrics</h4>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            {learningPath.success_metrics.map((metric, index) => (<li key={index}>{metric}</li>))}
          </ul>
        </div>
      )}
    </div>
  );
}