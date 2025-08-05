import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function HackathonPanel() {
  const [hackathons, setHackathons] = useState([]);
  const [userApplications, setUserApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedHackathon, setSelectedHackathon] = useState(null);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [applicationForm, setApplicationForm] = useState({
    team_name: '',
    team_members: [],
    project_idea: '',
    experience_level: 'beginner'
  });
  const { user } = useAuth();

  useEffect(() => {
    fetchHackathons();
    if (user) {
      fetchUserApplications();
    }
  }, [user]);

  const fetchHackathons = async () => {
    try {
      const response = await fetch('http://localhost:8000/hackathon/list');
      if (response.ok) {
        const data = await response.json();
        setHackathons(data.hackathons);
      }
    } catch (error) {
      console.error('Error fetching hackathons:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserApplications = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`http://localhost:8000/hackathon/user/${user.uid}/applications`);
      if (response.ok) {
        const data = await response.json();
        setUserApplications(data.applications);
      }
    } catch (error) {
      console.error('Error fetching user applications:', error);
    }
  };

  const handleApply = (hackathon) => {
    setSelectedHackathon(hackathon);
    setShowApplicationForm(true);
  };

  const handleApplicationSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      alert('Please log in to apply for hackathons');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/hackathon/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          hackathon_id: selectedHackathon.id,
          user_id: user.uid,
          team_name: applicationForm.team_name,
          team_members: applicationForm.team_members,
          project_idea: applicationForm.project_idea,
          skills: JSON.parse(localStorage.getItem('userSkills') || '[]'),
          experience_level: applicationForm.experience_level
        }),
      });

      if (response.ok) {
        alert('Application submitted successfully!');
        setShowApplicationForm(false);
        setApplicationForm({
          team_name: '',
          team_members: [],
          project_idea: '',
          experience_level: 'beginner'
        });
        fetchUserApplications();
      } else {
        const error = await response.json();
        alert(`Application failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error submitting application:', error);
      alert('Failed to submit application. Please try again.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'upcoming': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">🏆 Hackathons</h2>
        <p className="text-gray-600">Join exciting hackathons to showcase your skills and win prizes!</p>
      </div>

      {/* Hackathons List */}
      <div className="grid gap-6">
        {hackathons.map((hackathon) => (
          <div key={hackathon.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">{hackathon.title}</h3>
                  <p className="text-gray-600 mb-4">{hackathon.description}</p>
                </div>
                <div className="flex space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(hackathon.status)}`}>
                    {hackathon.status}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(hackathon.difficulty)}`}>
                    {hackathon.difficulty}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-1">📅 Timeline</h4>
                  <p className="text-sm text-gray-600">
                    {new Date(hackathon.start_date).toLocaleDateString()} - {new Date(hackathon.end_date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-700 mb-1">👥 Participants</h4>
                  <p className="text-sm text-gray-600">
                    {hackathon.participants.length} / {hackathon.max_participants}
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-700 mb-1">🏆 Prizes</h4>
                  <p className="text-sm text-gray-600">{hackathon.prizes.length} prizes available</p>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-gray-700 mb-2">🛠️ Technologies</h4>
                <div className="flex flex-wrap gap-2">
                  {hackathon.technologies.map((tech, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-gray-700 mb-2">🏆 Prizes</h4>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                  {hackathon.prizes.map((prize, index) => (
                    <li key={index}>{prize}</li>
                  ))}
                </ul>
              </div>

              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  Created by Admin • {new Date(hackathon.created_at).toLocaleDateString()}
                </div>
                <button
                  onClick={() => handleApply(hackathon)}
                  disabled={hackathon.status !== 'upcoming' || hackathon.participants.length >= hackathon.max_participants}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    hackathon.status !== 'upcoming' || hackathon.participants.length >= hackathon.max_participants
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-500 text-white hover:bg-blue-600'
                  }`}
                >
                  {hackathon.status !== 'upcoming' 
                    ? 'Applications Closed' 
                    : hackathon.participants.length >= hackathon.max_participants
                    ? 'Full'
                    : 'Apply Now'
                  }
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* User Applications */}
      {userApplications.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">📝 My Applications</h3>
          <div className="space-y-4">
            {userApplications.map((application) => (
              <div key={application.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold text-gray-800">{application.hackathon?.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Team: {application.team_name || 'Individual'}
                    </p>
                    <p className="text-sm text-gray-600">
                      Project: {application.project_idea}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    application.status === 'approved' ? 'bg-green-100 text-green-800' :
                    application.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {application.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Application Modal */}
      {showApplicationForm && selectedHackathon && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              Apply for {selectedHackathon.title}
            </h3>
            
            <form onSubmit={handleApplicationSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team Name (Optional)
                </label>
                <input
                  type="text"
                  value={applicationForm.team_name}
                  onChange={(e) => setApplicationForm(prev => ({ ...prev, team_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter team name or leave blank for individual"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Idea
                </label>
                <textarea
                  value={applicationForm.project_idea}
                  onChange={(e) => setApplicationForm(prev => ({ ...prev, project_idea: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Describe your project idea..."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Experience Level
                </label>
                <select
                  value={applicationForm.experience_level}
                  onChange={(e) => setApplicationForm(prev => ({ ...prev, experience_level: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowApplicationForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 