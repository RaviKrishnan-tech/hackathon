import google.generativeai as genai
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from PyPDF2 import PdfReader
import re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class EnhancedResumeParser:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        
    def parse_resume(self, file_obj) -> Dict:
        """Enhanced resume parsing using Gemini AI"""
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(file_obj)
        
        # Use Gemini AI to analyze the resume
        analysis = self._analyze_resume_with_ai(text)
        
        return {
            "extracted_skills": analysis.get("skills", []),
            "experience_level": analysis.get("experience_level", "entry"),
            "years_of_experience": analysis.get("years_of_experience", 0),
            "education": analysis.get("education", []),
            "projects": analysis.get("projects", []),
            "certifications": analysis.get("certifications", []),
            "skill_categories": analysis.get("skill_categories", {}),
            "career_summary": analysis.get("career_summary", ""),
            "recommended_learning_path": analysis.get("recommended_learning_path", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_text_from_pdf(self, file_obj) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_obj)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _analyze_resume_with_ai(self, resume_text: str) -> Dict:
        """Use Gemini AI to analyze resume content"""
        
        prompt = f"""Analyze the following resume and extract comprehensive information:

Resume Text:
{resume_text[:4000]}  # Limit text to avoid token limits

Please provide analysis in the following JSON format:
{{
    "skills": ["skill1", "skill2", "skill3"],
    "experience_level": "entry/mid/senior",
    "years_of_experience": 3,
    "education": [
        {{
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "institution": "University Name",
            "year": 2020
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"],
            "impact": "What was accomplished"
        }}
    ],
    "certifications": ["cert1", "cert2"],
    "skill_categories": {{
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Django"],
        "databases": ["PostgreSQL", "MongoDB"],
        "tools": ["Git", "Docker"],
        "soft_skills": ["Leadership", "Communication"]
    }},
    "career_summary": "Brief summary of career background and goals",
    "recommended_learning_path": [
        {{
            "skill": "skill_name",
            "priority": "high/medium/low",
            "reason": "Why this skill is recommended"
        }}
    ]
}}

Focus on:
1. Technical skills (programming languages, frameworks, tools)
2. Experience level and years of experience
3. Education and certifications
4. Notable projects and their impact
5. Skill categorization for better learning recommendations
6. Career summary and learning path suggestions

Be thorough but accurate. If information is not available, use empty arrays or appropriate defaults.
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
            # Fallback to basic skill extraction
            return self._fallback_skill_extraction(resume_text)
    
    def _fallback_skill_extraction(self, text: str) -> Dict:
        """Fallback method for skill extraction if AI fails"""
        
        # Common technical skills
        known_skills = {
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "express", "django", "flask", "spring", "sql", "mongodb",
            "postgresql", "mysql", "redis", "docker", "kubernetes", "aws", "azure",
            "git", "github", "jenkins", "ci/cd", "agile", "scrum", "html", "css",
            "bootstrap", "tailwind", "jquery", "ajax", "rest", "graphql", "api",
            "microservices", "serverless", "machine learning", "ai", "data science",
            "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "nlp",
            "computer vision", "blockchain", "ethereum", "solidity"
        }
        
        # Extract skills from text
        text_lower = text.lower()
        found_skills = []
        
        for skill in known_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return {
            "skills": found_skills,
            "experience_level": "entry",
            "years_of_experience": 0,
            "education": [],
            "projects": [],
            "certifications": [],
            "skill_categories": {
                "programming_languages": [s for s in found_skills if s in ["python", "java", "javascript", "typescript"]],
                "frameworks": [s for s in found_skills if s in ["react", "angular", "vue", "django", "flask", "spring"]],
                "databases": [s for s in found_skills if s in ["sql", "mongodb", "postgresql", "mysql", "redis"]],
                "tools": [s for s in found_skills if s in ["git", "docker", "aws", "jenkins"]]
            },
            "career_summary": "Resume analysis completed with basic skill extraction",
            "recommended_learning_path": []
        }
    
    def generate_skill_assessment_plan(self, extracted_skills: List[str], experience_level: str) -> Dict:
        """Generate assessment plan based on extracted skills"""
        
        prompt = f"""Based on the following skills and experience level, generate an assessment plan:

Skills: {extracted_skills}
Experience Level: {experience_level}

Create an assessment plan in JSON format:
{{
    "assessment_plan": [
        {{
            "skill": "skill_name",
            "difficulty": "beginner/intermediate/advanced",
            "question_count": 5,
            "focus_areas": ["area1", "area2"],
            "estimated_duration": "15 minutes"
        }}
    ],
    "total_questions": 25,
    "estimated_total_duration": "75 minutes",
    "skill_priorities": ["priority1", "priority2"],
    "assessment_strategy": "Strategy description"
}}

Consider the experience level when determining question difficulty and focus areas.
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
                "assessment_plan": [
                    {
                        "skill": skill,
                        "difficulty": "intermediate",
                        "question_count": 3,
                        "focus_areas": ["fundamentals", "practical application"],
                        "estimated_duration": "10 minutes"
                    } for skill in extracted_skills[:5]
                ],
                "total_questions": len(extracted_skills) * 3,
                "estimated_total_duration": f"{len(extracted_skills) * 10} minutes",
                "skill_priorities": extracted_skills[:3],
                "assessment_strategy": "Comprehensive skill assessment with practical questions"
            }

# Global parser instance
resume_parser = EnhancedResumeParser() 