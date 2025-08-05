from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/user", tags=["Progress"])

USER_PROGRESS: dict[str, list[dict]] = {}

@router.get("/{user_id}/progress", response_model=dict)
async def get_progress(user_id: str):
    return {
        "user_id": user_id,
        "progress": USER_PROGRESS.get(user_id, [])
    }

def log_event(user_id: str, name: str, details: dict = {}):
    USER_PROGRESS.setdefault(user_id, []).append({
        "name": name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "details": details
    })
