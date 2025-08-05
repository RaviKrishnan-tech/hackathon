from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict
import uuid

class UserActivityTracker:
    def __init__(self):
        self.user_activities = defaultdict(list)
        self.user_profiles = {}
        self.assessment_history = defaultdict(list)
        self.mentor_sessions = defaultdict(list)
        self.learning_progress = defaultdict(dict)
        
    def log_activity(self, user_id: str, activity_type: str, details: Dict = None) -> Dict:
        """Log user activity with timestamp and details"""
        
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        self.user_activities[user_id].append(activity)
        
        # Update user profile based on activity
        self._update_user_profile(user_id, activity)
        
        return activity
    
    def _update_user_profile(self, user_id: str, activity: Dict):
        """Update user profile based on activity"""
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "user_id": user_id,
                "first_seen": activity["timestamp"],
                "last_activity": activity["timestamp"],
                "total_activities": 0,
                "activity_breakdown": defaultdict(int),
                "skills_assessed": set(),
                "mentor_sessions_count": 0,
                "learning_modules_completed": 0,
                "current_learning_path": None
            }
        
        profile = self.user_profiles[user_id]
        profile["last_activity"] = activity["timestamp"]
        profile["total_activities"] += 1
        profile["activity_breakdown"][activity["activity_type"]] += 1
        
        # Update specific metrics based on activity type
        if activity["activity_type"] == "resume_upload":
            if "skills" in activity["details"]:
                profile["skills_assessed"].update(activity["details"]["skills"])
        
        elif activity["activity_type"] == "assessment_completed":
            if "skills" in activity["details"]:
                profile["skills_assessed"].update(activity["details"]["skills"])
        
        elif activity["activity_type"] == "mentor_session":
            profile["mentor_sessions_count"] += 1
        
        elif activity["activity_type"] == "learning_module_completed":
            profile["learning_modules_completed"] += 1
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent activities for a specific user"""
        return self.user_activities[user_id][-limit:]
    
    def get_all_activities(self, limit: int = 100) -> List[Dict]:
        """Get recent activities across all users"""
        all_activities = []
        for user_activities in self.user_activities.values():
            all_activities.extend(user_activities)
        
        # Sort by timestamp and return recent ones
        all_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_activities[:limit]
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get comprehensive user profile"""
        if user_id not in self.user_profiles:
            return {"error": "User not found"}
        
        profile = self.user_profiles[user_id].copy()
        profile["skills_assessed"] = list(profile["skills_assessed"])
        profile["activity_breakdown"] = dict(profile["activity_breakdown"])
        
        # Add recent activities
        profile["recent_activities"] = self.get_user_activities(user_id, 10)
        
        return profile
    
    def get_admin_dashboard_data(self) -> Dict:
        """Get comprehensive data for admin dashboard"""
        
        total_users = len(self.user_profiles)
        total_activities = sum(len(activities) for activities in self.user_activities.values())
        
        # Activity breakdown
        activity_breakdown = defaultdict(int)
        for activities in self.user_activities.values():
            for activity in activities:
                activity_breakdown[activity["activity_type"]] += 1
        
        # Recent activities (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_activities = [
            activity for activities in self.user_activities.values()
            for activity in activities
            if datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00')) > yesterday
        ]
        
        # User engagement metrics
        active_users_24h = len({
            user_id for user_id, activities in self.user_activities.items()
            if any(
                datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00')) > yesterday
                for activity in activities
            )
        })
        
        # Skills assessment statistics
        all_assessed_skills = set()
        for profile in self.user_profiles.values():
            all_assessed_skills.update(profile["skills_assessed"])
        
        # Learning progress statistics
        total_mentor_sessions = sum(profile["mentor_sessions_count"] for profile in self.user_profiles.values())
        total_modules_completed = sum(profile["learning_modules_completed"] for profile in self.user_profiles.values())
        
        return {
            "overview": {
                "total_users": total_users,
                "total_activities": total_activities,
                "active_users_24h": active_users_24h,
                "total_mentor_sessions": total_mentor_sessions,
                "total_modules_completed": total_modules_completed
            },
            "activity_breakdown": dict(activity_breakdown),
            "recent_activities": recent_activities[:20],
            "skills_statistics": {
                "total_unique_skills": len(all_assessed_skills),
                "most_assessed_skills": self._get_most_assessed_skills(),
                "skills_distribution": self._get_skills_distribution()
            },
            "user_engagement": {
                "most_active_users": self._get_most_active_users(),
                "user_activity_trends": self._get_activity_trends()
            },
            "learning_analytics": {
                "completion_rates": self._get_completion_rates(),
                "mentor_session_analytics": self._get_mentor_analytics()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_most_assessed_skills(self) -> List[Dict]:
        """Get most frequently assessed skills"""
        skill_counts = defaultdict(int)
        for profile in self.user_profiles.values():
            for skill in profile["skills_assessed"]:
                skill_counts[skill] += 1
        
        return [
            {"skill": skill, "count": count}
            for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _get_skills_distribution(self) -> Dict:
        """Get distribution of skills across users"""
        skill_distribution = defaultdict(int)
        for profile in self.user_profiles.values():
            skill_count = len(profile["skills_assessed"])
            skill_distribution[skill_count] += 1
        
        return dict(skill_distribution)
    
    def _get_most_active_users(self) -> List[Dict]:
        """Get most active users"""
        user_activity_counts = [
            {
                "user_id": user_id,
                "total_activities": profile["total_activities"],
                "last_activity": profile["last_activity"]
            }
            for user_id, profile in self.user_profiles.items()
        ]
        
        return sorted(user_activity_counts, key=lambda x: x["total_activities"], reverse=True)[:10]
    
    def _get_activity_trends(self) -> Dict:
        """Get activity trends over time"""
        # Group activities by hour for the last 24 hours
        hourly_activity = defaultdict(int)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        for activities in self.user_activities.values():
            for activity in activities:
                activity_time = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
                if activity_time > yesterday:
                    hour = activity_time.strftime("%Y-%m-%d %H:00")
                    hourly_activity[hour] += 1
        
        return dict(hourly_activity)
    
    def _get_completion_rates(self) -> Dict:
        """Get learning module completion rates"""
        total_modules_started = sum(
            profile.get("learning_modules_started", 0) for profile in self.user_profiles.values()
        )
        total_modules_completed = sum(
            profile["learning_modules_completed"] for profile in self.user_profiles.values()
        )
        
        completion_rate = (total_modules_completed / max(total_modules_started, 1)) * 100
        
        return {
            "completion_rate": round(completion_rate, 2),
            "total_started": total_modules_started,
            "total_completed": total_modules_completed
        }
    
    def _get_mentor_analytics(self) -> Dict:
        """Get mentor session analytics"""
        total_sessions = sum(profile["mentor_sessions_count"] for profile in self.user_profiles.values())
        users_with_sessions = sum(1 for profile in self.user_profiles.values() if profile["mentor_sessions_count"] > 0)
        
        return {
            "total_sessions": total_sessions,
            "users_with_sessions": users_with_sessions,
            "average_sessions_per_user": round(total_sessions / max(len(self.user_profiles), 1), 2)
        }
    
    def log_assessment_result(self, user_id: str, skills: List[str], scores: Dict[str, float]) -> Dict:
        """Log assessment results"""
        activity = self.log_activity(user_id, "assessment_completed", {
            "skills": skills,
            "scores": scores,
            "average_score": sum(scores.values()) / len(scores) if scores else 0
        })
        
        # Store in assessment history
        self.assessment_history[user_id].append({
            "timestamp": activity["timestamp"],
            "skills": skills,
            "scores": scores,
            "activity_id": activity["id"]
        })
        
        return activity
    
    def log_mentor_session(self, user_id: str, session_data: Dict) -> Dict:
        """Log mentor session"""
        activity = self.log_activity(user_id, "mentor_session", session_data)
        
        # Store in mentor sessions
        self.mentor_sessions[user_id].append({
            "timestamp": activity["timestamp"],
            "session_data": session_data,
            "activity_id": activity["id"]
        })
        
        return activity
    
    def log_learning_progress(self, user_id: str, module_id: str, progress_data: Dict) -> Dict:
        """Log learning module progress"""
        activity = self.log_activity(user_id, "learning_progress", {
            "module_id": module_id,
            "progress_data": progress_data
        })
        
        # Update learning progress
        if user_id not in self.learning_progress:
            self.learning_progress[user_id] = {}
        
        self.learning_progress[user_id][module_id] = {
            "last_updated": activity["timestamp"],
            "progress_data": progress_data
        }
        
        return activity

# Global tracker instance
activity_tracker = UserActivityTracker() 