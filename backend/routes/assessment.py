from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
from utils.skill_analyzer import skill_analyzer
from utils.user_activity_tracker import activity_tracker
from utils.ai_mentor import ai_mentor

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(prefix="/assessment", tags=["Assessment"])

class SkillList(BaseModel):
    skills: List[str]
    user_id: str

class AssessmentSubmission(BaseModel):
    user_id: str
    answers: Dict[str, str]  # question_id: selected_answer
    time_taken: int  # in seconds

class AssessmentResult(BaseModel):
    user_id: str
    skill_scores: Dict[str, float]
    strong_skills: List[str]
    medium_skills: List[str]
    weak_skills: List[str]
    overall_analysis: Dict
    learning_recommendations: Dict
    ai_mentor_suggestions: List[str]

@router.post("/generate")
async def generate_assessment(payload: SkillList):
    if not payload.skills:
        raise HTTPException(status_code=400, detail="No skills provided")

    model = genai.GenerativeModel("gemini-pro")
    questions = []

    for skill in payload.skills:
        try:
            # Enhanced prompt for better question generation
            prompt = (
                f"Generate 3 comprehensive multiple-choice questions to assess knowledge in '{skill}'. "
                f"Questions should cover different difficulty levels (beginner, intermediate, advanced). "
                f"Format each question as:\n\n"
                f"Question: <detailed question text>\n"
                f"Options: A. <option>, B. <option>, C. <option>, D. <option>\n"
                f"Answer: <A/B/C/D>\n"
                f"Explanation: <brief explanation of the correct answer>\n"
                f"Difficulty: <beginner/intermediate/advanced>\n\n"
                f"---\n\n"
            )

            response = model.generate_content(prompt)
            result = response.text.strip().split("---")[0].strip()

            for block in result.split("Question:")[1:]:
                parts = block.strip().split("\n")
                q_text = parts[0]
                
                # Extract options
                opts_line = next((line for line in parts if line.startswith("Options:")), "")
                options = opts_line.replace("Options:", "").strip().split(", ")
                options = [opt[3:] if opt.startswith(("A. ", "B. ", "C. ", "D. ")) else opt for opt in options]
                
                # Extract answer
                answer_line = next((line for line in parts if line.startswith("Answer:")), "")
                correct = answer_line.replace("Answer:", "").strip()
                
                # Extract explanation
                explanation_line = next((line for line in parts if line.startswith("Explanation:")), "")
                explanation = explanation_line.replace("Explanation:", "").strip()
                
                # Extract difficulty
                difficulty_line = next((line for line in parts if line.startswith("Difficulty:")), "")
                difficulty = difficulty_line.replace("Difficulty:", "").strip()

                questions.append({
                    "id": f"{skill}_{len(questions)}",
                    "skill": skill,
                    "question": q_text,
                    "options": options,
                    "answer": correct,
                    "explanation": explanation,
                    "difficulty": difficulty
                })

        except Exception as e:
            print(f"⚠️ Failed to generate question for {skill}: {e}")
            continue

    if not questions:
        raise HTTPException(status_code=500, detail="No questions generated.")

    # Log assessment generation
    activity_tracker.log_activity(payload.user_id, "assessment_generated", {
        "skills": payload.skills,
        "question_count": len(questions)
    })

    return {"questions": questions, "user_id": payload.user_id}

@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(payload: AssessmentSubmission):
    """Submit assessment answers and get comprehensive analysis"""
    
    try:
        # Calculate scores (this would need to be enhanced with actual question data)
        # For now, we'll simulate scoring
        skill_scores = {}
        for question_id, answer in payload.answers.items():
            skill = question_id.split("_")[0]
            if skill not in skill_scores:
                skill_scores[skill] = {"correct": 0, "total": 0}
            skill_scores[skill]["total"] += 1
            # Assume correct answer for demo (in real implementation, compare with stored correct answers)
            skill_scores[skill]["correct"] += 1
        
        # Convert to percentage scores
        final_scores = {}
        for skill, score_data in skill_scores.items():
            final_scores[skill] = (score_data["correct"] / score_data["total"]) * 10
        
        # Analyze skills using AI
        skill_analysis = skill_analyzer.analyze_skill_strengths(final_scores)
        
        # Generate learning recommendations
        learning_path = skill_analyzer.generate_personalized_learning_path(skill_analysis)
        
        # Get AI mentor suggestions
        mentor_suggestions = ai_mentor.get_mentor_response(
            payload.user_id,
            f"I just completed an assessment with scores: {final_scores}. What should I focus on next?",
            {
                "recent_assessment_scores": final_scores,
                "weak_skills": skill_analysis["weak_skills"],
                "strong_skills": skill_analysis["strong_skills"]
            }
        )
        
        # Log assessment completion
        activity_tracker.log_assessment_result(payload.user_id, list(final_scores.keys()), final_scores)
        
        return AssessmentResult(
            user_id=payload.user_id,
            skill_scores=final_scores,
            strong_skills=skill_analysis["strong_skills"],
            medium_skills=skill_analysis["medium_skills"],
            weak_skills=skill_analysis["weak_skills"],
            overall_analysis=skill_analysis["ai_analysis"],
            learning_recommendations=learning_path,
            ai_mentor_suggestions=mentor_suggestions.get("suggestions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {e}")

@router.get("/{user_id}/history")
async def get_assessment_history(user_id: str):
    """Get user's assessment history"""
    try:
        user_profile = activity_tracker.get_user_profile(user_id)
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get assessment activities
        assessment_activities = [
            activity for activity in activity_tracker.get_user_activities(user_id, 50)
            if activity["activity_type"] == "assessment_completed"
        ]
        
        return {
            "user_id": user_id,
            "assessment_history": assessment_activities,
            "total_assessments": len(assessment_activities),
            "profile": user_profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {e}")

@router.get("/{user_id}/progress")
async def get_skill_progress(user_id: str):
    """Get skill progress over time"""
    try:
        # Get assessment history for progress tracking
        assessment_activities = [
            activity for activity in activity_tracker.get_user_activities(user_id, 100)
            if activity["activity_type"] == "assessment_completed"
        ]
        
        if len(assessment_activities) < 2:
            return {
                "user_id": user_id,
                "progress": "Insufficient data for progress tracking",
                "assessments_count": len(assessment_activities)
            }
        
        # Get first and latest assessment scores
        first_assessment = assessment_activities[-1]
        latest_assessment = assessment_activities[0]
        
        if "scores" in first_assessment["details"] and "scores" in latest_assessment["details"]:
            progress_data = skill_analyzer.track_skill_progress(
                user_id,
                first_assessment["details"]["scores"],
                latest_assessment["details"]["scores"]
            )
        else:
            progress_data = {"error": "No score data available"}
        
        return {
            "user_id": user_id,
            "progress_data": progress_data,
            "assessments_count": len(assessment_activities)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {e}")
