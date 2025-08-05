import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import "../styles.css";

export default function Dashboard() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(
          `http://localhost:8000/admin/dashboard?admin_id=${user?.email}`
        );
        if (!res.ok) throw new Error("Failed to fetch dashboard data");
        const data = await res.json();
        setDashboard(data);
      } catch (err) {
        setError("Could not load dashboard data.");
      } finally {
        setLoading(false);
      }
    }
    if (user?.email) fetchDashboard();
  }, [user]);

  if (loading) return <div className="p-8">Loading admin dashboard...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!dashboard) return null;

  const stats = dashboard.real_time_stats || {};
  const userAnalytics = dashboard.user_analytics || {};
  const systemHealth = dashboard.system_health || {};
  const recentActivities = dashboard.recent_activities || [];

  return (
    <div className="dashboard-container">
      <div className="flex justify-between items-center mb-4">
        <h1 className="dashboard-title">Admin Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>
      <p className="dashboard-subtitle">Welcome, {user?.email}</p>

      {/* Real-time Stats */}
      <div className="metrics-grid">
        <div className="metrics-card">
          <div className="metrics-title">Users (24h)</div>
          <div className="metrics-value">{stats.last_24_hours?.unique_users ?? '-'}</div>
        </div>
        <div className="metrics-card">
          <div className="metrics-title">Activities (24h)</div>
          <div className="metrics-value">{stats.last_24_hours?.total_activities ?? '-'}</div>
        </div>
        <div className="metrics-card">
          <div className="metrics-title">Active Users (7d)</div>
          <div className="metrics-value">{userAnalytics.active_users_7d ?? '-'}</div>
        </div>
        <div className="metrics-card">
          <div className="metrics-title">Total Users</div>
          <div className="metrics-value">{userAnalytics.total_users ?? '-'}</div>
        </div>
        <div className="metrics-card">
          <div className="metrics-title">System Health</div>
          <div className="metrics-value" style={{color: systemHealth.overall_status === 'healthy' ? 'green' : 'red'}}>{systemHealth.overall_status ?? '-'}</div>
        </div>
      </div>

      {/* User Engagement */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-2">Top Users</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded">
            <thead>
              <tr>
                <th className="px-4 py-2">User ID</th>
                <th className="px-4 py-2">Activities</th>
                <th className="px-4 py-2">Last Activity</th>
                <th className="px-4 py-2">Engagement</th>
              </tr>
            </thead>
            <tbody>
              {(userAnalytics.top_users || []).map((u) => (
                <tr key={u.user_id} className="border-t">
                  <td className="px-4 py-2">{u.user_id}</td>
                  <td className="px-4 py-2">{u.total_activities}</td>
                  <td className="px-4 py-2">{u.last_activity?.slice(0, 19).replace('T', ' ')}</td>
                  <td className="px-4 py-2">{u.engagement_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-2">Recent Activity</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded">
            <thead>
              <tr>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">User</th>
                <th className="px-4 py-2">Time</th>
                <th className="px-4 py-2">Description</th>
              </tr>
            </thead>
            <tbody>
              {recentActivities.map((a, i) => (
                <tr key={i} className="border-t">
                  <td className="px-4 py-2">{a.activity_type}</td>
                  <td className="px-4 py-2">{a.user_id}</td>
                  <td className="px-4 py-2">{a.timestamp?.slice(0, 19).replace('T', ' ')}</td>
                  <td className="px-4 py-2">{a.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* System Health */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-2">System Health</h2>
        <div className="bg-white p-4 rounded shadow">
          <div>Status: <span style={{color: systemHealth.overall_status === 'healthy' ? 'green' : 'red'}}>{systemHealth.overall_status}</span></div>
          <div>AI Services: {systemHealth.ai_services}</div>
          <div>Database: {systemHealth.database}</div>
          <div>API Endpoints: {systemHealth.api_endpoints}</div>
          <div>Uptime: {systemHealth.uptime}</div>
          <div>Response Time: {systemHealth.response_time}</div>
        </div>
      </div>
    </div>
  );
}
