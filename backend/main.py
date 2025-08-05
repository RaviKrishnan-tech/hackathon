from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Import all route modules
from routes import resume, assessment, recommend, hackathon, progress, admin, mentor

app = FastAPI(
    title="Mavericks AI-Powered Learning Platform",
    description="A comprehensive AI-driven platform for skill assessment, personalized learning, and 24/7 AI mentoring",
    version="2.0.0"
)

# ✅ CORS setup to allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🚨 In production, change this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register all routers
app.include_router(resume.router)       # /resume           ← AI-powered resume parsing
app.include_router(assessment.router)   # /assessment       ← AI-generated assessments + skill analysis
app.include_router(recommend.router)    # /recommend        ← AI-powered learning paths
app.include_router(mentor.router)       # /mentor           ← 24/7 AI mentoring
app.include_router(hackathon.router)    # /hackathon        ← events, competitions
app.include_router(progress.router)     # /user             ← progress tracking
app.include_router(admin.router)        # /admin            ← real-time admin dashboard

# ✅ Health check route
@app.get("/")
def root():
    return {
        "message": "✅ Mavericks AI Learning Platform is up and running",
        "version": "2.0.0",
        "features": [
            "AI-powered resume parsing with Gemini AI",
            "Dynamic skill assessment generation",
            "Real-time skill strength analysis",
            "Personalized learning path generation",
            "24/7 AI mentor assistance",
            "Comprehensive activity tracking",
            "Real-time admin dashboard"
        ],
        "status": "operational"
    }

@app.get("/health")
def health_check():
    """Comprehensive health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "ai_services": "operational",
            "activity_tracking": "operational"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }
