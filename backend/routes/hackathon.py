from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from utils.user_activity_tracker import activity_tracker
import uuid

router = APIRouter(prefix="/hackathon", tags=["Hackathon"])

class HackathonCreate(BaseModel):
    title: str
    description: str
    start_date: str
    end_date: str
    max_participants: int
    prizes: List[str]
    requirements: List[str]
    technologies: List[str]
    difficulty: str  # beginner, intermediate, advanced
    admin_id: str

class HackathonApplication(BaseModel):
    hackathon_id: str
    user_id: str
    team_name: Optional[str] = None
    team_members: List[str] = []
    project_idea: str
    skills: List[str]
    experience_level: str

class HackathonSubmission(BaseModel):
    hackathon_id: str
    user_id: str
    project_name: str
    project_description: str
    github_link: Optional[str] = None
    demo_link: Optional[str] = None
    presentation_link: Optional[str] = None

# In-memory storage (replace with database in production)
hackathons = {}
applications = {}
submissions = {}

@router.post("/create")
async def create_hackathon(payload: HackathonCreate):
    """Create a new hackathon (Admin only)"""
    
    print(f"🏆 Creating hackathon: {payload.title}")
    
    hackathon_id = str(uuid.uuid4())
    
    hackathon_data = {
        "id": hackathon_id,
        "title": payload.title,
        "description": payload.description,
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "max_participants": payload.max_participants,
        "prizes": payload.prizes,
        "requirements": payload.requirements,
        "technologies": payload.technologies,
        "difficulty": payload.difficulty,
        "admin_id": payload.admin_id,
        "status": "upcoming",  # upcoming, active, completed
        "participants": [],
        "applications": [],
        "submissions": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    hackathons[hackathon_id] = hackathon_data
    
    # Log hackathon creation
    activity_tracker.log_activity(payload.admin_id, "hackathon_created", {
        "hackathon_id": hackathon_id,
        "title": payload.title,
        "difficulty": payload.difficulty,
        "max_participants": payload.max_participants,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "hackathon_id": hackathon_id,
        "message": "Hackathon created successfully",
        "hackathon": hackathon_data
    }

@router.get("/list")
async def list_hackathons(status: Optional[str] = None, difficulty: Optional[str] = None):
    """List all hackathons with optional filters"""
    
    filtered_hackathons = list(hackathons.values())
    
    if status:
        filtered_hackathons = [h for h in filtered_hackathons if h["status"] == status]
    
    if difficulty:
        filtered_hackathons = [h for h in filtered_hackathons if h["difficulty"] == difficulty]
    
    # Sort by start date
    filtered_hackathons.sort(key=lambda x: x["start_date"])
    
    return {
        "hackathons": filtered_hackathons,
        "total_count": len(filtered_hackathons),
        "filters_applied": {
            "status": status,
            "difficulty": difficulty
        }
    }

@router.get("/{hackathon_id}")
async def get_hackathon_details(hackathon_id: str):
    """Get detailed information about a specific hackathon"""
    
    if hackathon_id not in hackathons:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    hackathon = hackathons[hackathon_id]
    
    # Get applications and submissions for this hackathon
    hackathon_applications = [
        app for app in applications.values() 
        if app["hackathon_id"] == hackathon_id
    ]
    
    hackathon_submissions = [
        sub for sub in submissions.values() 
        if sub["hackathon_id"] == hackathon_id
    ]
    
    return {
        "hackathon": hackathon,
        "applications": hackathon_applications,
        "submissions": hackathon_submissions,
        "stats": {
            "total_applications": len(hackathon_applications),
            "total_submissions": len(hackathon_submissions),
            "participation_rate": len(hackathon_applications) / hackathon["max_participants"] * 100 if hackathon["max_participants"] > 0 else 0
        }
    }

@router.post("/apply")
async def apply_for_hackathon(payload: HackathonApplication):
    """Apply for a hackathon"""
    
    print(f"📝 User {payload.user_id} applying for hackathon {payload.hackathon_id}")
    
    if payload.hackathon_id not in hackathons:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    hackathon = hackathons[payload.hackathon_id]
    
    # Check if hackathon is accepting applications
    if hackathon["status"] != "upcoming":
        raise HTTPException(status_code=400, detail="Hackathon is not accepting applications")
    
    # Check if user already applied
    existing_application = next(
        (app for app in applications.values() 
         if app["hackathon_id"] == payload.hackathon_id and app["user_id"] == payload.user_id),
        None
    )
    
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied for this hackathon")
    
    # Check if hackathon is full
    if len(hackathon["participants"]) >= hackathon["max_participants"]:
        raise HTTPException(status_code=400, detail="Hackathon is full")
    
    application_id = str(uuid.uuid4())
    
    application_data = {
        "id": application_id,
        "hackathon_id": payload.hackathon_id,
        "user_id": payload.user_id,
        "team_name": payload.team_name,
        "team_members": payload.team_members,
        "project_idea": payload.project_idea,
        "skills": payload.skills,
        "experience_level": payload.experience_level,
        "status": "pending",  # pending, approved, rejected
        "applied_at": datetime.utcnow().isoformat(),
        "reviewed_at": None,
        "admin_notes": None
    }
    
    applications[application_id] = application_data
    
    # Add to hackathon participants
    hackathon["participants"].append(payload.user_id)
    hackathon["applications"].append(application_id)
    
    # Log application
    activity_tracker.log_activity(payload.user_id, "hackathon_applied", {
        "hackathon_id": payload.hackathon_id,
        "hackathon_title": hackathon["title"],
        "team_name": payload.team_name,
        "project_idea": payload.project_idea[:100] + "..." if len(payload.project_idea) > 100 else payload.project_idea,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "application_id": application_id,
        "message": "Application submitted successfully",
        "application": application_data
    }

@router.post("/{hackathon_id}/review-application")
async def review_application(hackathon_id: str, application_id: str, admin_id: str, 
                           status: str, notes: Optional[str] = None):
    """Review hackathon application (Admin only)"""
    
    if application_id not in applications:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = applications[application_id]
    
    if application["hackathon_id"] != hackathon_id:
        raise HTTPException(status_code=400, detail="Application does not belong to this hackathon")
    
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    application["status"] = status
    application["reviewed_at"] = datetime.utcnow().isoformat()
    application["admin_notes"] = notes
    
    # Log application review
    activity_tracker.log_activity(admin_id, "hackathon_application_reviewed", {
        "hackathon_id": hackathon_id,
        "application_id": application_id,
        "user_id": application["user_id"],
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "message": f"Application {status}",
        "application": application
    }

@router.post("/submit-project")
async def submit_project(payload: HackathonSubmission):
    """Submit project for hackathon"""
    
    print(f"🚀 User {payload.user_id} submitting project for hackathon {payload.hackathon_id}")
    
    if payload.hackathon_id not in hackathons:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    hackathon = hackathons[payload.hackathon_id]
    
    # Check if hackathon is active
    if hackathon["status"] != "active":
        raise HTTPException(status_code=400, detail="Hackathon is not active for submissions")
    
    # Check if user is approved participant
    user_application = next(
        (app for app in applications.values() 
         if app["hackathon_id"] == payload.hackathon_id and app["user_id"] == payload.user_id),
        None
    )
    
    if not user_application or user_application["status"] != "approved":
        raise HTTPException(status_code=400, detail="You are not an approved participant")
    
    # Check if user already submitted
    existing_submission = next(
        (sub for sub in submissions.values() 
         if sub["hackathon_id"] == payload.hackathon_id and sub["user_id"] == payload.user_id),
        None
    )
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="You have already submitted a project")
    
    submission_id = str(uuid.uuid4())
    
    submission_data = {
        "id": submission_id,
        "hackathon_id": payload.hackathon_id,
        "user_id": payload.user_id,
        "project_name": payload.project_name,
        "project_description": payload.project_description,
        "github_link": payload.github_link,
        "demo_link": payload.demo_link,
        "presentation_link": payload.presentation_link,
        "submitted_at": datetime.utcnow().isoformat(),
        "score": None,
        "feedback": None,
        "rank": None
    }
    
    submissions[submission_id] = submission_data
    
    # Add to hackathon submissions
    hackathon["submissions"].append(submission_id)
    
    # Log project submission
    activity_tracker.log_activity(payload.user_id, "hackathon_project_submitted", {
        "hackathon_id": payload.hackathon_id,
        "hackathon_title": hackathon["title"],
        "project_name": payload.project_name,
        "submission_id": submission_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "submission_id": submission_id,
        "message": "Project submitted successfully",
        "submission": submission_data
    }

@router.get("/user/{user_id}/applications")
async def get_user_applications(user_id: str):
    """Get all hackathon applications for a user"""
    
    user_applications = [
        app for app in applications.values() 
        if app["user_id"] == user_id
    ]
    
    # Add hackathon details to each application
    for app in user_applications:
        hackathon_id = app["hackathon_id"]
        if hackathon_id in hackathons:
            app["hackathon"] = hackathons[hackathon_id]
    
    return {
        "user_id": user_id,
        "applications": user_applications,
        "total_applications": len(user_applications)
    }

@router.get("/user/{user_id}/submissions")
async def get_user_submissions(user_id: str):
    """Get all hackathon submissions for a user"""
    
    user_submissions = [
        sub for sub in submissions.values() 
        if sub["user_id"] == user_id
    ]
    
    # Add hackathon details to each submission
    for sub in user_submissions:
        hackathon_id = sub["hackathon_id"]
        if hackathon_id in hackathons:
            sub["hackathon"] = hackathons[hackathon_id]
    
    return {
        "user_id": user_id,
        "submissions": user_submissions,
        "total_submissions": len(user_submissions)
    }

@router.get("/admin/{admin_id}/hackathons")
async def get_admin_hackathons(admin_id: str):
    """Get all hackathons created by an admin"""
    
    admin_hackathons = [
        hackathon for hackathon in hackathons.values() 
        if hackathon["admin_id"] == admin_id
    ]
    
    return {
        "admin_id": admin_id,
        "hackathons": admin_hackathons,
        "total_hackathons": len(admin_hackathons)
    }
