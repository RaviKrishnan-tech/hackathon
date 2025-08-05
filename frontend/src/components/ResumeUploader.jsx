import { useState } from "react";
import SkillChart from "./SkillChart";
import SkillAssessment from "./SkillAssessment";
import LearningPathTable from "./LearningPathTable";

export default function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [step, setStep] = useState(0); // 0: upload, 1: skills, 2: assessment, 3: learning path
  const [skillScores, setSkillScores] = useState(null);
  const [assessmentDone, setAssessmentDone] = useState(false);
  const [learningPathDone, setLearningPathDone] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        setError("Please upload a PDF file only.");
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }
      setFile(selectedFile);
      setError(null);
      setResumeData(null);
      setStep(0);
      setSkillScores(null);
      setAssessmentDone(false);
      setLearningPathDone(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF file first!");
      return;
    }
    setLoading(true);
    setError(null);
    try {
        const formData = new FormData();
        formData.append("file", file);
      const response = await fetch("http://localhost:8000/resume/process", {
          method: "POST",
          body: formData,
        });
      const data = await response.json();
      console.log("Resume API response:", data);
      if (!data.extracted_skills || data.extracted_skills.length === 0) {
        // Continue with empty skills - don't show error
        console.log("No skills found, but continuing with empty skills array");
      }
      setResumeData(data);
      // Generate initial skill scores for chart
      const scores = data.extracted_skills.map((skill) => ({
        name: skill,
        score: Math.floor(Math.random() * 10) + 1,
      }));
      setSkillScores(scores);
      setStep(2); // Immediately go to assessment step after upload
    } catch (err) {
      setError(err.message || "Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Navigation handlers
  const goToNext = () => setStep((s) => s + 1);
  const goToPrev = () => setStep((s) => s - 1);

  // Called by SkillAssessment when done
  const handleAssessmentComplete = () => {
    setAssessmentDone(true);
    goToNext();
  };

  // Called by LearningPathTable when done (optional, for future expansion)
  const handleLearningPathComplete = () => {
    setLearningPathDone(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            AI-Powered Resume Analysis
          </h1>
          <p className="text-lg text-gray-600">
            Upload your resume and get instant skill analysis, personalized assessments, and learning recommendations
          </p>
        </div>
        {/* Step 0: Upload */}
        {step === 0 && (
          <div className="bg-white rounded-2xl p-8 shadow-xl mb-8">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Upload Your Resume
              </h2>
              <p className="text-gray-600">
                Supported format: PDF only (max 10MB)
              </p>
            </div>
      <input
        type="file"
              accept=".pdf"
        onChange={handleFileChange}
        className="mb-4 w-full"
      />
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <span className="text-red-800">{error}</span>
              </div>
            )}
      <button
        onClick={handleUpload}
        disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full mt-2"
      >
        {loading ? "Uploading..." : "Upload & Extract Skills"}
      </button>
          </div>
        )}
        {/* Step 1: Show Extracted Skills (no longer used, but kept for possible future use) */}
        {step === 1 && resumeData && (
          <div className="space-y-8">
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-green-800">
                Resume Analysis Complete! Found {resumeData.extracted_skills.length} technical skills
              </h3>
            </div>
            <div className="bg-white rounded-2xl p-8 shadow-xl">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Extracted Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {resumeData.extracted_skills.map((skill, index) => (
                  <span key={index} className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
              <div className="mt-8 flex justify-end">
                <button
                  onClick={goToNext}
                  className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 hidden"
                  style={{display: 'none'}} // Hide Next button
                >
                  Next: Skill Assessment
                </button>
              </div>
            </div>
          </div>
        )}
        {/* Step 2: Skill Assessment */}
        {step === 2 && resumeData && (
          <div className="space-y-8">
            <div className="bg-white rounded-2xl p-8 shadow-xl">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Skill Assessment
              </h3>
              <SkillChart skills={skillScores} />
              <SkillAssessment
                skills={resumeData.extracted_skills}
                userId={resumeData.user_id}
                onComplete={handleAssessmentComplete}
              />
              <div className="mt-8 flex justify-between">
                <button
                  onClick={goToPrev}
                  className="bg-gray-400 text-white px-6 py-2 rounded hover:bg-gray-500"
                >
                  Back
                </button>
                <button
                  onClick={assessmentDone ? goToNext : undefined}
                  disabled={!assessmentDone}
                  className={`px-6 py-2 rounded ${assessmentDone ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
                >
                  Next: Learning Path
                </button>
              </div>
            </div>
          </div>
        )}
        {/* Step 3: Learning Path */}
        {step === 3 && resumeData && (
          <div className="space-y-8">
            <div className="bg-white rounded-2xl p-8 shadow-xl">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Personalized Learning Path
              </h3>
              <LearningPathTable
                weakSkills={resumeData.extracted_skills}
                userId={resumeData.user_id}
                onComplete={handleLearningPathComplete}
              />
              <div className="mt-8 flex justify-between">
                <button
                  onClick={goToPrev}
                  className="bg-gray-400 text-white px-6 py-2 rounded hover:bg-gray-500"
                >
                  Back
                </button>
                <button
                  disabled
                  className="px-6 py-2 rounded bg-gray-300 text-gray-500 cursor-not-allowed"
                >
                  Done
                </button>
              </div>
            </div>
        </div>
      )}
      </div>
    </div>
  );
}