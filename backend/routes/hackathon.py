from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random

router = APIRouter(prefix="/hackathon", tags=["Hackathon"])

class HackSubmit(BaseModel):
    user_id: str
    code: str

@router.post("/submit", response_model=dict)
async def submit_challenge(payload: HackSubmit):
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    passed = random.random() < 0.7
    score = random.randint(60, 100) if passed else random.randint(0, 59)
    feedback = "Great job!" if passed else "Needs improvement."
    return {"status": "passed" if passed else "failed", "score": score, "feedback": feedback}
