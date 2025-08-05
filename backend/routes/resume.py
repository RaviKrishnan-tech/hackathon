from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from utils.enhanced_resume_parser import resume_parser
from utils.user_activity_tracker import activity_tracker
import uuid

router = APIRouter(prefix="/resume", tags=["Resume"])

class ResumeResponse(BaseModel):
    user_id: str
    extracted_skills: List[str]
    experience_level: str
    years_of_experience: int
    education: List[Dict]
    projects: List[Dict]
    certifications: List[str]
    skill_categories: Dict
    career_summary: str
    recommended_learning_path: List[Dict]
    assessment_plan: Dict

@router.post("/process", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        print(f"📁 Processing resume: {file.filename}")
        
        # Generate user ID for tracking
        user_id = str(uuid.uuid4())
        print(f"🆔 Generated user ID: {user_id}")
        
        # Parse resume using enhanced AI parser
        resume_data = resume_parser.parse_resume(file.file)
        print(f"📊 Resume parsing completed. Skills found: {len(resume_data.get('extracted_skills', []))}")
        print(f"📋 Skills: {resume_data.get('extracted_skills', [])}")
        
        # Check if skills were found
        if not resume_data.get("extracted_skills") or len(resume_data["extracted_skills"]) == 0:
            print("⚠️ No skills found in resume, but continuing...")
            print("🔍 Resume data structure:", resume_data.keys())
            # Don't raise error, continue with empty skills array
        
        # Generate assessment plan based on extracted skills
        assessment_plan = resume_parser.generate_skill_assessment_plan(
            resume_data["extracted_skills"], 
            resume_data["experience_level"]
        )
        
        # Log activity
        activity_tracker.log_activity(user_id, "resume_upload", {
            "filename": file.filename,
            "skills": resume_data["extracted_skills"],
            "experience_level": resume_data["experience_level"],
            "years_of_experience": resume_data["years_of_experience"]
        })
        
        response_data = ResumeResponse(
            user_id=user_id,
            extracted_skills=resume_data["extracted_skills"],
            experience_level=resume_data["experience_level"],
            years_of_experience=resume_data["years_of_experience"],
            education=resume_data["education"],
            projects=resume_data["projects"],
            certifications=resume_data["certifications"],
            skill_categories=resume_data["skill_categories"],
            career_summary=resume_data["career_summary"],
            recommended_learning_path=resume_data["recommended_learning_path"],
            assessment_plan=assessment_plan
        )
        
        print(f"✅ Resume processing successful. Returning {len(response_data.extracted_skills)} skills.")
        return response_data

    except Exception as e:
        print(f"❌ Resume processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

@router.get("/{user_id}/analysis")
async def get_resume_analysis(user_id: str):
    """Get detailed resume analysis for a user"""
    try:
        user_profile = activity_tracker.get_user_profile(user_id)
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user_id,
            "profile": user_profile,
            "recent_activities": activity_tracker.get_user_activities(user_id, 10)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {e}")
