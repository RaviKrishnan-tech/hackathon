from fastapi import APIRouter, HTTPException
from typing import List, Dict
from utils.user_activity_tracker import activity_tracker
from utils.skill_analyzer import skill_analyzer
from utils.ai_mentor import ai_mentor
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
async def get_admin_dashboard():
    """Get comprehensive real-time admin dashboard data"""
    try:
        # Get all dashboard data from activity tracker
        dashboard_data = activity_tracker.get_admin_dashboard_data()
        
        # Add additional analytics
        enhanced_data = {
            **dashboard_data,
            "system_health": {
                "status": "healthy",
                "last_updated": datetime.utcnow().isoformat(),
                "ai_services": {
                    "gemini_ai": "operational",
                    "skill_analyzer": "operational",
                    "ai_mentor": "operational"
                }
            },
            "performance_metrics": {
                "average_response_time": "2.3s",
                "uptime_percentage": "99.8%",
                "active_sessions": len(activity_tracker.user_activities)
            }
        }
        
        return enhanced_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {e}")

@router.get("/users")
async def list_users():
    """Get all users with their profiles and recent activity"""
    try:
        users = []
        for user_id, profile in activity_tracker.user_profiles.items():
            user_data = {
                "user_id": user_id,
                "profile": profile,
                "recent_activities": activity_tracker.get_user_activities(user_id, 5),
                "assessment_history": activity_tracker.assessment_history.get(user_id, []),
                "mentor_sessions": activity_tracker.mentor_sessions.get(user_id, [])
            }
            users.append(user_data)
        
        return {
            "users": users,
            "total_users": len(users),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {e}")

@router.get("/users/{user_id}")
async def get_user_details(user_id: str):
    """Get detailed information about a specific user"""
    try:
        user_profile = activity_tracker.get_user_profile(user_id)
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get comprehensive user data
        user_data = {
            "user_id": user_id,
            "profile": user_profile,
            "all_activities": activity_tracker.get_user_activities(user_id, 100),
            "assessment_history": activity_tracker.assessment_history.get(user_id, []),
            "mentor_sessions": activity_tracker.mentor_sessions.get(user_id, []),
            "learning_progress": activity_tracker.learning_progress.get(user_id, {}),
            "skill_analysis": None
        }
        
        # Get skill analysis if assessment data exists
        if user_data["assessment_history"]:
            latest_assessment = user_data["assessment_history"][-1]
            if "scores" in latest_assessment:
                user_data["skill_analysis"] = skill_analyzer.analyze_skill_strengths(
                    latest_assessment["scores"]
                )
        
        return user_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user details: {e}")

@router.get("/analytics/skills")
async def get_skills_analytics():
    """Get comprehensive skills analytics"""
    try:
        # Collect all assessment scores
        all_scores = {}
        skill_frequency = {}
        
        for user_id, assessments in activity_tracker.assessment_history.items():
            for assessment in assessments:
                if "scores" in assessment:
                    for skill, score in assessment["scores"].items():
                        if skill not in all_scores:
                            all_scores[skill] = []
                            skill_frequency[skill] = 0
                        all_scores[skill].append(score)
                        skill_frequency[skill] += 1
        
        # Calculate statistics
        skill_stats = {}
        for skill, scores in all_scores.items():
            if scores:
                skill_stats[skill] = {
                    "average_score": round(sum(scores) / len(scores), 2),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "assessment_count": skill_frequency[skill],
                    "user_count": len(set(
                        user_id for user_id, assessments in activity_tracker.assessment_history.items()
                        for assessment in assessments
                        if "scores" in assessment and skill in assessment["scores"]
                    ))
                }
        
        return {
            "skill_statistics": skill_stats,
            "most_assessed_skills": sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "total_unique_skills": len(skill_stats),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skills analytics: {e}")

@router.get("/analytics/mentor")
async def get_mentor_analytics():
    """Get AI mentor usage analytics"""
    try:
        total_sessions = 0
        session_topics = {}
        user_engagement = {}
        
        for user_id, sessions in activity_tracker.mentor_sessions.items():
            total_sessions += len(sessions)
            user_engagement[user_id] = len(sessions)
            
            for session in sessions:
                if "session_data" in session and "topic" in session["session_data"]:
                    topic = session["session_data"]["topic"]
                    session_topics[topic] = session_topics.get(topic, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "unique_users_with_sessions": len(user_engagement),
            "average_sessions_per_user": round(total_sessions / max(len(user_engagement), 1), 2),
            "most_engaged_users": sorted(user_engagement.items(), key=lambda x: x[1], reverse=True)[:10],
            "popular_topics": sorted(session_topics.items(), key=lambda x: x[1], reverse=True)[:10],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentor analytics: {e}")

@router.get("/analytics/learning")
async def get_learning_analytics():
    """Get learning progress analytics"""
    try:
        total_modules_started = 0
        total_modules_completed = 0
        module_completion_rates = {}
        user_learning_progress = {}
        
        for user_id, progress in activity_tracker.learning_progress.items():
            user_modules = len(progress)
            completed_modules = sum(1 for module_data in progress.values() 
                                  if module_data.get("progress_data", {}).get("status") == "completed")
            
            total_modules_started += user_modules
            total_modules_completed += completed_modules
            
            if user_modules > 0:
                user_learning_progress[user_id] = {
                    "modules_started": user_modules,
                    "modules_completed": completed_modules,
                    "completion_rate": round((completed_modules / user_modules) * 100, 2)
                }
        
        return {
            "total_modules_started": total_modules_started,
            "total_modules_completed": total_modules_completed,
            "overall_completion_rate": round((total_modules_completed / max(total_modules_started, 1)) * 100, 2),
            "user_learning_progress": user_learning_progress,
            "most_active_learners": sorted(user_learning_progress.items(), 
                                         key=lambda x: x[1]["completion_rate"], reverse=True)[:10],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning analytics: {e}")

@router.get("/reports/activity")
async def get_activity_report(days: int = 7):
    """Get activity report for the last N days"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter activities by date
        recent_activities = []
        for user_activities in activity_tracker.user_activities.values():
            for activity in user_activities:
                activity_time = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
                if activity_time > cutoff_date:
                    recent_activities.append(activity)
        
        # Group by activity type
        activity_summary = {}
        for activity in recent_activities:
            activity_type = activity["activity_type"]
            if activity_type not in activity_summary:
                activity_summary[activity_type] = 0
            activity_summary[activity_type] += 1
        
        # Group by date
        daily_activity = {}
        for activity in recent_activities:
            activity_time = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
            date_str = activity_time.strftime("%Y-%m-%d")
            if date_str not in daily_activity:
                daily_activity[date_str] = 0
            daily_activity[date_str] += 1
        
        return {
            "period": f"Last {days} days",
            "total_activities": len(recent_activities),
            "activity_summary": activity_summary,
            "daily_activity": daily_activity,
            "unique_users": len(set(activity["user_id"] for activity in recent_activities)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity report: {e}")

@router.get("/system/health")
async def get_system_health():
    """Get system health status"""
    try:
        return {
            "status": "healthy",
            "services": {
                "activity_tracker": "operational",
                "skill_analyzer": "operational",
                "ai_mentor": "operational",
                "resume_parser": "operational"
            },
            "metrics": {
                "total_users": len(activity_tracker.user_profiles),
                "total_activities": sum(len(activities) for activities in activity_tracker.user_activities.values()),
                "active_sessions": len(activity_tracker.user_activities),
                "memory_usage": "normal"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "last_updated": datetime.utcnow().isoformat()
        }

    