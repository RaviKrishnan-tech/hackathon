import google.generativeai as genai
import os
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class SkillAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        
    def analyze_skill_strengths(self, assessment_scores: Dict[str, float]) -> Dict:
        """
        Analyze assessment scores and categorize skills as strong, weak, or medium
        Returns detailed analysis with recommendations
        """
        
        if not assessment_scores:
            return {
                "strong_skills": [],
                "medium_skills": [],
                "weak_skills": [],
                "overall_analysis": "No assessment data available",
                "recommendations": []
            }
        
        # Categorize skills based on scores
        strong_skills = {skill: score for skill, score in assessment_scores.items() if score >= 8.0}
        weak_skills = {skill: score for skill, score in assessment_scores.items() if score < 6.0}
        medium_skills = {skill: score for skill, score in assessment_scores.items() if 6.0 <= score < 8.0}
        
        # Generate AI-powered analysis
        analysis = self._generate_skill_analysis(strong_skills, medium_skills, weak_skills)
        
        # Calculate overall metrics
        avg_score = np.mean(list(assessment_scores.values()))
        total_skills = len(assessment_scores)
        
        return {
            "strong_skills": list(strong_skills.keys()),
            "medium_skills": list(medium_skills.keys()),
            "weak_skills": list(weak_skills.keys()),
            "score_breakdown": {
                "strong": dict(strong_skills),
                "medium": dict(medium_skills),
                "weak": dict(weak_skills)
            },
            "overall_metrics": {
                "average_score": round(avg_score, 2),
                "total_skills_assessed": total_skills,
                "strong_skills_count": len(strong_skills),
                "medium_skills_count": len(medium_skills),
                "weak_skills_count": len(weak_skills)
            },
            "ai_analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_skill_analysis(self, strong_skills: Dict, medium_skills: Dict, weak_skills: Dict) -> Dict:
        """Generate AI-powered analysis of skill strengths and weaknesses"""
        
        prompt = f"""Analyze the following skill assessment results and provide detailed insights:

Strong Skills (Score >= 8.0): {dict(strong_skills)}
Medium Skills (Score 6.0-7.9): {dict(medium_skills)}
Weak Skills (Score < 6.0): {dict(weak_skills)}

Provide analysis in the following JSON format:
{{
    "strength_analysis": "Detailed analysis of strong skills and how to leverage them",
    "improvement_areas": "Analysis of weak skills and specific improvement strategies",
    "skill_gaps": "Identified gaps in the skill set",
    "career_recommendations": "Career path suggestions based on skill profile",
    "learning_priorities": "Prioritized list of skills to focus on",
    "next_steps": "Specific actionable next steps for skill development"
}}

Focus on practical, actionable insights that can guide learning and career development.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                # Try to parse as JSON directly
                return json.loads(response_text)
                
        except Exception as e:
            return {
                "strength_analysis": f"Error generating analysis: {str(e)}",
                "improvement_areas": "Focus on skills with scores below 6.0",
                "skill_gaps": "Unable to analyze gaps due to processing error",
                "career_recommendations": "Consider retaking assessment for better analysis",
                "learning_priorities": list(weak_skills.keys()),
                "next_steps": "Retake assessment or contact support"
            }
    
    def generate_personalized_learning_path(self, skill_analysis: Dict) -> Dict:
        """Generate personalized learning path based on skill analysis"""
        
        weak_skills = skill_analysis.get("weak_skills", [])
        medium_skills = skill_analysis.get("medium_skills", [])
        
        prompt = f"""Based on the skill analysis, generate a personalized learning path:

Weak Skills to Improve: {weak_skills}
Medium Skills to Strengthen: {medium_skills}

Create a structured learning path with:
1. Priority order for learning
2. Estimated time commitment for each skill
3. Specific learning objectives
4. Recommended resources and courses
5. Practice exercises and projects
6. Milestones and checkpoints

Format as JSON:
{{
    "learning_path": [
        {{
            "skill": "skill_name",
            "priority": "high/medium/low",
            "estimated_weeks": 4,
            "learning_objectives": ["objective1", "objective2"],
            "resources": ["resource1", "resource2"],
            "exercises": ["exercise1", "exercise2"],
            "milestones": ["milestone1", "milestone2"]
        }}
    ],
    "total_estimated_weeks": 12,
    "focus_areas": ["area1", "area2"],
    "success_metrics": ["metric1", "metric2"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return json.loads(response_text)
                
        except Exception as e:
            return {
                "learning_path": [],
                "total_estimated_weeks": 0,
                "focus_areas": weak_skills,
                "success_metrics": ["Complete all weak skill assessments with score >= 7.0"],
                "error": str(e)
            }
    
    def track_skill_progress(self, user_id: str, initial_scores: Dict, current_scores: Dict) -> Dict:
        """Track progress between assessments"""
        
        if not initial_scores or not current_scores:
            return {"error": "Insufficient data for progress tracking"}
        
        progress_data = {}
        total_improvement = 0
        improved_skills = []
        declined_skills = []
        
        for skill in set(initial_scores.keys()) | set(current_scores.keys()):
            initial_score = initial_scores.get(skill, 0)
            current_score = current_scores.get(skill, 0)
            improvement = current_score - initial_score
            
            progress_data[skill] = {
                "initial_score": initial_score,
                "current_score": current_score,
                "improvement": improvement,
                "improvement_percentage": round((improvement / max(initial_score, 1)) * 100, 2)
            }
            
            total_improvement += improvement
            
            if improvement > 0:
                improved_skills.append(skill)
            elif improvement < 0:
                declined_skills.append(skill)
        
        avg_improvement = total_improvement / len(progress_data) if progress_data else 0
        
        return {
            "user_id": user_id,
            "progress_data": progress_data,
            "summary": {
                "total_skills_tracked": len(progress_data),
                "average_improvement": round(avg_improvement, 2),
                "improved_skills_count": len(improved_skills),
                "declined_skills_count": len(declined_skills),
                "improved_skills": improved_skills,
                "declined_skills": declined_skills
            },
            "timestamp": datetime.utcnow().isoformat()
        }

# Global analyzer instance
skill_analyzer = SkillAnalyzer() 